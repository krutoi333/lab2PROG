# Файлы создаются во временной папке, загрузка страниц подменяется.

import pytest

from domain_search.application.search import SourceError
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
