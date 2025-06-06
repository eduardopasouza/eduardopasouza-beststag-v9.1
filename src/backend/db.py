import os
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)

if DATABASE_URL.startswith("sqlite"):
    TABLE_ARGS: dict | None = {}
else:
    TABLE_ARGS = {"schema": "beststag"}

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class InboundMessage(Base):
    __tablename__ = "inbound_messages"
    __table_args__ = TABLE_ARGS

    id = Column(Integer, primary_key=True, index=True)
    from_number = Column(String, nullable=False)
    to_number = Column(String, nullable=False)
    message_body = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)


# Create tables
Base.metadata.create_all(bind=engine)
