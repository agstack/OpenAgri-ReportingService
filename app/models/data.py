from sqlalchemy import Column, Integer, String

from db.base_class import Base


class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    filename = Column(String, nullable=False)
    data = Column(String(10485760), nullable=False)

