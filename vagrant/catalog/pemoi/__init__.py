from flask import Flask

app = Flask(__name__)

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