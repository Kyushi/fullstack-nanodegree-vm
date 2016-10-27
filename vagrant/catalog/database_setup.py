import sys
from sqlalchemy import Column, \
                       ForeignKey, \
                       Integer, \
                       String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Create base class
Base = declarative_base()

# Create Restaurant class
class Restaurant(Base):
    '''
    Database for restaurants

    Restaurants in the restaurant table have an ID, a name and a cuisine.
    '''
    __tablename__ = 'restaurant'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)


# Create MenuItem class:
class MenuItem(Base):
    '''
    Database for menu items

    Menu items in the menu_item table have an ID, a name, a course it belongs
    to, a description, a price and a foreign key restaurant_id.
    '''
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)



### Keep this at the end of the file ###
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)
