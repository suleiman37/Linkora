import pytest
from pydantic import ValidationError

from app.schemas.link import CreateLinkRequest
from app.utils.urls import normalize_url


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "https://example.com/path?one=1&two=2#section",
        "http://localhost:8080/test",
        "https://127.0.0.1/path",
        "https://[::1]/path",
    ],
)
def test_valid_urls_are_accepted(url: str) -> None:
    assert CreateLinkRequest(url=url).url == url


@pytest.mark.parametrize(
    "url",
    [
        "",
        "   ",
        " example.com",
        "example.com ",
        "example.com/path",
        "//example.com/path",
        "ftp://example.com/file",
        "file:///tmp/file",
        "javascript:alert(1)",
        "data:text/plain,test",
        "mailto:user@example.com",
        "tel:+123456789",
        "https://user:password@example.com",
        "https:///missing-host",
        "https://example.com:0/path",
        "https://example.com:65536/path",
    ],
)
def test_invalid_urls_are_rejected(url: str) -> None:
    with pytest.raises(ValidationError):
        CreateLinkRequest(url=url)


def test_url_length_limit_is_exact() -> None:
    valid_url = "https://example.com/" + "a" * (2048 - len("https://example.com/"))
    too_long_url = valid_url + "a"

    assert CreateLinkRequest(url=valid_url).url == valid_url
    with pytest.raises(ValidationError):
        CreateLinkRequest(url=too_long_url)


@pytest.mark.parametrize(
    ("original", "normalized"),
    [
        ("HTTP://Example.com:80/path", "http://example.com/path"),
        ("https://Example.com:443/path", "https://example.com/path"),
        ("https://example.com/path/", "https://example.com/path/"),
        ("https://example.com?a=1&b=2", "https://example.com?a=1&b=2"),
        ("https://example.com?b=2&a=1", "https://example.com?b=2&a=1"),
        ("https://example.com/page#one", "https://example.com/page#one"),
    ],
)
def test_normalization_is_conservative(original: str, normalized: str) -> None:
    assert normalize_url(original) == normalized