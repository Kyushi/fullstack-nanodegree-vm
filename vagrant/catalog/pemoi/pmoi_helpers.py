"""Varous helper functions that do not require a route."""

import random
import string
import json
import re

from flask import make_response
from sqlalchemy.orm.exc import NoResultFound
from pmoi_db_session import db_session
from database_setup import User, Category

# Helper function for returning json
def json_response(response_string, code):
    """Function for generating a json response

    Keyword arguments:
    response_string: String that will be dumped and shown to the user
    code: HTML response code
    """
    response = make_response(json.dumps(response_string), code)
    response.headers['Content-Type'] = 'application/json'
    return response

# Generate a state for oauth
def make_state():
    """Create state parameter for OAuth.

    Return: Random string of ascii letters and digits of length 32.
    """
    return ''.join(random.choice(string.ascii_letters + string.digits)\
                   for x in xrange(32))

# Verify user input
def username_error(username):
    """Verify username.

    Argument: Username as string. Username must be between 5 and 20 characters
        long, contain alphanumeric characters and '.', '-', '_' only. Must be
        unique.
    Return: Error message or None.
    """
    if not (len(username) >= 5 and len(username) <= 20):
        return "Bad length: %d (must be between 5 and 20)" % len(username)
    if not re.match(r'^[\w.-]+$', username):
        return """Illegal characters detected in '%s'.
               Alphanumeric and '.', '_' or '-' only.""" % username
    if get_user_by_username(username):
        return "Username %s is already taken" % username
    print "Username checks out"
    return None

# Get user by username
def get_user_by_username(username):
    """Get user object from database by username.

    Argument: Username as string.
    Return: User object or None.
    """
    try:
        user = db_session.query(User).filter_by(username=username).one()
        return user
    except NoResultFound as err:
        return None

# make sure link is an image
def check_img_link(link):
    """Verify image link.

    Argument: Link as string. Link must end with "jpg", "jpeg", "png" or "gif".
    Return: Link or None.
    """
    allowed_img = ('jpg', 'jpeg', 'png', 'gif')
    if '.' in link:
        splitlink = link.split('.')
        if splitlink[-1].lower() in allowed_img:
            return link
    return None

def get_or_create_cat_zero():
    """Check if a category with ID 0 exists in db, create one if not.

    Category 0 serves as a catchall category in case a user forgets to select a
    category when registering a new item. The category is required as a foreign
    key for item objects.
    """
    try:
        cat_zero = db_session.query(Category).filter_by(id=0).one()
        print "Found cat_zero, continue"
        return cat_zero
    except NoResultFound:
        print "Category not found, creating cat_zero"
        cat_zero = Category(id=0,
                            name="No Category",
                            description="Catchall category for uncategorised \
                                        items",
                            user_id=0,
                            public=True)
        db_session.add(cat_zero)
        db_session.commit()
        print "cat_zero added"
        return cat_zero

def get_or_create_admin():
    """Check if an admin user with id 0 is registered, create if not.

    The admin account is required, so that when a user wants to delete their
    account but they own a public category with other users' items in them,
    this category will not be without user_id (foreign key requirement).
    """
    try:
        admin = db_session.query(User).filter_by(id=0).one()
        print "Admin account exists, show page normally"
        return admin
    except NoResultFound:
        print "No admin found, cerating admin account"
        admin = User(id=0,
                     name="Admin",
                     username="Admin",
                     email="admin@pemoi.com",
                     about="Admin account. Adopts all abandoned categories.",
                     picture="/static/users/admin.jpg")
        db_session.add(admin)
        db_session.commit()
        print "Admin created"
        return admin
