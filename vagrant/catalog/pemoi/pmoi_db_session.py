"""Database session for user across the site."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from pemoi import app

engine = create_engine(app.config['DB_URI'],
                       convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
