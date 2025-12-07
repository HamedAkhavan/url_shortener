import logging
from datetime import datetime
from typing import (
    TypeVar,
)

import sqlalchemy as db
from sqlalchemy import Select, delete, insert, select, update
from sqlalchemy.exc import (
    MultipleResultsFound,
    NoResultFound,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.sql import func

from core.database import Base

T = TypeVar("T", bound=Base)

logger = logging.getLogger(__name__)


class Manager[T: Base]:
    def __init__(self, model: type[T] = None, default_filters: dict = None):
        self.model = model
        self.default_filters = default_filters or {}

    def _prepare_filters(self, **kwargs) -> list:
        filters = []
        for attr, value in kwargs.items():
            filters.append(getattr(self.model, attr).__eq__(value))
        return filters

    def _build_query(self, **filters) -> Select:
        """Build a fresh query with filters applied."""
        query = select(self.model).select_from(self.model)
        all_filters = {**self.default_filters, **filters}
        if all_filters:
            query = query.where(*self._prepare_filters(**all_filters))
        return query

    def get(self, session: Session, **kwargs) -> T:
        """Get a single instance matching the filters."""
        query = self._build_query(**kwargs)
        return session.execute(query).unique().scalar_one()

    def select(self, *columns) -> Select:
        """Select specific columns."""
        query = select(self.model).select_from(self.model)
        if columns:
            return query.with_only_columns(*columns).select_from(self.model)
        return query

    def create(self, session: Session, **kwargs) -> T:
        """Create and return a new instance."""
        object_instance = session.execute(
            insert(self.model).returning(self.model).values(**kwargs)
        ).scalar_one()
        session.commit()
        return object_instance

    def get_or_create(
        self, session: Session, defaults: dict = None, **kwargs
    ) -> tuple[T, bool]:
        """Get or create an instance. Returns (instance, created)."""
        created = False
        try:
            query = self._build_query(**kwargs)
            instance = session.execute(query).unique().scalar_one()
        except NoResultFound:
            created = True
            if defaults is not None:
                kwargs.update(defaults)
            instance = self.create(session, **kwargs)
        except MultipleResultsFound:
            logger.error(
                "Multiple results found for get_or_create with filters: %s", kwargs
            )
            return None, created

        return instance, created


class ObjectsDescriptor:
    def __init__(self, **default_filters) -> None:
        self.default_filters = default_filters

    def __get__(self, _: T, owner: type[T]) -> Manager[T]:
        return Manager(model=owner, default_filters=self.default_filters)


class BaseModel(Base):
    """Abstract base model with common functionality for all models."""

    __abstract__ = True
    objects = ObjectsDescriptor()

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        db.DateTime(timezone=True), onupdate=func.now()
    )

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:  # noqa
        """Generate table name from module and class name."""
        return f"{cls.__module__.split('.')[1]}_{cls.__name__.lower()}"

    def update(self, session: Session, **kwargs) -> None:
        """
        Update instance with given values and commit.
        """
        # Lock the row for update to prevent race conditions
        session.execute(
            select(self.__class__)
            .where(self.__class__.id == self.id)
            .with_for_update(of=self.__class__)
        )
        session.execute(
            update(self.__class__)
            .where(self.__class__.id == self.id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        session.commit()
        session.refresh(self)

    def delete(self, session: Session) -> None:
        """
        Delete this instance from database.
        """
        # Lock the row for update before deleting to prevent race conditions
        session.execute(
            select(self.__class__)
            .where(self.__class__.id == self.id)
            .with_for_update(of=self.__class__)
        )
        session.execute(
            delete(self.__class__)
            .where(self.__class__.id == self.id)
            .execution_options(synchronize_session="fetch")
        )
        session.commit()
