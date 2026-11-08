# Проверка меток и общей длины доменного имени.

import re

LABEL = r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
TOP_LABEL = r"(?:[a-z]{1,63}|xn--[a-z0-9](?:[a-z0-9-]{0,57}[a-z0-9])?)"
DOMAIN_PATTERN = re.compile(
    rf"(?=.{{1,253}}\Z)(?:{LABEL}\.)+{TOP_LABEL}",
    re.ASCII | re.IGNORECASE,
)


class RegexDomainMatcher:
    def is_domain(self, name: str) -> bool:
        return _normalize_domain(name) is not None


def _normalize_domain(name: str) -> str | None:
    # Одна завершающая точка обозначает корень DNS.
    candidate = name.removesuffix(".").lower()
    return candidate if DOMAIN_PATTERN.fullmatch(candidate) else None
