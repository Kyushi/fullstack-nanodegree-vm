"""Configuration file"""

import os

_basedir = os.path.abspath(os.path.dirname(__file__))

# Not sure why this is here, TODO: Find out why
DEBUG = False
# This is where my db sits
DB_URI = 'sqlite:///' + os.path.join(_basedir, 'pemoi.db')
# This is so secret you don't even know about it
SECRET_KEY = "askjbio3g4owiebtUH!?27gsAEG"
# This is the folder in which users' folders are created
UPLOAD_FOLDER = os.path.join(_basedir,'pemoi', 'static', 'users')
# This makes sure that no files larger than 10MB are uploaded
MAX_CONTENT_LENGTH = 10 * 1024 * 1024
