# Чтение источников с единым контрактом.

from dataclasses import dataclass

from domain_search.application.search import Source


@dataclass(frozen=True)
class StringSource(Source):
    text: str

    def read(self) -> str:
        return self.text
