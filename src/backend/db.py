import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class InboundMessage(Base):
    __tablename__ = "inbound_messages"
    __table_args__ = {"schema": "beststag"}

    id = Column(Integer, primary_key=True, index=True)
    from_number = Column(String, nullable=False)
    to_number = Column(String, nullable=False)
    message_body = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)

# Create tables
Base.metadata.create_all(bind=engine)
