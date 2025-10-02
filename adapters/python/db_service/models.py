from sqlalchemy import Column, Integer, String, Text, Float
from .database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True)
    text = Column(Text)
    embedding = Column(Text)   # نخزنها كـ JSON لاحقًا
    score = Column(Float, default=0.0)
