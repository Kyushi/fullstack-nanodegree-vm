__author__ = 'Akechi'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base

# Connect to database and create db_session
engine = create_engine('sqlite:///pemoi.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()
