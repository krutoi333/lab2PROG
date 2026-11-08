# Правила проверки доменных имен и поиска в исходном тексте.

import re
from dataclasses import dataclass

import idna

LABEL = r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
TOP_LABEL = r"(?:[a-z]{1,63}|xn--[a-z0-9](?:[a-z0-9-]{0,57}[a-z0-9])?)"
DOMAIN_PATTERN = re.compile(
    rf"(?=.{{1,253}}\Z)(?:{LABEL}\.)+{TOP_LABEL}",
    re.ASCII | re.IGNORECASE,
)

DOT_VARIANTS = str.maketrans({"。": ".", "．": ".", "｡": "."})

# Ошибочный кандидат проверяется целиком: точки, дефисы и подчеркивания
# не отделяются, чтобы bad..example.org не дал совпадение example.org.
SEPARATORS = "/\\:@<>()[]{};,!?\"'=+&%#|«»“”‘’—–"
TOKEN_PATTERN = re.compile(rf"[^\s{re.escape(SEPARATORS)}]+")


@dataclass(frozen=True)
class DomainMatch:
    # Исходное написание, ASCII-форма и полуинтервал [start:end).

    value: str
    ascii_name: str
    start: int
    end: int


class RegexDomainMatcher:
    def is_domain(self, name: str) -> bool:
        return _normalize_domain(name) is not None

    def find_domains(self, text: str) -> list[DomainMatch]:
        found = []
        for candidate in TOKEN_PATTERN.finditer(text):
            ascii_name = _normalize_domain(candidate.group())
            if ascii_name is not None:
                found.append(
                    DomainMatch(
                        candidate.group(),
                        ascii_name,
                        candidate.start(),
                        candidate.end(),
                    )
                )
        return found


def _normalize_domain(name: str) -> str | None:
    # Ограничения длины относятся к ASCII-форме без корневой точки.
    candidate = name.translate(DOT_VARIANTS).removesuffix(".")
    try:
        labels = [_ascii_label(label) for label in candidate.split(".")]
    except idna.IDNAError:
        return None
    candidate = ".".join(labels)
    return candidate if DOMAIN_PATTERN.fullmatch(candidate) else None


def _ascii_label(label: str) -> str:
    if label.isascii() and not label.lower().startswith("xn--"):
        return label.lower()
    # Проверяет содержимое A-label и Unicode по IDNA2008 после UTS #46.
    return idna.encode(label, uts46=True, std3_rules=True).decode("ascii")
