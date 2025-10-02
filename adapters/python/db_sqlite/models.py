from sqlalchemy import Column, Integer, String, Text

from .database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True)
    text = Column(Text)
