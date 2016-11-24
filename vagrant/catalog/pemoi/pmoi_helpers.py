import random
import string
import json

from flask import make_response

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
    return ''.join(random.choice(string.ascii_letters + string.digits) for x in xrange(32))

# Verify user input
def verify_username(username, users):
    usernames = [user.username for user in users]
    if not username or username in usernames:
        return False
    if len(username) < 5 or len(username) > 50:
        return False
    return True

# make sure link is an image
def check_img_link(link):
    allowed_img = ('jpg', 'jpeg', 'png', 'gif')
    if '.' in link:
        splitlink = link.split('.')
        print splitlink, splitlink[-1].lower()
        if splitlink[-1].lower() in allowed_img:
            return link
    return None
