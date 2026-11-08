# Ввод задается списком строк; запуск и проверка вывода видны в тесте.

from unittest.mock import Mock

import pytest

from domain_search.application.search import SearchService
from domain_search.domain.domains import DomainMatch, RegexDomainMatcher
from domain_search.infrastructure.sources import URLSource
from domain_search.presentation.console import Console, SearchOperations


@pytest.fixture
def console():
    return Console(SearchService(RegexDomainMatcher()))


@pytest.fixture
def input_lines(monkeypatch):
    # Каждый вызов input получает следующую строку из списка.
    lines = []

    def read_input(prompt):
        return lines.pop(0)

    monkeypatch.setattr("builtins.input", read_input)
    return lines


@pytest.mark.parametrize(
    "name, message",
    [
        ("пример.рф", "Корректное доменное имя."),
        ("-bad.org", "Некорректное доменное имя."),
    ],
)
def test_check_from_menu(console, input_lines, capsys, name, message):
    input_lines.extend(["1", name, "0"])

    code = console.run()
    output = capsys.readouterr()

    assert code == 0
    assert message in output.out
    assert output.err == ""
    assert output.out.count("1. Проверить") == 2


@pytest.mark.parametrize(
    "text, count", [("пример.рф example.org", 2), ("", 0)]
)
def test_search_text_from_menu(console, input_lines, capsys, text, count):
    input_lines.extend(["2", text, "0"])

    code = console.run()
    output = capsys.readouterr()

    assert code == 0
    assert f"Найдено: {count}" in output.out
    assert output.err == ""
    if count:
        assert "пример.рф -> xn--e1afmkfd.xn--p1ai [0:9]" in output.out


def test_file_with_spaces_and_windows_encoding(
    console, input_lines, capsys, tmp_path
):
    path = tmp_path / "домены список.txt"
    path.write_bytes("пример.рф".encode("cp1251"))
    input_lines.extend(["3", f'"{path}"', "cp1251", "0"])

    code = console.run()
    output = capsys.readouterr()

    assert code == 0
    assert "пример.рф" in output.out
    assert output.err == ""


def test_url_from_menu(console, input_lines, capsys, monkeypatch):
    def read_page(source):
        return "example.org"

    monkeypatch.setattr(URLSource, "read", read_page)
    input_lines.extend(["4", "https://example.org", "0"])

    code = console.run()
    output = capsys.readouterr()

    assert code == 0
    assert "Найдено: 1" in output.out
    assert output.err == ""


def test_unknown_choice_returns_to_menu(console, input_lines, capsys):
    input_lines.extend(["abc", "0"])

    code = console.run()
    output = capsys.readouterr()

    assert code == 0
    assert "Выберите число от 0 до 4." in output.out
    assert output.err == ""


def test_source_error_returns_to_menu(
    console, input_lines, capsys, tmp_path
):
    missing = str(tmp_path / "missing.txt")
    input_lines.extend(["3", missing, "", "0"])

    code = console.run()
    output = capsys.readouterr()

    assert code == 0
    assert "прочитать файл" in output.err
    assert "Работа завершена." in output.out


def test_console_uses_service_contract(input_lines, capsys):
    service = Mock(spec=SearchOperations)
    service.search.return_value = [
        DomainMatch("example.org", "example.org", 0, 11)
    ]
    console = Console(service)
    input_lines.extend(["2", "произвольный текст", "0"])

    code = console.run()
    output = capsys.readouterr()

    assert code == 0
    assert "example.org -> example.org [0:11]" in output.out
    service.search.assert_called_once()
    service.check.assert_not_called()
