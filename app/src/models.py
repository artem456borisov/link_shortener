from datetime import datetime

from sqlalchemy import Column, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Links_Table(Base):
    __tablename__ = "links_table"

    id = Column(UUID, primary_key=True, index=True)
    full_link = Column(String, nullable=False)
    short_link = Column(String, nullable=False, default=)