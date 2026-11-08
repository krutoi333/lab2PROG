# Грамматика, нормализация и поиск доменных имен.

import pytest

from domain_search.domain.domains import RegexDomainMatcher


@pytest.fixture
def matcher():
    return RegexDomainMatcher()


@pytest.mark.parametrize(
    "name",
    ["example.org", "A-1.Example.ORG."],
)
def test_valid_ascii_domains(matcher, name):
    assert matcher.is_domain(name)


@pytest.mark.parametrize(
    "name",
    [
        "", "localhost", "-bad.org", "bad-.org", "bad_name.org",
        "a..org", "127.0.0.1", "a.123", "https://example.org",
    ],
)
def test_invalid_names_are_rejected_as_whole_strings(matcher, name):
    assert not matcher.is_domain(name)


@pytest.mark.parametrize(
    "name, expected",
    [
        ("a" * 63 + ".org", True),
        ("a" * 64 + ".org", False),
        ("host." + "a" * 63, True),
        ("host." + "a" * 64, False),
    ],
)
def test_label_length_boundaries(matcher, name, expected):
    assert matcher.is_domain(name) == expected


@pytest.mark.parametrize("root", ["", "."])
def test_total_ascii_length_and_optional_root(matcher, root):
    maximum = ".".join(("a" * 63, "b" * 63, "c" * 63, "d" * 61))
    assert len(maximum) == 253
    assert matcher.is_domain(maximum + root)
    assert not matcher.is_domain(maximum + "d" + root)


@pytest.mark.parametrize(
    "name",
    ["пример.рф", "xn--e1afmkfd.xn--p1ai", "bücher.de"],
)
def test_unicode_and_valid_punycode(matcher, name):
    assert matcher.is_domain(name)


@pytest.mark.parametrize(
    "name",
    ["xn--a.org", "☕.example"],
)
def test_malformed_ace_and_disallowed_unicode(matcher, name):
    assert not matcher.is_domain(name)


def test_unicode_dot_and_root(matcher):
    assert matcher.is_domain("пример。рф。")


def test_length_is_checked_after_idna_encoding(matcher):
    assert not matcher.is_domain("я" * 64 + ".рф")
