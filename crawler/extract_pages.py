import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


# ============================================================
# CONFIG
# ============================================================

SITE_MAP_FILE = Path("../data/site_map.json")
OUTPUT_DIR = Path("../data/pages")

REQUEST_DELAY = 0.5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; DICD-Content-Extractor/1.0)"
    )
}


# ============================================================
# HTTP SESSION
# ============================================================

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# URL -> FILENAME
# ============================================================

def url_to_filename(url: str) -> str:
    """
    Convert a DICD URL into a safe Markdown filename.

    Examples:

        https://dicd.tuiasi.ro/ro/studenti/
            -> studenti.md

        https://dicd.tuiasi.ro/ro/studenti/autocad/
            -> studenti__autocad.md
    """

    parsed = urlparse(url)

    path = parsed.path.strip("/")

    # Remove "ro/" from the beginning.
    if path.startswith("ro/"):
        path = path[3:]

    # Convert path separators into a readable filename.
    filename = path.replace("/", "__")

    # Remove characters that are problematic in filenames.
    filename = re.sub(
        r"[^a-zA-Z0-9ăâîșțĂÂÎȘȚ._-]+",
        "-",
        filename
    )

    if not filename:
        filename = "index"

    return f"{filename}.md"


# ============================================================
# LOAD SITE MAP
# ============================================================

def load_site_map():
    print(f"Loading site map: {SITE_MAP_FILE}")

    with open(
        SITE_MAP_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# ============================================================
# TRAVERSE SITE MAP
# ============================================================

def collect_pages(nodes):
    """
    Recursively collect every page from the sitemap.

    The sitemap can contain either:

        [...]
    or a single:

        {...}

    root.
    """

    pages = []
    seen = set()

    def visit(node):

        if not isinstance(node, dict):
            return

        url = node.get("url")

        if url and url not in seen:

            seen.add(url)

            pages.append({
                "url": url,
                "title": node.get("title", "")
            })

        for child in node.get("children", []):
            visit(child)

    if isinstance(nodes, list):

        for node in nodes:
            visit(node)

    else:
        visit(nodes)

    return pages


# ============================================================
# FETCH PAGE
# ============================================================

def fetch_page(url):

    print(f"  Fetching: {url}")

    try:

        response = session.get(
            url,
            timeout=20
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "text/html" not in content_type:

            print(
                f"  [SKIP] Not HTML: {content_type}"
            )

            return None

        return response.text

    except requests.RequestException as e:

        print(
            f"  [ERROR] {e}"
        )

        return None


# ============================================================
# IMAGE HELPERS
# ============================================================

def get_image_url(image, page_url):
    """
    Resolve an image URL to an absolute URL.

    Supports normal src and common lazy-loading attributes.
    """

    # Check several common WordPress/lazy-loading attributes.
    candidates = [
        image.get("src"),
        image.get("data-src"),
        image.get("data-lazy-src"),
        image.get("data-original"),
    ]

    src = ""

    for candidate in candidates:

        if candidate and candidate.strip():
            src = candidate.strip()
            break

    if not src:
        return None

    # Ignore inline/base64 images.
    if src.startswith("data:"):
        return None

    return urljoin(
        page_url,
        src
    )


def get_image_caption(image):
    """
    Find useful text describing an image.

    Priority:

        1. <figcaption>
        2. alt
        3. title

    Returns an empty string if none exists.
    """

    # --------------------------------------------------------
    # Figure caption
    # --------------------------------------------------------

    figure = image.find_parent("figure")

    if figure:

        caption = figure.find("figcaption")

        if caption:

            text = caption.get_text(
                " ",
                strip=True
            )

            if text:
                return text

    # --------------------------------------------------------
    # Alt text
    # --------------------------------------------------------

    alt = (
        image.get("alt")
        or ""
    ).strip()

    if alt:
        return alt

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    title = (
        image.get("title")
        or ""
    ).strip()

    return title


def is_probably_decorative_image(image):
    """
    Try to identify images that are probably decorative UI
    elements rather than useful page content.

    We intentionally err on the side of KEEPING images.

    Screenshots and instructional images should therefore
    normally survive this filter.
    """

    src = (
        image.get("src")
        or image.get("data-src")
        or image.get("data-lazy-src")
        or image.get("data-original")
        or ""
    ).lower()

    alt = (
        image.get("alt")
        or ""
    ).strip().lower()

    classes = " ".join(
        image.get("class", [])
    ).lower()

    # --------------------------------------------------------
    # Common decorative/icon indicators.
    # --------------------------------------------------------

    decorative_keywords = [
        "icon",
        "logo",
        "social",
        "facebook",
        "twitter",
        "instagram",
        "linkedin",
        "youtube",
        "arrow",
        "chevron",
        "menu",
        "search",
        "close",
        "loading",
        "avatar",
    ]

    for keyword in decorative_keywords:

        if keyword in src:
            return True

        if keyword in classes:
            return True

    # --------------------------------------------------------
    # Very small images are usually icons.
    # --------------------------------------------------------

    try:

        width = int(
            image.get("width", 0)
        )

        height = int(
            image.get("height", 0)
        )

        if (
            width
            and height
            and width <= 64
            and height <= 64
        ):
            return True

    except (TypeError, ValueError):
        pass

    # Empty alt text alone is NOT enough to discard an image.
    #
    # Screenshots often have no alt text.
    #
    # Therefore we keep the image unless there is stronger
    # evidence that it is decorative.

    return False


# ============================================================
# PREPARE IMAGES FOR MARKDOWN
# ============================================================

def prepare_images(content, page_url):
    """
    Prepare useful images for Markdown conversion.

    Important:

    Images are NOT extracted into a separate metadata list.

    Instead, they remain in the exact position in which they
    appeared on the original page.

    Example:

        Text

        <img>

        More text

    becomes:

        Text

        ![caption](https://...)

        More text
    """

    for image in content.find_all("img"):

        # ----------------------------------------------------
        # Decorative image
        # ----------------------------------------------------

        if is_probably_decorative_image(image):

            # Remove only the image.
            #
            # If it happens to be inside a link, the link's
            # text remains.
            image.decompose()

            continue

        # ----------------------------------------------------
        # Resolve image URL
        # ----------------------------------------------------

        image_url = get_image_url(
            image,
            page_url
        )

        if not image_url:

            image.decompose()

            continue

        # ----------------------------------------------------
        # Image inside a link
        # ----------------------------------------------------

        parent_link = image.find_parent("a")

        if parent_link:

            # These are usually navigation buttons or linked
            # thumbnails.
            #
            # Remove the image but preserve the surrounding
            # link/text.
            image.decompose()

            continue

        # ----------------------------------------------------
        # Useful content image
        # ----------------------------------------------------

        image["src"] = image_url

        caption = get_image_caption(
            image
        )

        if caption:

            image["alt"] = caption

        else:

            image["alt"] = ""

        # ----------------------------------------------------
        # Remove lazy-loading attributes.
        # ----------------------------------------------------

        for attr in [
            "data-src",
            "data-lazy-src",
            "data-original",
            "srcset",
            "data-srcset",
            "loading",
            "decoding",
        ]:

            if image.has_attr(attr):
                del image[attr]


# ============================================================
# EXTRACT MAIN CONTENT
# ============================================================

def extract_content(html, url):
    """
    Extract only the actual page content.

    We intentionally ignore:

        header
        navigation
        footer
        sidebar
        search
        menus

    and only use:

        #main .entry-content

    Useful images remain inline in their original position.
    """

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    # --------------------------------------------------------
    # Find the main article content.
    # --------------------------------------------------------

    content = soup.select_one(
        "#main .entry-content"
    )

    if not content:

        print(
            "  [WARNING] Could not find "
            "#main .entry-content"
        )

        return None

    # --------------------------------------------------------
    # Remove elements that aren't useful knowledge.
    # --------------------------------------------------------

    unwanted_selectors = [
        "script",
        "style",
        "noscript",
        "iframe",

        # Forms/search widgets
        "form",

        # WordPress/admin-ish elements
        ".screen-reader-text",

        # Social/share widgets
        ".sharedaddy",
        ".wp-block-social-links",

        # Comments
        "#comments",
        ".comments-area",
    ]

    for selector in unwanted_selectors:

        for element in content.select(selector):
            element.decompose()

    # --------------------------------------------------------
    # Prepare images BEFORE converting HTML to Markdown.
    #
    # This preserves their location in the document.
    # --------------------------------------------------------

    prepare_images(
        content,
        url
    )

    # --------------------------------------------------------
    # Remove empty div/span elements.
    #
    # IMPORTANT:
    # Do this AFTER image preparation so that a container
    # containing a useful image isn't accidentally removed.
    # --------------------------------------------------------

    for element in content.find_all():

        if element.name in {
            "div",
            "span"
        }:

            text = element.get_text(
                " ",
                strip=True
            )

            if not text and not element.find("img"):

                element.decompose()

    # --------------------------------------------------------
    # Convert HTML -> Markdown.
    # --------------------------------------------------------

    markdown = md(
        str(content),

        heading_style="ATX",

        bullets="-",

        strip=[
            "script",
            "style"
        ]
    )

    # --------------------------------------------------------
    # Clean whitespace.
    # --------------------------------------------------------

    markdown = clean_markdown(
        markdown
    )

    return markdown


# ============================================================
# CLEAN MARKDOWN
# ============================================================

def clean_markdown(text):
    """
    Normalize Markdown without destroying its structure.
    """

    # --------------------------------------------------------
    # Normalize line endings.
    # --------------------------------------------------------

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    # --------------------------------------------------------
    # Remove trailing spaces.
    # --------------------------------------------------------

    text = "\n".join(
        line.rstrip()
        for line in text.splitlines()
    )

    # --------------------------------------------------------
    # Collapse 3+ blank lines to 2.
    # --------------------------------------------------------

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    # --------------------------------------------------------
    # Remove empty Markdown links.
    #
    # Examples:
    #
    #   []()
    #   [ ](https://...)
    #
    # But DON'T touch image syntax:
    #
    #   ![caption](image.jpg)
    # --------------------------------------------------------

    text = re.sub(
        r"(?<!\!)\[\s*\]\([^)]*\)",
        "",
        text
    )

    return text.strip()


# ============================================================
# YAML HELPERS
# ============================================================

def yaml_quote(value):
    """
    Safely quote a string for our simple YAML front matter.
    """

    value = str(value)

    value = value.replace(
        "\\",
        "\\\\"
    )

    value = value.replace(
        '"',
        '\\"'
    )

    value = value.replace(
        "\n",
        " "
    )

    return f'"{value}"'


# ============================================================
# BUILD MARKDOWN DOCUMENT
# ============================================================

def build_document(
    title,
    url,
    content
):
    """
    Build the final Markdown document.

    Only basic page metadata is stored in front matter.

    Images are deliberately NOT listed here.

    They remain inline in the actual Markdown content.
    """

    return f"""---
title: {yaml_quote(title)}
url: {yaml_quote(url)}
---

# {title}

{content}
"""


# ============================================================
# SAVE PAGE
# ============================================================

def save_page(
    url,
    title,
    content
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = url_to_filename(
        url
    )

    output_file = OUTPUT_DIR / filename

    document = build_document(
        title=title,
        url=url,
        content=content
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(document)

    return output_file


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("DICD PAGE CONTENT EXTRACTOR")
    print("=" * 70)

    # --------------------------------------------------------
    # Load sitemap.
    # --------------------------------------------------------

    site_map = load_site_map()

    pages = collect_pages(
        site_map
    )

    print(
        f"Pages found in sitemap: {len(pages)}"
    )

    print()

    # --------------------------------------------------------
    # Create output directory.
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Extract every page.
    # --------------------------------------------------------

    successful = 0
    failed = 0

    for index, page in enumerate(
        pages,
        start=1
    ):

        url = page["url"]
        title = page["title"]

        print(
            f"[{index}/{len(pages)}] {title}"
        )

        print(
            f"  URL: {url}"
        )

        # ----------------------------------------------------
        # Fetch
        # ----------------------------------------------------

        html = fetch_page(
            url
        )

        if not html:

            failed += 1

            time.sleep(
                REQUEST_DELAY
            )

            continue

        # ----------------------------------------------------
        # Extract
        # ----------------------------------------------------

        content = extract_content(
            html,
            url
        )

        if not content:

            failed += 1

            print(
                "  [FAILED] No content extracted"
            )

            time.sleep(
                REQUEST_DELAY
            )

            continue

        # ----------------------------------------------------
        # Save
        # ----------------------------------------------------

        output_file = save_page(
            url=url,
            title=title,
            content=content
        )

        successful += 1

        print(
            f"  [OK] {output_file}"
        )

        time.sleep(
            REQUEST_DELAY
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)

    print(
        f"Pages in sitemap: {len(pages)}"
    )

    print(
        f"Successfully extracted: {successful}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()