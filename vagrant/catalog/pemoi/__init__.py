"""Init file for package. Create flask app."""
from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

import pemoi.authentication
import pemoi.category
import pemoi.fboauth
import pemoi.githuboauth
import pemoi.googleoauth
import pemoi.index
import pemoi.item
import pemoi.user
import pemoi.helpers

# Make sure that admin and category 0 exist when starting the app.
admin = pemoi.helpers.get_or_create_admin()
cat_zero = pemoi.helpers.get_or_create_cat_zero()

@app.context_processor
def categories_for_menu():
    return dict(categories=pemoi.category.get_categories())
