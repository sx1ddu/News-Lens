import pytest
from pydantic import ValidationError

from schemas import SearchRequest


def test_valid_query_accepted():
    request = SearchRequest(query="ai regulation")
    assert request.query == "ai regulation"
    assert request.page_size == 10  # default


def test_empty_query_rejected():
    with pytest.raises(ValidationError):
        SearchRequest(query="")


def test_whitespace_only_query_rejected():
    with pytest.raises(ValidationError):
        SearchRequest(query="   ")


def test_excessively_long_query_rejected():
    with pytest.raises(ValidationError):
        SearchRequest(query="a" * 101)


def test_page_size_out_of_range_rejected():
    with pytest.raises(ValidationError):
        SearchRequest(query="ai policy", page_size=50)

    with pytest.raises(ValidationError):
        SearchRequest(query="ai policy", page_size=0)
