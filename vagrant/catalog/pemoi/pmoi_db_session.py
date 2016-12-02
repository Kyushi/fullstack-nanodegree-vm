__author__ = 'Akechi'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from pemoi import app
# from database_setup import Base

# Connect to database and create db_session
# engine = create_engine('sqlite:///../pemoi.db')
# Base.metadata.bind = engine
#
# DBSession = sessionmaker(bind=engine)
# db_session = DBSession()

engine = create_engine(app.config['DB_URI'],
                       convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
