# Единая точка запуска: python -m domain_search.

import sys
from pathlib import Path
from typing import Protocol

if not __package__:
    # Позволяет вывести подсказку при неподдерживаемом запуске файла.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain_search.application.search import SearchService
from domain_search.domain.domains import RegexDomainMatcher
from domain_search.presentation.console import Console


class Application(Protocol):
    def run(self) -> int: ...


def main(application: Application) -> int:
    return application.run()


def create_application() -> Application:
    matcher = RegexDomainMatcher()
    service = SearchService(matcher)
    return Console(service)


if __name__ == "__main__":
    if not __package__ or len(sys.argv) > 1:
        raise SystemExit(
            "Используйте запуск без аргументов: python -m domain_search"
        )
    raise SystemExit(main(create_application()))
