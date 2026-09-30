from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.link import (
    AnalyticsSummaryResponse,
    CreateLinkRequest,
    CreateLinkResponse,
    LinkHistoryItem,
    LinkListResponse,
    LinkPagination,
    LinkSort,
    LinkStatisticsResponse,
)
from app.services.links import LinkService


router = APIRouter(prefix="/links", tags=["links"])
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])
public_router = APIRouter(tags=["redirect"])


def _history_item(link) -> LinkHistoryItem:
    return LinkHistoryItem(
        id=link.id,
        original_url=link.original_url,
        short_code=link.short_code,
        short_url=f"{settings.base_url.rstrip('/')}/{link.short_code}",
        created_at=link.created_at,
        click_count=link.click_count,
        last_clicked_at=link.last_clicked_at,
    )


@router.post("", response_model=CreateLinkResponse, status_code=status.HTTP_201_CREATED)
def create_link(
    request: CreateLinkRequest,
    http_response: Response,
    session: Session = Depends(get_db),
) -> CreateLinkResponse:
    result = LinkService().create_link_with_status(session, request.url)

    response = CreateLinkResponse(
        id=result.link.id,
        original_url=result.link.original_url,
        short_code=result.link.short_code,
        short_url=f"{settings.base_url.rstrip('/')}/{result.link.short_code}",
        created_at=result.link.created_at,
    )
    if result.existing:
        http_response.status_code = status.HTTP_200_OK
        http_response.headers["X-Link-Existing"] = "true"
    else:
        http_response.headers["X-Link-Existing"] = "false"
    return response


@router.get("", response_model=LinkListResponse, status_code=status.HTTP_200_OK)
def list_links(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=2048),
    sort: LinkSort = Query(default=LinkSort.CREATED_DESC),
    session: Session = Depends(get_db),
) -> LinkListResponse:
    result = LinkService().list_links(
        session,
        page=page,
        page_size=page_size,
        search=search,
        sort=sort,
    )
    total_pages = (result.total + result.page_size - 1) // result.page_size
    return LinkListResponse(
        items=[_history_item(link) for link in result.links],
        pagination=LinkPagination(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
            total_pages=total_pages,
        ),
    )


@public_router.get("/{short_code}", status_code=status.HTTP_302_FOUND)
def redirect_to_original_url(
    short_code: str,
    session: Session = Depends(get_db),
) -> RedirectResponse:
    link = LinkService().resolve_and_record_click(session, short_code)

    return RedirectResponse(
        url=link.original_url,
        status_code=status.HTTP_302_FOUND,
    )


@router.get(
    "/{short_code}/stats",
    response_model=LinkStatisticsResponse,
    status_code=status.HTTP_200_OK,
)
def get_link_statistics(
    short_code: str,
    session: Session = Depends(get_db),
) -> LinkStatisticsResponse:
    link = LinkService().get_link_by_short_code(session, short_code)

    return LinkStatisticsResponse(
        short_code=link.short_code,
        original_url=link.original_url,
        click_count=link.click_count,
        last_clicked_at=link.last_clicked_at,
        created_at=link.created_at,
    )


@analytics_router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    session: Session = Depends(get_db),
) -> AnalyticsSummaryResponse:
    result = LinkService().get_analytics_summary(session)
    return AnalyticsSummaryResponse(
        total_links=result.total_links,
        total_clicks=result.total_clicks,
        last_clicked_at=result.last_clicked_at,
        top_links=[_history_item(link) for link in result.top_links],
        recently_active_links=[_history_item(link) for link in result.recently_active_links],
    )