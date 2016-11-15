import httplib2
import json
import requests

from flask import Flask, \
                  request, \
                  render_template, \
                  redirect, \
                  url_for, \
                  jsonify, \
                  flash, \
                  session as login_session

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from database_setup import Base, \
                           User, \
                           Category, \
                           Item

# import helpers
from helpers import json_response, \
                    make_state

# import secret
from secret import SECRET

# Connect to database and create session
engine = create_engine('sqlite:///pemoi.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create app and tell it the secret
app = Flask(__name__)
app.secret_key = SECRET


# TODO: Make sure that each page with an id renders an error if the id does not
# exist. Redirect to a meaningful page and show flash message

### User signup/login ###

# Create user entry
def create_user(login_session):
    user = User(name=login_session['name'],
                username=login_session['username'],
                email=login_session['email'],
                picture=login_session.get('picture'),
                about=login_session.get('about'))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user.id

# Get user id by email
def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Get user info
def get_user_info(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# Get user categories
def get_user_categories(user_id, public=False):
    return session.query(Category).filter((Category.user_id==user_id)&(Category.public==public)).all()

# Get user items
def get_user_items(user_id):
    return session.query(Item).filter_by(user_id=user_id).all()

### TODO: Remove before going live! not for production ###
# Force clear old session
@app.route('/clearSession')
def clearSession():
    login_session.clear()
    return "Session cleared"

# helper page to show session details
@app.route('/login_session/')
def show_session():
    return render_template('session.html')

@app.route('/allitems/')
def show_all_items():
    items = session.query(Item).all()
    return render_template('showallitems.html', items=items)
### ---------- ###

@app.route('/')
@app.route('/index/')
def index():
    user_id = login_session.get("user_id")
    try:
        categories = session.query(Category).filter((Category.public==True)| (Category.user_id==user_id)).all()
        items = session.query(Item).filter((Item.public==True)| (Item.user_id==user_id)).order_by(desc(Item.add_date)).all()
    except:
        categories = None
        items = None
    return render_template('index.html', categories=categories, items=items)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    state = make_state()
    login_session['state'] = state
    return render_template('login.html', STATE = state)

# Connect with Google+
@app.route('/gconnect', methods=['POST'])
def gconnect():
    CLIENT_ID = json.loads(open('google_client_secrets.json','r').read())['web']['client_id']
    print "Starting login process"
    if request.args.get('state') != login_session['state']:
        response = "Invalid STATE parameter"
        return json_response(response, 401)
    # Obtain auth code
    code = request.data
    print "Received code %s" % code
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
    print "Token is valid"

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
    print "Checking if user is logged in"
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and stored_gplus_id == gplus_id:
        response = make_response(json.dumps(
                                 'Current user is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store credentials for usage
    print "Storing credentials"
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user Information
    print "Retrieving user info"
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    # Receive user information from google's api
    data = answer.json()
    print "Received %s" % data

    # Store interesting stuff in my session
    print "Storing info in login session"
    login_session['provider'] = 'Google'
    login_session['name'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check if user exists in database
    user_id = get_user_id(login_session['email'])
    print "Found user: %s" % user_id
    if not user_id:
        print "New user"
        return "new"
    # If yes, get user info from db and welcome user, redirect handled by js
    user = get_user_info(user_id)
    login_session['user_id'] = user.id
    login_session['username'] = user.username
    flash("Thanks for logging in, %s" % login_session['username'])
    return user.username

# User logout /disconnect Google Plus
@app.route('/gdisconnect')
def gdisconnect():
    # Disconnect a logged in user
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

# Connect with Facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
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
    print "First result after exchanging access_token for server token: %s" % result

    # Use token to get user info
    userinfo_url = 'https://graph.facebook.com/v2.8/me'
    # strip expire tag from token
    token = result.split('&')[0]
    print "Server side token: %s" % token
    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print "Retrieved user info \n Result: %s\nResult type: %s" % (result, type(result))
    data = json.loads(result)
    login_session['provider'] = 'Facebook'
    login_session['name'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    # Get profile picture in separate call
    url = 'https://graph.facebook.com/v2.8/me/picture?%s&redirect=0&height=200&width=200' % token
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']
    print login_session['picture']
    # Check if user exists in db
    user_id = get_user_id(login_session['email'])
    # if not, make js redirect to comeplete signup
    if not user_id:
        print "No user id found, creating new user"
        return "new"
    # If yes, get user info from db and welcome user, redirect handled by js
    user = get_user_info(user_id)
    login_session['user_id'] = user.id
    login_session['username'] = user.username
    flash("Thanks for logging in, %s" % login_session['username'])
    return user.username

# Facebook disconnect function
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You've been logged out"

@app.route('/completesignup/', methods=['GET', 'POST'])
def complete_signup():
    if request.method == 'POST':
        login_session['username'] = request.form['username']
        login_session['about'] = request.form['about']
        user_id = create_user(login_session)
        login_session['user_id'] = user_id
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

@app.route('/profile/<int:user_id>/')
def show_profile(user_id):
    user = get_user_info(user_id)
    return render_template('profile.html', user=user)

@app.route('/profile/<int:user_id>/edit/', methods=['GET', 'POST'])
def edit_profile(user_id):
    if 'user_id' not in login_session:
        return redirect('/login')
    if user_id != login_session['user_id']:
        flash("You can only edit your own profile")
        return redirect(url_for('show_profile', user_id=user_id))
    user = get_user_info(user_id)
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        picture = request.form['picture']
        about = request.form['about']
        email = request.form['email']
        user.name = name
        user.username = username
        user.picture = picture
        user.about = about
        user.email = email
        login_session['name'] = name
        login_session['username'] = username
        login_session['picture'] = picture
        login_session['email'] = email
        session.add(user)
        session.commit()

        return redirect(url_for('show_profile', user_id=user.id))
    else:
        return render_template('editprofile.html', user=user)

@app.route('/profile/<int:user_id>/delete/', methods=['GET', 'POST'])
def delete_profile(user_id):
    if not 'user_id' in login_session:
        return redirect(url_for('login'))
    if user_id != login_session["user_id"]:
        flash("You can only delete your own profile.")
        return redirect(url_for('index'))
    user = get_user_info(user_id)
    items = get_user_items(user_id)
    private_categories = get_user_categories(user_id, False)
    if request.method == 'POST':
        for item in items:
            session.delete(item)
        for cat in private_categories:
            session.delete(cat)
        session.delete(user)
        session.commit()
        flash("We are crying bitter tears to see you leaving. Please come back one day.")
        return redirect(url_for('logout'))
    else:
        return render_template('deleteprofile.html', user=user, categories=private_categories, items=items)


@app.route('/category/<int:category_id>/')
def show_category(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        flash("This category does not exist yet")
        return redirect('/')
    if category.public or category.user_id==login_session['user_id']:
        print "Querying for items"
        items = session.query(Item).filter(Item.category_id==category.id, Item.public==True).all()
        print "Query successful. Items found: %s" % len(items)
        return render_template('showcategory.html', category=category, items=items)
    else:
        flash('This is a private category')
        return redirect('/')

@app.route('/category/new/', methods=['GET', 'POST'])
def new_category():
    if 'user_id' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        print "POST method for new category"
        public = True if request.form.get('public') else False
        print public
        category = Category(name=request.form['name'],
                            description=request.form['description'],
                            user_id=login_session['user_id'],
                            public=public)
        session.add(category)
        print "Category added"
        session.commit()
        print "Session committed"
        session.refresh(category)
        print "ID: %s\nName: %s\nDescription: %s\nPublic: %s" % (category.id, category.name, category.description, category.public)
        return redirect(url_for('show_category', category_id=category.id))
    else:
        return render_template('newcategory.html')

@app.route('/category/<int:category_id>/edit/', methods={'GET', 'POST'})
def edit_category(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        flash("This category does not exist yet")
        return redirect('/')
    if 'user_id' not in login_session:
        flash("Please log in to edit categories.")
        return redirect('/login')
    elif login_session['user_id'] != category.user_id:
        flash("You can only edit categories that you have created yourself")
        return redirect("/category/%s" % category_id)
    else:
        if request.method == 'POST':
            category.name = request.form['name']
            category.description = request.form['description']
            category.public = True if request.form.get('public') else False
            session.add(category)
            session.commit()
            return redirect("/category/%s" % category_id)
        else:
            return render_template('editcategory.html', category=category)

@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def delete_category(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        flash("This category does not exist yet")
        return redirect('/')
    if 'user_id' not in login_session:
        flash("Please log in to delete categories.")
        return redirect('/login')
    elif login_session['user_id'] != category.user_id:
        flash("You can only delete categories that you have created yourself")
        return redirect("/category/%s" % category_id)
    # TODO: check if category has items and don't allow deletion
    else:
        if request.method == 'POST':
            session.delete(category)
            session.commit()
            return redirect('/')
        else:
            return render_template('deletecategory.html', category=category)

@app.route('/inspiration/<int:item_id>/', methods=['GET', 'POST'])
def show_item(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if item.public or item.user_id == login_session.get('user_id'):
        return render_template('showitem.html', item=item)
    else:
        flash("This item is not public and/or belongs to somebody else.")
        return redirect('/')

@app.route('/inspiration/new/', methods=['GET', 'POST'])
def new_item():
    if not 'user_id' in login_session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        print "POST request received"
        item = Item(link=request.form['link'],
                    title=request.form['title'],
                    artist=request.form['artist'],
                    note=request.form['note'],
                    keywords=request.form['keywords'],
                    category_id=request.form['category'],
                    user_id=login_session['user_id'],
                    public=True if request.form.get('public') else False
                    )
        print "Item populated"
        session.add(item)
        print "Item added"
        session.commit()
        print "Session committed"
        flash("Inspiration successfully saved")
        session.refresh(item)
        return redirect(url_for('show_item', item_id=item.id))
    else:
        categories = session.query(Category).filter((Category.public==True)|(Category.user_id==login_session['user_id']))
        return render_template('newitem.html', categories=categories)

@app.route('/inspiration/<int:item_id>/edit/', methods=['GET', 'POST'])
def edit_item(item_id):
    if not 'user_id' in login_session:
        return redirect(url_for('login'))
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST' and item.user_id == login_session['user_id']:
        item.link = request.form['link']
        item.title = request.form['title']
        item.artist = request.form['artist']
        item.note = request.form['note']
        item.keywords = request.form['keywords']
        item.category_id = request.form['category']
        item.user_id = login_session['user_id']
        item.public = True if request.form.get('public') else False
        session.add(item)
        print "Item added"
        session.commit()
        print "Session committed"
        flash("Inspiration successfully saved")
        session.refresh(item)
        return redirect(url_for('show_item', item_id=item.id))
    else:
        categories = session.query(Category).filter((Category.public==True)|(Category.user_id==login_session['user_id']))
        return render_template('edititem.html', categories=categories, item=item)

@app.route('/inspiration/<int:item_id>/delete/', methods=['GET', 'POST'])
def delete_item(item_id):
    if not 'user_id' in login_session:
        return redirect(url_for('login'))
    item = session.query(Item).filter_by(id=item_id).one()
    item_title = item.title
    if item.user_id != login_session['user_id']:
        flash("You can only delete your own items!<br>")
        return redirect(url_for('show_item', item_id=item_id))
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item %s deleted!" % item_title)
        return redirect('/')
    else:
        return render_template('deleteitem.html', item_title=item_title)

# Start app
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
