from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.link import Link
from app.schemas.link import LinkSort


class LinkRepository:
    def add(self, session: Session, link: Link) -> None:
        session.add(link)

    def get_by_short_code(self, session: Session, short_code: str) -> Link | None:
        return session.scalar(select(Link).where(Link.short_code == short_code))

    def get_by_normalized_url(
        self,
        session: Session,
        normalized_url: str,
    ) -> Link | None:
        return session.scalar(select(Link).where(Link.normalized_url == normalized_url))

    def list_links(
        self,
        session: Session,
        *,
        offset: int,
        limit: int,
        search: str | None,
        sort: LinkSort,
    ) -> tuple[list[Link], int]:
        filters = []
        if search:
            search_pattern = f"%{search.lower()}%"
            filters.append(
                (func.lower(Link.original_url).like(search_pattern))
                | (func.lower(Link.short_code).like(search_pattern))
            )

        count_query = select(func.count()).select_from(Link)
        list_query = select(Link)
        if filters:
            count_query = count_query.where(*filters)
            list_query = list_query.where(*filters)

        if sort is LinkSort.CREATED_ASC:
            list_query = list_query.order_by(Link.created_at.asc(), Link.id.asc())
        elif sort is LinkSort.CLICKS_DESC:
            list_query = list_query.order_by(Link.click_count.desc(), Link.id.desc())
        else:
            list_query = list_query.order_by(Link.created_at.desc(), Link.id.desc())

        total = session.scalar(count_query) or 0
        links = list(session.scalars(list_query.offset(offset).limit(limit)))
        return links, total

    def get_analytics_summary(self, session: Session, *, limit: int) -> tuple[int, int, object | None, list[Link], list[Link]]:
        total_links = session.scalar(select(func.count()).select_from(Link)) or 0
        total_clicks = session.scalar(select(func.coalesce(func.sum(Link.click_count), 0))) or 0
        last_clicked_at = session.scalar(select(func.max(Link.last_clicked_at)))
        top_links = list(
            session.scalars(
                select(Link)
                .order_by(Link.click_count.desc(), Link.id.desc())
                .limit(limit)
            )
        )
        recently_active_links = list(
            session.scalars(
                select(Link)
                .where(Link.last_clicked_at.is_not(None))
                .order_by(Link.last_clicked_at.desc(), Link.id.desc())
                .limit(limit)
            )
        )
        return total_links, total_clicks, last_clicked_at, top_links, recently_active_links

    def increment_click_count(self, session: Session, link_id: int) -> bool:
        result = session.execute(
            update(Link)
            .where(Link.id == link_id)
            .values(
                click_count=Link.click_count + 1,
                last_clicked_at=func.current_timestamp(),
            )
        )
        return result.rowcount == 1