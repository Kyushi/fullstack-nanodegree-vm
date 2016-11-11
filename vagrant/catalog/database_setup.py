from sqlalchemy import Column, \
                       ForeignKey, \
                       Integer, \
                       String, \
                       DateTime, \
                       Boolean, \
                       UnicodeText, \
                       create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """User class for the user table

    Columns:
    id: Primary key, auto-genereated, incremental integer
    name: User's real name or name from Google Plus, Facebook, Twitter, github
          (if implemented)
    username: User name, chosen by user, used for display on website
    email: User's e-mail address.
    register_date: DateTime of user registration, gets added automatically

    All columns are required or auto-generated
    """
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    register_date = Column(DateTime(timezone=True), server_default=func.now())

class Category(Base):
    """Category class for the category table

    Columns:
    id: Primary key, auto-generated, incremental integer
    name: Name of the category, must be unique for public categories
    user_id: Foreign key, user.id from user table
    user: Relationship to User table
    add_date: DateTime of addition, auto-generated
    public: Boolean, so that the user can decide whether or not to make a
            category public (private is default)
    """
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    add_date = Column(DateTime(timezone=True), server_default=func.now())
    public = Column(Boolean)

    @property
    def serialize(self):
        """Return public categories in serialisable format"""
        if self.public:
            return {
                'name': self.name,
            }

class Item(Base):
    """Item class for item table

    Columns:
    id: Primary key, auto-generated, incremental integer
    link: String for URL to picture/video. Required
    title: String for the title of the inspiration. Optional
    artist: String for the artist/author/director. Optional
    note: UnicodeText for storing personal notes. Optional
    keywords: String for keywords, optional
    add_date: DateTime of addition, auto-generated
    edit_date: DateTime of last edit, updated on edit
    category_id: Foreign key category.id form category table
    category: Relationship to Category class
    user_id: Foreign key user.id from user table
    user: Relationship to User class
    public: Boolean, so that the user can decide whether or not to share the
            inspiration
    """
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    link = Column(String(250), nullable=False)
    title = Column(String(250))
    artist = Column(String(250))
    note = Column(UnicodeText)
    keywords = Column(String(250))
    add_date = Column(DateTime(timezone=True), server_default = func.now())
    edit_date = Column(DateTime(timezone=True), onupdate = func.now())
    category_id = Column(Integer, ForeignKey('category.id'))
    category = Relationship('Category')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = Relationship('User')
    public = Column(Boolean)

    @property
    def serialize(self):
        """Return public items in serialisable format"""
        if self.public:
            return {
                'link': self.link,
                'title': self.title,
                'artist': self.artist,
                'note': self.note,
            }


engine = create_engine('sqlite:///pemoi.db')

Base.metadata.create_all(engine)
