from typing import Any

from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase

# @as_declarative()
# class Base:
#     id: Any
#     __name__: str
#     # Generate __tablename__ automatically
#
#     @declared_attr
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()


class Base(DeclarativeBase):
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically"""
        return cls.__name__.lower()

    def _asdict(self):
        """Convert extract record to dict."""
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}