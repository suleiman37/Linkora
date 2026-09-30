from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings, settings
from app.errors.exceptions import ApplicationError
from app.models.link import Link
from app.repositories.links import LinkRepository
from app.schemas.link import LinkSort
from app.utils.short_codes import generate_short_code
from app.utils.urls import normalize_url


class LinkCreationError(ApplicationError):
    """Raised when a link cannot be persisted after bounded retries."""

    status_code = 503
    error_code = "link_creation_unavailable"
    default_message = "Unable to create link"


class LinkNotFoundError(ApplicationError):
    """Raised when a short code does not identify a stored link."""

    status_code = 404
    error_code = "link_not_found"
    default_message = "Link not found"


class ClickTrackingError(ApplicationError):
    """Raised when a redirect click cannot be recorded."""

    status_code = 503
    error_code = "click_tracking_unavailable"
    default_message = "Unable to record link click"


@dataclass(frozen=True)
class LinkCreationResult:
    link: Link
    existing: bool


@dataclass(frozen=True)
class LinkListResult:
    links: list[Link]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True)
class AnalyticsSummaryResult:
    total_links: int
    total_clicks: int
    last_clicked_at: object | None
    top_links: list[Link]
    recently_active_links: list[Link]


class LinkService:
    def __init__(
        self,
        repository: LinkRepository | None = None,
        code_generator: Callable[[], str] = generate_short_code,
        max_attempts: int = 5,
        app_settings: Settings = settings,
    ) -> None:
        self.repository = repository or LinkRepository()
        self.code_generator = code_generator
        self.max_attempts = max_attempts
        self.settings = app_settings

    def create_link(self, session: Session, original_url: str) -> Link:
        return self.create_link_with_status(session, original_url).link

    def create_link_with_status(
        self,
        session: Session,
        original_url: str,
    ) -> LinkCreationResult:
        normalized_url = normalize_url(original_url)

        for _ in range(self.max_attempts):
            try:
                with session.begin():
                    existing_link = self.repository.get_by_normalized_url(
                        session,
                        normalized_url,
                    )
                    if existing_link is not None:
                        return LinkCreationResult(existing_link, True)

                    link = Link(
                        original_url=original_url,
                        normalized_url=normalized_url,
                        short_code=self.code_generator(),
                    )
                    self.repository.add(session, link)
                    session.flush()
                return LinkCreationResult(link, False)
            except IntegrityError as error:
                if self._is_normalized_url_collision(error):
                    existing_link = self.repository.get_by_normalized_url(
                        session,
                        normalized_url,
                    )
                    if existing_link is not None:
                        return LinkCreationResult(existing_link, True)
                    raise LinkCreationError("Unable to create link") from error
                if not self._is_short_code_collision(error):
                    raise LinkCreationError("Unable to create link") from error

        raise LinkCreationError("Unable to generate a unique short code")

    def get_link_by_short_code(self, session: Session, short_code: str) -> Link:
        link = self.repository.get_by_short_code(session, short_code)
        if link is None:
            raise LinkNotFoundError("Link not found")
        return link

    def list_links(
        self,
        session: Session,
        *,
        page: int,
        page_size: int,
        search: str | None,
        sort: LinkSort,
    ) -> LinkListResult:
        links, total = self.repository.list_links(
            session,
            offset=(page - 1) * page_size,
            limit=page_size,
            search=search.strip() if search else None,
            sort=sort,
        )
        return LinkListResult(links=links, total=total, page=page, page_size=page_size)

    def get_analytics_summary(self, session: Session, *, limit: int = 5) -> AnalyticsSummaryResult:
        total_links, total_clicks, last_clicked_at, top_links, recently_active_links = (
            self.repository.get_analytics_summary(session, limit=limit)
        )
        return AnalyticsSummaryResult(
            total_links=total_links,
            total_clicks=total_clicks,
            last_clicked_at=last_clicked_at,
            top_links=top_links,
            recently_active_links=recently_active_links,
        )

    def resolve_and_record_click(self, session: Session, short_code: str) -> Link:
        try:
            with session.begin():
                link = self.repository.get_by_short_code(session, short_code)
                if link is None:
                    raise LinkNotFoundError("Link not found")
                if not self.repository.increment_click_count(session, link.id):
                    raise ClickTrackingError("Unable to record link click")
            return link
        except (LinkNotFoundError, ClickTrackingError):
            raise
        except Exception as error:
            raise ClickTrackingError("Unable to record link click") from error

    @staticmethod
    def _is_short_code_collision(error: IntegrityError) -> bool:
        original_error = error.orig
        constraint_name = getattr(getattr(original_error, "diag", None), "constraint_name", None)
        if constraint_name == "uq_links_short_code":
            return True
        message = str(original_error).lower()
        return "uq_links_short_code" in message or "links.short_code" in message

    @staticmethod
    def _is_normalized_url_collision(error: IntegrityError) -> bool:
        original_error = error.orig
        constraint_name = getattr(getattr(original_error, "diag", None), "constraint_name", None)
        if constraint_name == "uq_links_normalized_url":
            return True
        message = str(original_error).lower()
        return "uq_links_normalized_url" in message or "links.normalized_url" in message