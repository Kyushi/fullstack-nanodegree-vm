"""Module for all pages regarding items."""
import os

import json
from flask import flash, \
                  redirect, \
                  render_template, \
                  url_for, \
                  request, \
                  session as login_session, \
                  send_from_directory

from werkzeug.utils import secure_filename
from pemoi import app
from database_setup import Item, Category
from db_session import db_session
from category import name_exists
from helpers import check_img_link, json_serial, login_required

# set allowed extensions for upload
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    """Check if an uploaded file has allowed filetype.

    Argument: Filename as string.
    Return: Boolean
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# JSON endpoint for items
@app.route('/inspiration/<int:item_id>/json/')
def item_json(item_id):
    """Provide JSON endpoint for an individual item."""
    item = db_session.query(Item).filter_by(id=item_id).one()
    return json.dumps(item.serialize,
                      default=json_serial,
                      sort_keys=True,
                      indent=4)

# Show an individual item
@app.route('/inspiration/<int:item_id>/', methods=['GET', 'POST'])
def show_item(item_id):
    """Show individual item."""
    try:
        item = db_session.query(Item).filter_by(id=item_id).one()
    except:
        flash("This item does not exist")
        return redirect('/')
    # Make sure that user is authorised to see the item
    if item.public or item.user_id == login_session.get('user_id'):
        return render_template('itemshow.html', item=item)
    else:
        flash("This item is not public and belongs to somebody else.")
        return redirect('/')

# Create a new item
@app.route('/inspiration/new/', methods=['GET', 'POST'])
@login_required
def new_item():
    """Create a new item.

    Logged in users can create new items. Items can be image links or uploaded
    image files.
    """
    if request.method == 'POST':
        link = ''
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'],
                                login_session['username'])
            save_path = os.path.join(path, filename)
            file.save(save_path)
            link = os.path.join('/',
                                'static',
                                'users',
                                login_session['username'],
                                filename)
        # 'link' will be empty if no file was uploaded. In that case, the user
        # should provide an image link.
        if not link:
            link = check_img_link(request.form.get('link'))
        # Check if user has entered a new category name.
        if request.form['category'] == '0' and request.form['newcategory']:
            public = request.form.get('public-category')
            # Make sure that the new category name is not double if category is
            # public.
            if public and name_exists(request.form['newcategory']):
                # Submit is disabled and an error shown via ajax, but we keep
                # this just in case
                return "This public category exists already"
            category = Category(name=request.form['newcategory'],
                                user_id=login_session['user_id'],
                                public=True if public else False)
            db_session.add(category)
            db_session.commit()
            db_session.refresh(category)
            category_id = category.id
        else:
            # If no new category was provided, use the ID from the drop down.
            category_id = request.form['category']
        if not link:
            # If the user does not provide a link or upload an image, they have
            # to try again.
            flash("You have to add a link or upload an image")
            return redirect(url_for('new_item'))
        item = Item(link=link,
                    title=request.form['title'],
                    artist=request.form['artist'],
                    note=request.form['note'],
                    keywords=request.form['keywords'],
                    category_id=category_id,
                    user_id=login_session['user_id'],
                    public=True if request.form.get('public') else False
                    )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        flash("Inspiration successfully saved")
        return redirect(url_for('show_item', item_id=item.id))
    else:
        return render_template('itemnew.html')


# Edit an item
@app.route('/inspiration/<int:item_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    """Edit an item's properties.

    The item's owner can change an item's title, artist name, keywords, user
    note and category, and toggle between public and private.
    """
    try:
        item = db_session.query(Item).filter_by(id=item_id).one()
    except:
        flash("This item does not exist")
        return redirect('/')
    if request.method == 'POST' and item.user_id == login_session['user_id']:
        item.title = request.form['title']
        item.artist = request.form['artist']
        item.note = request.form['note']
        item.keywords = request.form['keywords']
        item.category_id = request.form['category']
        item.user_id = login_session['user_id']
        item.public = True if request.form.get('public') else False
        db_session.add(item)
        db_session.commit()
        flash("Inspiration successfully saved")
        db_session.refresh(item)
        return redirect(url_for('show_item', item_id=item.id))
    else:
        return render_template('itemedit.html', item=item)


# delete an item
@app.route('/inspiration/<int:item_id>/delete/', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    """Delete an item.

    A user can delete their own items.
    """
    try:
        item = db_session.query(Item).filter_by(id=item_id).one()
    except:
        flash("This item does not exist")
        return redirect ('/')
    if item.user_id != login_session['user_id']:
        flash("You can only delete your own items!<br>")
        return redirect(url_for('show_item', item_id=item.id))
    if request.method == 'POST':
        # The actual item deletion is handled via another function.
        delete_file_and_row(item)
        flash("Item %s deleted!" % item.title)
        return redirect('/')
    else:
        return render_template('itemdelete.html',
                               item=item)


def delete_file_and_row(item):
    """Function for deleting item entries from database as well as deleting
    an item's uploaded file if present.

    Argument: An Item object.
    """
    try:
        # The item name is saved in the link as a path.
        filename = item.link.rsplit('/', 1)[1]
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'],
                               item.user.username,
                               filename))
    except:
        pass
    db_session.delete(item)
    db_session.commit()
