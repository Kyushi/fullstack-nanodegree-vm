"""Index module. Render the index page."""

from flask import session as login_session, \
                  render_template

from sqlalchemy import desc

from pemoi import app
from database_setup import Item
from pmoi_db_session import db_session

@app.route('/')
@app.route('/index/')
def index():
    """Render index page with all public items.

    If user session exists, user's private items will be displayed as well.
    """
    user_id = login_session.get("user_id")
    try:
        items = db_session.query(Item).filter(\
                                (Item.public==True)| (Item.user_id==user_id)).\
                                order_by(desc(Item.add_date)).all()
    except:
        # Make sure that there is something to be passed to the template.
        items = None
    return render_template('index.html', items=items)
