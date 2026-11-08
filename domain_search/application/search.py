# Контракты зависимостей и сценарии проверки и поиска.

from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from domain_search.domain.domains import DomainMatch


class SourceError(Exception):
    # Источник не смог предоставить текст.
    pass


class Source(Protocol):
    # Единый контракт пользовательского текста, файла и страницы.

    @abstractmethod
    def read(self) -> str: ...


class DomainMatcher(Protocol):
    def is_domain(self, name: str) -> bool: ...

    def find_domains(self, text: str) -> list[DomainMatch]: ...


@dataclass(frozen=True)
class SearchService:
    matcher: DomainMatcher

    def check(self, name: str) -> bool:
        return self.matcher.is_domain(name)

    def search(self, source: Source) -> list[DomainMatch]:
        text = source.read()
        return self.matcher.find_domains(text)
