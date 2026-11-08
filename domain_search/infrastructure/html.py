# Извлечение статического текста HTML без исполнения JavaScript.

from html.parser import HTMLParser

HIDDEN_TAGS = {"script", "style", "template", "noscript"}
BLOCK_TAGS = set(
    "address article aside blockquote br div dl dt dd footer form "
    "h1 h2 h3 h4 h5 h6 header hr li main nav ol p pre section "
    "table tbody td th thead tr ul".split()
)


def html_to_text(markup: str) -> str:
    parser = TextExtractor()
    parser.feed(markup)
    parser.close()
    return "".join(parser.parts)


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag in HIDDEN_TAGS:
            self.hidden.append(tag)
            self.parts.append(" ")
        elif tag in BLOCK_TAGS and not self.hidden:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if self.hidden:
            if tag == self.hidden[-1]:
                self.hidden.pop()
        elif tag in BLOCK_TAGS:
            self.parts.append(" ")

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if not self.hidden and tag in BLOCK_TAGS | HIDDEN_TAGS:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)
