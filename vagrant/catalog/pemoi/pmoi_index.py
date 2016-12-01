__author__ = 'Akechi'
from flask import session as login_session, \
                  render_template

from sqlalchemy import desc

from pemoi import app
from database_setup import Category, Item

from pmoi_db_session import db_session
from pmoi_helpers import get_or_create_cat_zero, get_or_create_admin

@app.route('/')
@app.route('/index/')
def index():
    user_id = login_session.get("user_id")
    get_or_create_admin()
    get_or_create_cat_zero()
    try:
        items = db_session.query(Item).filter((Item.public==True)| (Item.user_id==user_id)).order_by(desc(Item.add_date)).all()
    except:
        items = None
    return render_template('index.html', items=items)
