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


def test_domains_in_urls_and_email(matcher):
    text = "https://one.org/two.net user@EXAMPLE.COM?x=пример.рф"
    found = matcher.find_domains(text)
    assert [item.value for item in found] == [
        "one.org", "two.net", "EXAMPLE.COM", "пример.рф",
    ]
    for item in found:
        assert text[item.start:item.end] == item.value


def test_duplicates_and_root_dot_are_preserved(matcher):
    found = matcher.find_domains("example.org, example.org.")
    assert [item.value for item in found] == ["example.org", "example.org."]
    assert [(item.start, item.end) for item in found] == [(0, 11), (13, 25)]
    assert [item.ascii_name for item in found] == ["example.org"] * 2


def test_invalid_candidates_do_not_return_valid_suffixes(matcher):
    text = "bad..example.org -example.org ex_ample.org example.org.."
    assert matcher.find_domains(text) == []


def test_canonical_forms_keep_original_unicode_offsets(matcher):
    # Комбинируемый знак занимает отдельную позицию исходного текста.
    text = "До: bu\u0308cher.de!"
    item = matcher.find_domains(text)[0]
    assert item.ascii_name == "xn--bcher-kva.de"
    assert (item.start, item.end) == (4, 14)
    assert text[item.start:item.end] == item.value
