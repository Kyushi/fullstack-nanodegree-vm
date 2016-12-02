from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

import pemoi.menu
import pemoi.pmoi_auth
import pemoi.pmoi_cat
import pemoi.debugpages
import pemoi.fboauth
import pemoi.githuboauth
import pemoi.googleoauth
import pemoi.pmoi_index
import pemoi.pmoi_item
import pemoi.pmoi_user
import pemoi.pmoi_helpers

admin = pemoi.pmoi_helpers.get_or_create_admin()
cat_zero = pemoi.pmoi_helpers.get_or_create_cat_zero()

@app.context_processor
def categories_for_menu():
    return dict(categories=pemoi.pmoi_cat.get_categories())
