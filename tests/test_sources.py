# Файлы создаются во временной папке, загрузка страниц подменяется.

import pytest

from domain_search.application.search import SourceError
from domain_search.domain.domains import RegexDomainMatcher
from domain_search.infrastructure.html import html_to_text
from domain_search.infrastructure.sources import FileSource, StringSource


@pytest.fixture
def file_path(tmp_path):
    return tmp_path / "список доменов.txt"


def test_text_is_not_modified():
    source = StringSource(" example.org\n")

    assert source.read() == " example.org\n"


def test_utf8_bom_and_unicode_path(file_path):
    file_path.write_bytes("пример.рф".encode("utf-8-sig"))
    source = FileSource(file_path)

    assert source.read() == "пример.рф"


def test_missing_file(file_path):
    source = FileSource(file_path)

    with pytest.raises(SourceError, match="прочитать"):
        source.read()


def test_invalid_file_bytes(file_path):
    file_path.write_bytes(b"\xff")
    source = FileSource(file_path)

    with pytest.raises(SourceError, match="декодировать"):
        source.read()


def test_byte_limit(file_path, monkeypatch):
    monkeypatch.setattr("domain_search.infrastructure.sources.MAX_BYTES", 4)
    file_path.write_bytes(b"1234")
    assert FileSource(file_path).read() == "1234"

    file_path.write_bytes(b"12345")
    with pytest.raises(SourceError, match="Размер"):
        FileSource(file_path).read()


def test_inline_text_and_entities():
    markup = "<p>exa<b>mple</b>.org &amp; текст</p>"

    assert html_to_text(markup) == " example.org & текст "


def test_block_tags_do_not_join_separate_names():
    markup = "<div>example</div><div>.org</div>"
    text = html_to_text(markup)

    assert RegexDomainMatcher().find_domains(text) == []


def test_hidden_text_attributes_and_comments_are_skipped():
    markup = (
        "<script>bad.org</script><style>bad.net</style>"
        "<template><i>bad.com</i></template><noscript>bad.edu</noscript>"
        '<a href="attribute.org">example.org</a><!-- comment.org -->'
    )
    text = html_to_text(markup)
    found = RegexDomainMatcher().find_domains(text)

    assert len(found) == 1
    assert found[0].value == "example.org"
