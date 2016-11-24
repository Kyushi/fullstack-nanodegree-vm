__author__ = 'Akechi'
from flask import session as login_session, render_template
from pmoi_db_session import db_session
from pemoi import app
from database_setup import Item

### TODO: Remove before going live! not for production ###
# Force clear old db_session
@app.route('/clearSession')
def clearSession():
    login_session.clear()
    return "Session cleared"

# helper page to show db_session details
@app.route('/login_session/')
def show_session():
    return render_template('db_session.html')

@app.route('/allitems/')
def show_all_items():
    items = db_session.query(Item).all()
    return render_template('showallitems.html', items=items)
### ---------- ###