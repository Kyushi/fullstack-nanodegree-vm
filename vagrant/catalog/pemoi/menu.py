__author__ = 'Akechi'

from pmoi_db_session import db_session

from pemoi import app

from database_setup import Category

from flask import render_template, url_for

@app.route("/menu")
def menu():
    print "Menu gets called"
    categories = db_session.query(Category).filter_by(public=True).all()
    return render_template('menu.html', categories=categories)
