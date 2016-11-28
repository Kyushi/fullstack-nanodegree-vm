__author__ = 'Akechi'
import json
import urllib
import httplib2

from pemoi import app

from flask import request, \
                  session as login_session, \
                  flash, \
                  redirect, \
                  url_for

from pmoi_auth import get_user_info, get_user_id

from pmoi_db_session import db_session


# Connect with github
@app.route('/githubconnect', methods=['GET', 'POST'])
def githubconnect():
    # Receive state from github
    state = request.args.get('state')
    # If state is not identical to db_session state, return error TODO: proper redirect
    if state != login_session['state']:
        response = "Your state is not my state"
        return response
    # Code is received from github
    code = request.args.get('code')
    # Load client id and secret from file
    client_id = json.loads(open('github_client_secrets.json', 'r').read())['web']['client_id']
    client_secret = json.loads(open('github_client_secrets.json', 'r').read())['web']['client_secret']
    # Get parameters ready for requesting access token
    params = {'code': code, 'client_id': client_id, 'client_secret': client_secret, 'state':state}
    # Set headers to receive json encoded data
    headers = {'Accept':'application/json'}
    url = 'https://github.com/login/oauth/access_token'
    # Get response with access_token or error from github
    h = httplib2.Http()
    response = h.request(url, 'POST', urllib.urlencode(params), headers=headers)
    # Read the actual result from the response
    result = json.loads(response[1])
    # Let the user know if there was an error TODO: proper return
    if 'error' in result:
        return "There was a problem: %s" % result['error']
    # get the access token
    access_token = result['access_token']
    #prepare headers with token
    headers = {'Authorization': 'token %s' % access_token}
    # get user data with access_token
    url = 'https://api.github.com/user'
    response, content = h.request(url, 'GET', headers=headers)
    status = response.status
    if status != 200:
        return "There was a problem %s" % json.loads(content)['message']
    result = json.loads(content)
    login_session['provider'] = 'Github'
    login_session['name'] = result['name']
    login_session['picture'] = result['avatar_url']
    login_session['access_token'] = access_token
    # get user e-mail with access_token
    url = 'https://api.github.com/user/emails'
    response, content = h.request(url, 'GET', headers=headers)
    status = response.status
    if status != 200:
        return "There was a problem %s" % json.loads(content)['message']
    # get list of non public e-mail addresses
    emails = json.loads(content)
    # Check if user exists in db
    email_addresses = [e['email'] for e in emails]
    login_session['emails'] = email_addresses
    for e in emails:
        if e['primary']:
            login_session['email'] = e['email']
        user_id = get_user_id(e['email'])
        if user_id:
            user = get_user_info(user_id)
            login_session['email'] = e['email']
            login_session['username'] = user.username
            login_session['user_id'] = user_id
            user.picture = login_session['picture']
            db_session.add(user)
            db_session.commit()
            flash("Thanks for logging in, %s" % login_session['username'])
            return redirect('/')
    login_session['emails'] = email_addresses
    return redirect(url_for('complete_signup'))
