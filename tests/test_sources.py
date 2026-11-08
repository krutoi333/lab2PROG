# Файлы создаются во временной папке, загрузка страниц подменяется.

from domain_search.infrastructure.sources import StringSource


def test_text_is_not_modified():
    source = StringSource(" example.org\n")

    assert source.read() == " example.org\n"
