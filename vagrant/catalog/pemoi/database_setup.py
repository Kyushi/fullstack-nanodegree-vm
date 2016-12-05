"""Set up the database, create tables User, Category, Items"""

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
from pemoi import app
Base = declarative_base()

class User(Base):
    """User class for the user table

    Columns:
    id: Primary key, auto-genereated, incremental integer
    name: User's real name or name from Google Plus, Facebook, Twitter, github
          (if implemented)
    username: User name, chosen by user, used for display on website, unique
    email: User's e-mail address, unique value
    picture: Link to profile picture
    about: Text about  the user, i.e. info about self
    register_date: DateTime of user registration, gets added automatically
    """
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    picture = Column(String(250))
    about = Column(UnicodeText)
    register_date = Column(DateTime(timezone=True), server_default=func.now())
    categories = relationship('Category', back_populates='user')
    items = relationship('Item', back_populates='user')

class Category(Base):
    """Category class for the category table

    Columns:
    id: Primary key, auto-generated, incremental integer
    name: String(100) Name of the category, must be unique for public categories
    description: String(250) Short description of category
    user_id: Foreign key, user.id from user table
    user: Relationship to User table
    items: Items by this user (id)
    add_date: DateTime of addition, auto-generated
    public: Boolean, so that the user can decide whether or not to make a
            category public (private is default)

    The following fields have to be provided: name, user_id, public
    """
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates="categories")
    items = relationship('Item', back_populates="category")
    add_date = Column(DateTime(timezone=True), server_default=func.now())
    public = Column(Boolean, default=False)

    @property
    def serialize(self):
        """Return public categories in serialisable format"""
        if self.public:
            return {
                'name': self.name,
                'description': self.description,
                'add_date':self.add_date,
            }
        else:
            return {
                'public': self.public
            }

    def allow_private(self):
        """Check if category is allowed as private

        Check if category has items other than user's own, if yes, don't
        allow setting it to private"""
        allow = True
        for item in self.items:
            if item.user_id != self.user_id:
                allow = False
        return allow

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
    category = relationship('Category', back_populates="items")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates="items")
    public = Column(Boolean, default=False)

    @property
    def serialize(self):
        """Return public items in serialisable format"""
        if self.public:
            return {
                'link': self.link,
                'title': self.title,
                'artist': self.artist,
                'note': self.note,
                'add_date': self.add_date,
            }
        else:
            return {
                'public': self.public,
            }


engine = create_engine(app.config['DB_URI'],
                       convert_unicode=True)

Base.metadata.create_all(engine)
