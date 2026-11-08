# В каждом тесте явно создаются зависимости, сервис и ожидаемый результат.

from unittest.mock import Mock

import pytest

from domain_search.application.search import (
    DomainMatcher,
    SearchService,
    Source,
    SourceError,
)
from domain_search.domain.domains import DomainMatch


def test_check_forwards_name_without_preprocessing():
    matcher = Mock(spec=DomainMatcher)
    matcher.is_domain.return_value = True
    service = SearchService(matcher)

    assert service.check(" example.org ")
    matcher.is_domain.assert_called_once_with(" example.org ")


def test_source_is_read_once_and_result_is_returned():
    source = Mock(spec=Source)
    source.read.return_value = " example.org "
    expected = [DomainMatch("example.org", "example.org", 1, 12)]
    matcher = Mock(spec=DomainMatcher)
    matcher.find_domains.return_value = expected
    service = SearchService(matcher)

    result = service.search(source)

    assert result == expected
    source.read.assert_called_once_with()
    matcher.find_domains.assert_called_once_with(" example.org ")


def test_read_error_prevents_matching():
    source = Mock(spec=Source)
    source.read.side_effect = SourceError("нет доступа")
    matcher = Mock(spec=DomainMatcher)
    service = SearchService(matcher)

    with pytest.raises(SourceError, match="нет доступа"):
        service.search(source)

    matcher.find_domains.assert_not_called()
