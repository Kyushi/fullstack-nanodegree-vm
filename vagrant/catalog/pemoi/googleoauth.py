"""Google OAuth authentication"""

import requests
import json
import httplib2

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from flask import request, \
                  flash, \
                  session as login_session

from pemoi import app
from pmoi_helpers import json_response, make_response
import pmoi_auth

# Connect with Google+
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connect with Google Oauth API"""

    CLIENT_ID = json.loads(open('google_client_secrets.json','r').read())['web']['client_id']
    if request.args.get('state') != login_session['state']:
        response = "Invalid STATE parameter"
        return json_response(response, 401)
    # Obtain auth code
    code = request.data
    try:
        # Upgrade the auth code into a credentials object
        oauth_flow = flow_from_clientsecrets('google_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = 'Failed to upgrade the auth code to credentials object'
        return json_response(response, 401)

    # Check that access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there is an error in the result, abort mission
    if result.get('error') is not None:
        response = result.get('error')
        return json_response(response, 500)

    # Verify that the token is for this user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = 'User ID in token does not match user id'
        return json_response(response, 401)

    # Verify client ID
    if result['issued_to'] != CLIENT_ID:
        response = 'Client ID does not match'
        return json_response(response, 401)

    #Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and stored_gplus_id == gplus_id:
        response = make_response(json.dumps(
                                 'Current user is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store credentials for usage
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user Information
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    # Receive user information from google's api
    data = answer.json()

    # Store interesting stuff in my db_session
    login_session['provider'] = 'Google'
    login_session['name'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check if user exists in database
    user_id = pmoi_auth.get_user_id(login_session['email'])
    if not user_id:
        return "new"
    # If yes, get user info from db and welcome user, redirect handled by js
    user = pmoi_auth.get_user_info(user_id)
    login_session['user_id'] = user.id
    login_session['username'] = user.username
    flash("Thanks for logging in, %s" % login_session['username'])
    return user.username

# User logout /disconnect Google Plus
@app.route('/gdisconnect')
def gdisconnect():
    """Revoke Google OAuth access token"""
    access_token = login_session.get('access_token')
    if access_token is None:
        response = 'No user connected'
        return json_response(response, 401)
    # Revoke current token by http get request
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        # If token was invalid
        response = "Failed to revoke token for given user"
        return json_response(response, 400)
