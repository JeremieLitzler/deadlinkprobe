"""HTML link extraction."""

import html.parser


class LinkExtractor(html.parser.HTMLParser):
    """Extracts all href values from <a> tags in an HTML document."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for name, value in attrs:
            if name == "href" and value is not None and value != "":
                self.links.append(value)


def extract_links(html_content: str) -> list[str]:
    """Extract all href values from <a> tags in `html_content`.

    Returns an empty list on parse failure.
    """
    extractor = LinkExtractor()
    try:
        extractor.feed(html_content)
    except html.parser.HTMLParseError:
        return []
    return extractor.links
