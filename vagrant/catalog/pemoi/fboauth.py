"""Facebook OAuth authentication"""

import httplib2
import json

from flask import request, \
                  session as login_session, \
                  flash

from pemoi import app

from pmoi_helpers import json_response

import pmoi_auth

# Connect with Facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Connect to facebook OAuth API"""

    # Compare and validate STATE parameter, return error if invalid
    if request.args.get('state') != login_session['state']:
        response = "Invalid STATE parameter"
        return json_response(response, 401)

    access_token = request.data

    # Exchange client token for long-lived server side token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app-id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app-secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info
    userinfo_url = 'https://graph.facebook.com/v2.8/me'
    # Strip expire tag from token
    token = result.split('&')[0]
    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    # Store user info in session
    login_session['provider'] = 'Facebook'
    login_session['name'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    # Get profile picture in separate call
    url = 'https://graph.facebook.com/v2.8/me/picture?%s&redirect=0&height=200&width=200' % token
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']
    # Check if user exists in db
    user_id = pmoi_auth.get_user_id(login_session['email'])
    # if not, redirect to complete signup
    if not user_id:
        return "new"
    # If yes, get user info from db and welcome user, redirect handled by js
    user = pmoi_auth.get_user_info(user_id)
    login_session['user_id'] = user.id
    login_session['username'] = user.username
    flash("Thanks for logging in, %s" % login_session['username'])
    return user.username

# Facebook disconnect function
@app.route('/fbdisconnect')
def fbdisconnect():
    """Disconnect facebook session"""
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You've been logged out"
