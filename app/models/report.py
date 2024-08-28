from sqlalchemy import Column, Integer, String

from db.base_class import Base


class Report(Base):
    __tablename__ = 'report'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    file = Column(String(10485760), nullable=False)
    type = Column(String, nullable=False)
