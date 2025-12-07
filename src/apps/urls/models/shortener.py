import sqlalchemy as db
from sqlalchemy.orm import Mapped, Session, mapped_column

from core.models import BaseModel


class URLShortener(BaseModel):
    original_url: Mapped[str] = mapped_column(db.String(2048), nullable=False)
    short_code: Mapped[str] = mapped_column(db.String(10), nullable=False, unique=True)
    access_count: Mapped[int] = mapped_column(db.Integer, default=0, nullable=False)

    def increment_access_count(self, session: Session) -> None:
        """Increment the access count for the URL."""
        self.access_count += 1
        session.commit()
        session.refresh(self)
