from datetime import datetime
from enum import Enum
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, field_validator


MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = {"http", "https"}


def validate_original_url(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("URL must not be empty")
    if value != value.strip():
        raise ValueError("URL must not have surrounding whitespace")
    if len(value) > MAX_URL_LENGTH:
        raise ValueError("URL must not exceed 2048 characters")

    parsed = urlsplit(value)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise ValueError("URL scheme must be http or https")
    if not parsed.netloc or not parsed.hostname:
        raise ValueError("URL must include a valid host")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URL must not include credentials")
    try:
        if parsed.port is not None and not 0 < parsed.port <= 65535:
            raise ValueError("URL port is invalid")
    except ValueError as error:
        raise ValueError("URL port is invalid") from error

    return value


class CreateLinkRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return validate_original_url(value)


class CreateLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime


class LinkStatisticsResponse(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    last_clicked_at: datetime | None
    created_at: datetime


class LinkSort(str, Enum):
    CREATED_DESC = "created_desc"
    CREATED_ASC = "created_asc"
    CLICKS_DESC = "clicks_desc"


class LinkHistoryItem(BaseModel):
    id: int
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime
    click_count: int
    last_clicked_at: datetime | None


class LinkPagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class LinkListResponse(BaseModel):
    items: list[LinkHistoryItem]
    pagination: LinkPagination


class AnalyticsSummaryResponse(BaseModel):
    total_links: int
    total_clicks: int
    last_clicked_at: datetime | None
    top_links: list[LinkHistoryItem]
    recently_active_links: list[LinkHistoryItem]