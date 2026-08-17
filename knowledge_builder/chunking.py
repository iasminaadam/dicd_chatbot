import json
import re
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

PAGES_DIR = Path("../data/pages")
OUTPUT_FILE = Path("../data/chunks.json")


# ============================================================
# MARKDOWN PARSING
# ============================================================

HEADING_RE = re.compile(
    r"^(#{1,6})[ \t]+(.+?)\s*$"
)


# ============================================================
# DATA STRUCTURES
# ============================================================

class Section:
    """
    Represents one Markdown heading and everything belonging
    to that heading until the next heading of the same or
    higher level.

    Example:

        ## Section

        Text belonging to section.

        ### Subsection

        Text belonging to subsection.

    becomes:

        Section
        └── Subsection
    """

    def __init__(
        self,
        level,
        title
    ):
        self.level = level
        self.title = title

        # Text directly belonging to this section.
        #
        # Child sections are NOT stored here.
        self.lines = []

        # Nested sections.
        self.children = []


# ============================================================
# FRONT MATTER
# ============================================================

def parse_front_matter(text):
    """
    Extract the simple YAML-like front matter.

    Expected:

        ---
        title: "Acces la căsuța poștală"
        url: "https://..."
        ---

    Returns:

        {
            "title": "...",
            "url": "..."
        }
    """

    metadata = {}

    if not text.startswith("---"):
        return metadata

    lines = text.splitlines()

    if not lines:
        return metadata

    if lines[0].strip() != "---":
        return metadata

    end_index = None

    for index in range(1, len(lines)):

        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        return metadata

    for line in lines[1:end_index]:

        match = re.match(
            r"^([A-Za-z0-9_-]+):\s*(.*)$",
            line
        )

        if not match:
            continue

        key = match.group(1)
        value = match.group(2).strip()

        # Remove surrounding double quotes.
        if (
            len(value) >= 2
            and value[0] == '"'
            and value[-1] == '"'
        ):
            value = value[1:-1]

        metadata[key] = value

    return metadata


def remove_front_matter(text):
    """
    Remove YAML front matter from the Markdown document.
    """

    if not text.startswith("---"):
        return text

    lines = text.splitlines()

    if not lines:
        return text

    if lines[0].strip() != "---":
        return text

    for index in range(1, len(lines)):

        if lines[index].strip() == "---":

            return "\n".join(
                lines[index + 1:]
            )

    return text


# ============================================================
# MARKDOWN TREE
# ============================================================

def clean_heading_title(title):
    """
    Clean a Markdown heading title.

    Removes optional Markdown anchor syntax:

        ## Title {#some-anchor}

    ->

        Title
    """

    title = title.strip()

    title = re.sub(
        r"\s+\{#.*?\}\s*$",
        "",
        title
    ).strip()

    return title


def parse_markdown_tree(markdown):
    """
    Convert Markdown headings into a nested section tree.

    The # page title is ignored because the page title comes
    from front matter.

    IMPORTANT:

    Text appearing before the first real section is stored
    directly on the root node.

    Example:

        # Page title

        Introductory text.

        ## Section A

        Text A.

        ### Subsection A1

        Text A1.

    becomes:

        ROOT
        ├── lines: "Introductory text."
        │
        └── Section A
            └── Subsection A1
    """

    root = Section(
        level=0,
        title=""
    )

    # The stack represents the current heading path.
    #
    # root is always present.
    stack = [root]

    lines = markdown.splitlines()

    for line in lines:

        heading_match = HEADING_RE.match(line)

        if heading_match:

            level = len(
                heading_match.group(1)
            )

            title = clean_heading_title(
                heading_match.group(2)
            )

            # ------------------------------------------------
            # The # heading is the page title.
            #
            # We already get this from front matter, so it
            # should NOT become a section.
            #
            # However, we should also make sure that text
            # following # Title belongs to the root until
            # the first ## section.
            # ------------------------------------------------

            if level == 1:

                # If this is the page title, don't create a
                # section.
                #
                # We also reset the stack to root so that any
                # following text belongs to the page itself.
                stack = [root]

                continue

            # ------------------------------------------------
            # Find the correct parent.
            #
            # Example:
            #
            # ## A
            # ### B
            # ### C
            # ## D
            #
            # C is a child of A.
            # D is a child of root.
            # ------------------------------------------------

            while (
                len(stack) > 1
                and stack[-1].level >= level
            ):
                stack.pop()

            section = Section(
                level=level,
                title=title
            )

            parent = stack[-1]

            parent.children.append(
                section
            )

            stack.append(
                section
            )

            continue

        # ----------------------------------------------------
        # Normal content line.
        #
        # It belongs to the currently active section.
        #
        # If there is no active section, it belongs to the
        # page itself (root).
        # ----------------------------------------------------

        stack[-1].lines.append(
            line
        )

    return root


# ============================================================
# TEXT CLEANING
# ============================================================

def mute_images(text):
    """
    Replace Markdown images with <image>.

    Example:

        ![Fig. 1](https://example.com/image.png)

    becomes:

        <image>

    This is useful for retrieval because the actual image URL
    is not useful semantic information.
    """

    # Standard Markdown images.
    text = re.sub(
        r"!\[[^\]]*\]\([^)]*\)",
        "<image>",
        text
    )

    # Reference-style Markdown images.
    #
    # ![caption][image-id]
    text = re.sub(
        r"!\[[^\]]*\]\[[^\]]*\]",
        "<image>",
        text
    )

    return text


def mute_links(text):
    """
    Replace links with <link>.

    Examples:

        [Gmail](https://mail.google.com)

    becomes:

        <link>

    and:

        <https://example.com>

    becomes:

        <link>

    Bare URLs are also replaced.

    IMPORTANT:

    This only modifies the retrieval representation.

    The original Markdown files remain untouched, so the
    actual links can still be used when generating answers.
    """

    # --------------------------------------------------------
    # Markdown links.
    #
    # [text](url)
    # [text](url "title")
    # --------------------------------------------------------

    text = re.sub(
        r"\[[^\]]+\]\(\s*[^)\s]+(?:\s+[^)]*)?\)",
        "<link>",
        text
    )

    # --------------------------------------------------------
    # Reference-style links.
    #
    # [text][id]
    # --------------------------------------------------------

    text = re.sub(
        r"\[[^\]]+\]\[[^\]]*\]",
        "<link>",
        text
    )

    # --------------------------------------------------------
    # Autolinks.
    #
    # <https://example.com>
    # --------------------------------------------------------

    text = re.sub(
        r"<https?://[^>]+>",
        "<link>",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Bare URLs.
    #
    # Example:
    #
    # https://example.com
    # --------------------------------------------------------

    text = re.sub(
        r"(?<![<\w])https?://[^\s)>]+",
        "<link>",
        text,
        flags=re.IGNORECASE
    )

    return text


def clean_markdown_for_retrieval(text):
    """
    Prepare text for embedding/retrieval.

    We keep useful textual structure but remove things that
    should not influence retrieval:

        - URLs
        - image URLs
        - actual Markdown images
        - HTML comments

    Links become:

        <link>

    Images become:

        <image>
    """

    # --------------------------------------------------------
    # Images FIRST.
    #
    # This must happen before links because Markdown images
    # start with ![...].
    # --------------------------------------------------------

    text = mute_images(text)

    # --------------------------------------------------------
    # Links.
    # --------------------------------------------------------

    text = mute_links(text)

    # --------------------------------------------------------
    # Remove HTML comments.
    # --------------------------------------------------------

    text = re.sub(
        r"<!--.*?-->",
        "",
        text,
        flags=re.DOTALL
    )

    # --------------------------------------------------------
    # Normalize whitespace.
    # --------------------------------------------------------

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    text = "\n".join(lines)

    # --------------------------------------------------------
    # Collapse excessive blank lines.
    # --------------------------------------------------------

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# SECTION TEXT
# ============================================================

def get_own_section_text(section):
    """
    Return ONLY the text directly belonging to this section.

    Child section content is intentionally excluded.

    Example:

        ## Parent

        Parent text.

        ### Child

        Child text.

    Parent returns:

        Parent text.

    Child returns:

        Child text.
    """

    if not section.lines:
        return ""

    text = "\n".join(
        section.lines
    )

    return clean_markdown_for_retrieval(
        text
    )


# ============================================================
# PATH
# ============================================================

def build_section_path(
    page_title,
    ancestor_titles,
    current_title
):
    """
    Build the full hierarchy path.

    Example:

        [
            "Acces la căsuța poștală",
            "Trimiterea e-mailurilor în numele altei adrese de e-mail.",
            "Configurarea adresei de e-mail"
        ]
    """

    return [
        page_title,
        *ancestor_titles,
        current_title
    ]


def build_page_chunk_path(
    page_title
):
    """
    Path for text that belongs directly to the page before
    any section begins.

    Example:

        ["Acces la căsuța poștală"]
    """

    return [
        page_title
    ]


# ============================================================
# CHUNK TEXT
# ============================================================

def build_chunk_text(
    section_path,
    section_text
):
    """
    Prefix retrieval text with its hierarchical path.

    Example:

        Acces la căsuța poștală >
        Trimiterea e-mailurilor... >
        Configurarea adresei de e-mail

        Configurarea se realizează o singură dată...
    """

    path_text = " > ".join(
        section_path
    )

    if section_text:

        return (
            f"{path_text}\n\n"
            f"{section_text}"
        )

    return path_text


# ============================================================
# CHUNK CREATION
# ============================================================

def create_chunks_recursive(
    section,
    page_title,
    page_url,
    ancestor_titles,
    page_chunks
):
    """
    Recursively create retrieval chunks from the section tree.

    Rules:

    1. Leaf/final subsection:
       -> one chunk containing all of its own text.

    2. Section with own text + children:
       -> own text becomes one chunk.
       -> children are processed recursively.

    3. Section with children but no own text:
       -> no chunk for the parent.
       -> children are processed recursively.

    Therefore:

        ## Parent
        Parent text.

        ### Child A
        Child A text.

        ### Child B
        Child B text.

    produces:

        chunk -> Parent text
        chunk -> Child A text
        chunk -> Child B text
    """

    # --------------------------------------------------------
    # Build the path for this section.
    # --------------------------------------------------------

    section_path = build_section_path(
        page_title=page_title,
        ancestor_titles=ancestor_titles,
        current_title=section.title
    )

    # --------------------------------------------------------
    # Get text directly belonging to this section.
    # --------------------------------------------------------

    own_text = get_own_section_text(
        section
    )

    # --------------------------------------------------------
    # CASE 1:
    #
    # Leaf section.
    #
    # Everything in this subsection belongs together.
    # --------------------------------------------------------

    if not section.children:

        if own_text:

            page_chunks.append({
                "page_title": page_title,
                "page_link": page_url,
                "section_path": section_path,
                "text": build_chunk_text(
                    section_path,
                    own_text
                )
            })

        return

    # --------------------------------------------------------
    # CASE 2:
    #
    # Section has both its own text and children.
    #
    # Its own text gets its own chunk.
    # --------------------------------------------------------

    if own_text:

        page_chunks.append({
            "page_title": page_title,
            "page_link": page_url,
            "section_path": section_path,
            "text": build_chunk_text(
                section_path,
                own_text
            )
        })

    # --------------------------------------------------------
    # Process children recursively.
    # --------------------------------------------------------

    for child in section.children:

        create_chunks_recursive(
            section=child,
            page_title=page_title,
            page_url=page_url,
            ancestor_titles=[
                *ancestor_titles,
                section.title
            ],
            page_chunks=page_chunks
        )


# ============================================================
# PAGE-LEVEL TEXT
# ============================================================

def get_page_own_text(root):
    """
    Return text belonging directly to the page itself.

    This is text that occurs:

        after the # page title

    and:

        before the first ## section.

    Example:

        # Acces la căsuța poștală

        Căsuța poștală este asociată...

        ## Conectare de pe PC

        ...

    The first paragraph becomes a page-level chunk.
    """

    if not root.lines:
        return ""

    text = "\n".join(
        root.lines
    )

    return clean_markdown_for_retrieval(
        text
    )


# ============================================================
# WORD COUNT
# ============================================================

def count_words(text):
    """
    Simple whitespace-based word count.

    This is metadata only. It is NOT a tokenizer count.
    """

    return len(
        re.findall(
            r"\S+",
            text
        )
    )


# ============================================================
# PROCESS ONE PAGE
# ============================================================

def process_page(
    markdown_file,
    chunk_counter
):
    """
    Process one Markdown page.

    Creates chunks according to the recursive rules.

    Page-level text is handled separately from sections.
    """

    print(
        f"Processing: {markdown_file.name}"
    )

    # --------------------------------------------------------
    # Read Markdown.
    # --------------------------------------------------------

    with open(
        markdown_file,
        "r",
        encoding="utf-8"
    ) as file:

        markdown = file.read()

    # --------------------------------------------------------
    # Metadata.
    # --------------------------------------------------------

    metadata = parse_front_matter(
        markdown
    )

    page_title = metadata.get(
        "title",
        markdown_file.stem
    )

    page_url = metadata.get(
        "url",
        ""
    )

    # --------------------------------------------------------
    # Remove front matter.
    # --------------------------------------------------------

    body = remove_front_matter(
        markdown
    )

    # --------------------------------------------------------
    # Build Markdown tree.
    # --------------------------------------------------------

    root = parse_markdown_tree(
        body
    )

    page_chunks = []

    # --------------------------------------------------------
    # PAGE-LEVEL TEXT
    #
    # Text before the first ## section becomes its own chunk.
    # --------------------------------------------------------

    page_text = get_page_own_text(
        root
    )

    if page_text:

        page_path = build_page_chunk_path(
            page_title
        )

        page_chunks.append({
            "page_title": page_title,
            "page_link": page_url,
            "section_path": page_path,
            "text": build_chunk_text(
                page_path,
                page_text
            )
        })

    # --------------------------------------------------------
    # PROCESS SECTIONS
    # --------------------------------------------------------

    for section in root.children:

        create_chunks_recursive(
            section=section,
            page_title=page_title,
            page_url=page_url,
            ancestor_titles=[],
            page_chunks=page_chunks
        )

    # --------------------------------------------------------
    # Add chunk IDs and word counts.
    # --------------------------------------------------------

    result = []

    for chunk in page_chunks:

        chunk_id = (
            f"c{next(chunk_counter):06d}"
        )

        result.append({
            "chunk_id": chunk_id,
            "page_title": chunk["page_title"],
            "page_link": chunk["page_link"],
            "section_path": chunk["section_path"],
            "text": chunk["text"],
            "word_count": count_words(
                chunk["text"]
            )
        })

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("DICD MARKDOWN CHUNKER")
    print("=" * 70)

    # --------------------------------------------------------
    # Validate input directory.
    # --------------------------------------------------------

    if not PAGES_DIR.exists():

        print(
            f"[ERROR] Pages directory does not exist: "
            f"{PAGES_DIR}"
        )

        return

    # --------------------------------------------------------
    # Find Markdown files.
    # --------------------------------------------------------

    markdown_files = sorted(
        PAGES_DIR.glob("*.md")
    )

    print(
        f"Markdown pages found: {len(markdown_files)}"
    )

    print()

    # --------------------------------------------------------
    # Chunk ID generator.
    # --------------------------------------------------------

    def counter_generator():

        number = 1

        while True:

            yield number

            number += 1

    chunk_counter = counter_generator()

    # --------------------------------------------------------
    # Process pages.
    # --------------------------------------------------------

    all_chunks = []

    failed = 0

    for markdown_file in markdown_files:

        try:

            chunks = process_page(
                markdown_file,
                chunk_counter
            )

            all_chunks.extend(
                chunks
            )

            print(
                f"  Chunks created: {len(chunks)}"
            )

        except Exception as e:

            failed += 1

            print(
                f"  [ERROR] {e}"
            )

        print()

    # --------------------------------------------------------
    # Save JSON.
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------------------------
    # Statistics.
    # --------------------------------------------------------

    if all_chunks:

        word_counts = [
            chunk["word_count"]
            for chunk in all_chunks
        ]

        average_words = (
            sum(word_counts)
            / len(word_counts)
        )

        minimum_words = min(
            word_counts
        )

        maximum_words = max(
            word_counts
        )

    else:

        average_words = 0
        minimum_words = 0
        maximum_words = 0

    print()
    print("=" * 70)
    print("CHUNKING COMPLETE")
    print("=" * 70)

    print(
        f"Pages processed: "
        f"{len(markdown_files) - failed}"
    )

    print(
        f"Pages failed: {failed}"
    )

    print(
        f"Total chunks: {len(all_chunks)}"
    )

    print(
        f"Average words/chunk: "
        f"{average_words:.1f}"
    )

    print(
        f"Smallest chunk: "
        f"{minimum_words} words"
    )

    print(
        f"Largest chunk: "
        f"{maximum_words} words"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()