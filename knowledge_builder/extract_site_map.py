import json
import time
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup


# =========================================================
# CONFIGURATION
# =========================================================

START_URLS = [
    "https://dicd.tuiasi.ro/ro/studenti/",
    "https://dicd.tuiasi.ro/ro/angajati/",
    "https://dicd.tuiasi.ro/ro/vizitatori/",
    "https://dicd.tuiasi.ro/ro/selecteaza-campus/",
]

ALLOWED_HOST = "dicd.tuiasi.ro"
ALLOWED_PREFIX = "https://dicd.tuiasi.ro/ro/"

OUTPUT_FILE = "../data/site_map.json"

REQUEST_DELAY = 0.5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; DICD-Site-Mapper/1.0)"
    )
}

session = requests.Session()
session.headers.update(HEADERS)


# =========================================================
# URL HELPERS
# =========================================================

def normalize_url(url):
    """
    Normalize a URL.

    Examples:

        /ro/studenti
        /ro/studenti/
        /ro/studenti/#something

    all become:

        https://dicd.tuiasi.ro/ro/studenti/
    """

    if not url:
        return None

    # Remove #fragment
    url = urldefrag(url)[0]

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return None

    if parsed.netloc != ALLOWED_HOST:
        return None

    if not parsed.path.startswith("/ro/"):
        return None

    path = parsed.path

    if not path.endswith("/"):
        path += "/"

    return f"https://{ALLOWED_HOST}{path}"


def is_allowed_url(url):
    """
    Only allow pages from:

        https://dicd.tuiasi.ro/ro/
    """

    if not url:
        return False

    return (
        url.startswith(ALLOWED_PREFIX)
        and urlparse(url).netloc == ALLOWED_HOST
    )


# =========================================================
# FETCH
# =========================================================

def fetch_page(url):

    print(f"Fetching: {url}")

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


# =========================================================
# TITLE
# =========================================================

def extract_title(soup):

    # Prefer H1.
    h1 = soup.find("h1")

    if h1:

        title = h1.get_text(
            " ",
            strip=True
        )

        if title:
            return " ".join(title.split())

    # Fallback to <title>.
    if soup.title:

        title = soup.title.get_text(
            " ",
            strip=True
        )

        return " ".join(title.split())

    return ""


# =========================================================
# CHILDREN
# =========================================================

def extract_children(soup, current_url):

    """
    All non-homepage pages use the same card structure:

        .advgb-column-inner > a

    We only look inside #main, so:

        header navigation -> ignored
        footer            -> ignored
        menus             -> ignored
        cards             -> included
    """

    main = soup.select_one("#main")

    if not main:
        print("  [WARNING] #main not found")
        return []

    links = main.select(
        ".advgb-column-inner > a"
    )

    children = []
    seen = set()

    for link in links:

        href = link.get("href")

        if not href:
            continue

        # Convert relative URL to absolute.
        absolute_url = urljoin(
            current_url,
            href
        )

        # Normalize.
        child_url = normalize_url(
            absolute_url
        )

        # Only DICD /ro/ pages.
        if not is_allowed_url(child_url):

            print(
                f"    [IGNORED] {href}"
            )

            continue

        # Don't add current page.
        if child_url == current_url:
            continue

        # Don't duplicate links on the same page.
        if child_url in seen:
            continue

        seen.add(child_url)

        # Extract card title.
        title = link.get_text(
            " ",
            strip=True
        )

        title = " ".join(
            title.split()
        )

        if not title:
            continue

        children.append({
            "url": child_url,
            "title": title
        })

    return children


# =========================================================
# CRAWL ONE TREE
# =========================================================

def crawl_tree(start_url):

    print()
    print("=" * 70)
    print(f"STARTING TREE: {start_url}")
    print("=" * 70)

    queue = deque([start_url])

    visited = set()

    pages = {}

    while queue:

        url = queue.popleft()

        if url in visited:
            continue

        visited.add(url)

        print()
        print(
            f"[{len(visited)}] {url}"
        )

        html = fetch_page(url)

        if not html:
            continue

        soup = BeautifulSoup(
            html,
            "lxml"
        )

        title = extract_title(
            soup
        )

        children = extract_children(
            soup,
            url
        )

        pages[url] = {
            "url": url,
            "title": title,
            "children": children
        }

        print(
            f"  Title: {title}"
        )

        print(
            f"  Children: {len(children)}"
        )

        for child in children:

            child_url = child["url"]

            print(
                f"    -> {child['title']}"
            )

            print(
                f"       {child_url}"
            )

            if (
                child_url not in visited
                and child_url not in queue
            ):
                queue.append(
                    child_url
                )

        time.sleep(
            REQUEST_DELAY
        )

    return pages


# =========================================================
# BUILD TREE
# =========================================================

def build_tree(url, pages, ancestors=None):

    if ancestors is None:
        ancestors = set()

    page = pages.get(url)

    if not page:
        return None

    # Prevent infinite loops if the site contains
    # a circular link.
    if url in ancestors:

        return {
            "url": page["url"],
            "title": page["title"],
            "children": []
        }

    new_ancestors = set(ancestors)

    new_ancestors.add(url)

    children = []

    for child in page["children"]:

        child_node = build_tree(
            child["url"],
            pages,
            new_ancestors
        )

        if child_node:
            children.append(
                child_node
            )

    return {
        "url": page["url"],
        "title": page["title"],
        "children": children
    }


# =========================================================
# MAIN
# =========================================================

def main():

    all_pages = {}

    # Crawl all three roots.
    for start_url in START_URLS:

        normalized = normalize_url(
            start_url
        )

        if not normalized:
            print(
                f"Invalid start URL: {start_url}"
            )
            continue

        pages = crawl_tree(
            normalized
        )

        # Merge into global page collection.
        all_pages.update(
            pages
        )

    # -----------------------------------------------------
    # Build the three trees.
    # -----------------------------------------------------

    site_map = []

    for start_url in START_URLS:

        normalized = normalize_url(
            start_url
        )

        tree = build_tree(
            normalized,
            all_pages
        )

        if tree:
            site_map.append(
                tree
            )

    # -----------------------------------------------------
    # Save JSON.
    # -----------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            site_map,
            file,
            ensure_ascii=False,
            indent=2
        )

    # -----------------------------------------------------
    # Summary.
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("CRAWL COMPLETE")
    print("=" * 70)

    print(
        f"Total unique pages: {len(all_pages)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()