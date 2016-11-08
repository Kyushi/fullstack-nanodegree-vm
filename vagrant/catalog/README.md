# SO HUNGRY! #

_Project with simple python web server_

___
## Description ##

Simple web server that hosts a website to manage a list of restaurants and their menus.

### Technology ##
* Python 2.7
* SQLite
* Flask
* SQLAlchemy

---
## Requirements ##
* Files: `database_setup.py`, `finalProject.py`, `lotsofmenus.py`, `/templates/`, `/static/`
* Python 2.7.6+
* Web browser

### Dependencies ###

* SQLalchemy
___

## Quickstart ##

1. Open command line tool
* run `python database_setup.py` to create `restaurantmenu.db` SQLita database
* run `python lotsofmenus.py` to populate `restaurantmenu.db` with testing data
* create file `secret.py` with constant `SECRET='yoursecret'` in the repo folder
* run `python finalProject.py` to start flask app on `0.0.0.0:5000`
* enter `0.0.0.0:5000` in your browser's address bar to open the website

Now you can browse the restaurants and their menus, add, edit and delete, restaurants, and add, edit and delete restaurants' menu items.
