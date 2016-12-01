__author__ = 'Akechi'
import os

from flask import session as login_session, \
                  render_template, \
                  request, \
                  flash, \
                  redirect

from pemoi import app

from pmoi_helpers import make_state
# imports to connect to database and create User instances
from pmoi_db_session import db_session
from pmoi_helpers import username_error
from database_setup import User

from googleoauth import gdisconnect
from fboauth import fbdisconnect
from config import UPLOAD_FOLDER


### User signup/login ###

# Create user entry
def create_user():
    user = User(name=login_session['name'],
                username=login_session['username'],
                email=login_session['email'],
                picture=login_session.get('picture'),
                about=login_session.get('about'))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user.id

# Get user id by email
def get_user_id(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Get user info
def get_user_info(user_id):
    """


    :rtype : object
    :param user_id:
    :return:
    """
    user = db_session.query(User).filter_by(id=user_id).one()
    return user



# Login page, creates state
@app.route('/login/', methods=['GET', 'POST'])
def login():
    login_session.clear()
    state = make_state()
    login_session['state'] = state
    return render_template('login.html', STATE = state)

@app.route('/completesignup/', methods=['GET', 'POST'])
def complete_signup():
    if request.method == 'POST':
        username = request.form.get('username')
        about = request.form['about']
        error = username_error(username)
        if error:
            flash(error)
            return render_template('signup.html',
                                   username=username,
                                   about=about)
        if 'email' in request.form:
            login_session['email'] = request.form['email']
        if not username_error(username):
            print username
            login_session['username'] = username
            login_session['about'] = about
            # Create user in db and receive new user ID
            user_id = create_user()
            # store user ID in db_session
            login_session['user_id'] = user_id
            # finally, if everything is okay, create a user directory for uploads
            os.mkdir(os.path.join(UPLOAD_FOLDER, username))
            flash("Welcome to your Personal Museum of Inspiration, %s" % login_session['username'])
            return redirect('index')

    else:
        return render_template('signup.html')

@app.route('/logout/')
def logout():
    provider = login_session['provider']
    if provider == 'Google':
        gdisconnect()
    elif provider == 'Facebook':
        fbdisconnect()
    login_session.clear()
    flash("You have been logged out. Come back soon!")
    return redirect('/')

@app.route('/privacy/')
def privacy():
    return "This will be information about data we store."
