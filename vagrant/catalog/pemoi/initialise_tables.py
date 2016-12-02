__author__ = 'Akechi'

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

from database_setup import Base, \
                           User, \
                           Category, \
                           Item

# Connect to database and create db_session
engine = create_engine('sqlite:///../pemoi.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()

categories = db_session.query(Category).all()
items = db_session.query(Item).all()
users = db_session.query(User).all()

admin = db_session.query(User).filter_by(name="Admin").one()

def populate_categories(cats):
    for cat in cats:
        print "Creating category %s" % cat
        category = Category(name=cat,
                            description="For all things %s" % cat,
                            user_id=admin.id,
                            public=True
                            )
        db_session.add(category)
        print "Added to session"
        db_session.commit()
        print "Committed"
    return

categories = ["Painting", "Sculpture", "Video", "Performance", "Installation", "Action"]

populate_categories(categories)
