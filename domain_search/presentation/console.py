# Консольное меню проверки имени и поиска в выбранном источнике.

import sys
from pathlib import Path
from typing import Protocol

from domain_search.application.search import Source, SourceError
from domain_search.domain.domains import DomainMatch
from domain_search.infrastructure.sources import (
    FileSource,
    StringSource,
    URLSource,
)


class SearchOperations(Protocol):
    # Консоль получает операции сервиса через собственный контракт.

    def check(self, name: str) -> bool: ...

    def search(self, source: Source) -> list[DomainMatch]: ...


class Console:
    def __init__(self, service: SearchOperations) -> None:
        self.service = service

    def run(self) -> int:
        while True:
            try:
                choice = _read_choice()
                if choice == "0":
                    print("Работа завершена.")
                    return 0
                self._perform_choice(choice)
            except SourceError as error:
                print(f"Ошибка ввода: {error}", file=sys.stderr)
            except (EOFError, KeyboardInterrupt):
                print("\nРабота завершена.")
                return 0

    def _perform_choice(self, choice: str) -> None:
        if choice == "1":
            name = input("Введите доменное имя без протокола: ")
            self._check_domain(name)
        elif choice in {"2", "3", "4"}:
            source = _read_source(choice)
            matches = self.service.search(source)
            _print_matches(matches)
        else:
            print("Выберите число от 0 до 4.")

    def _check_domain(self, name: str) -> None:
        valid = self.service.check(name)
        print(
            "Корректное доменное имя."
            if valid
            else "Некорректное доменное имя."
        )


def _read_choice() -> str:
    print(
        "\n1. Проверить доменное имя\n"
        "2. Найти домены в тексте\n"
        "3. Найти домены в файле\n"
        "4. Найти домены на веб-странице\n"
        "0. Выход"
    )
    return input("Выберите действие: ").strip()


def _read_source(choice: str) -> Source:
    if choice == "2":
        return StringSource(input("Введите текст: "))
    if choice == "3":
        path = Path(input("Путь к текстовому файлу: ").strip().strip('"'))
        encoding = input("Кодировка файла [UTF-8]: ").strip() or "utf-8-sig"
        return FileSource(path, encoding)
    return URLSource(input("URL страницы HTTP(S): ").strip())


def _print_matches(matches: list[DomainMatch]) -> None:
    print(f"Найдено: {len(matches)}")
    for match in matches:
        print(
            f"{match.value} -> {match.ascii_name} [{match.start}:{match.end}]"
        )
