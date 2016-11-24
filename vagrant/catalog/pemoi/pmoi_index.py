__author__ = 'Akechi'
from flask import session as login_session, \
                  render_template

from sqlalchemy import desc

from pmoi_db_session import db_session

from database_setup import Category, Item

from pemoi import app

@app.route('/')
@app.route('/index/')
def index():
    user_id = login_session.get("user_id")
    try:
        categories = db_session.query(Category).filter((Category.public==True)| (Category.user_id==user_id)).all()
        items = db_session.query(Item).filter((Item.public==True)| (Item.user_id==user_id)).order_by(desc(Item.add_date)).all()
    except:
        categories = None
        items = None
    return render_template('index.html', categories=categories, items=items)