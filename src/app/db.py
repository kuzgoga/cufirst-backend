from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(str(settings.database_dsn), pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def provide_db_session() -> Generator[Session, None, None]:
    with SessionFactory() as session:
        yield session
