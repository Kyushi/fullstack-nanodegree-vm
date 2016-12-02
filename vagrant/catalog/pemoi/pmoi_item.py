__author__ = 'Akechi'
import os

from flask import flash, \
                  redirect, \
                  render_template, \
                  url_for, \
                  request, \
                  session as login_session, \
                  send_from_directory, \
                  jsonify

from werkzeug.utils import secure_filename

from pemoi import app

from pmoi_db_session import db_session

from database_setup import Item, Category

from pmoi_cat import name_exists

from pmoi_helpers import check_img_link

# set upload folder and allowed extensions for upload

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# File uploads
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# create route to serve uploaded items
@app.route('/<username>/<filename>')
def serve_file_from_folder(username, filename):
    path = os.path.join('static', 'uploads', username)
    return send_from_directory(path, filename)

# JSON endpoint for items
@app.route('/inspiration/<int:item_id>/json/')
def item_json(item_id):
    item = db_session.query(Item).filter_by(id=item_id).one()
    return jsonify(item.serialize)

# Show an individual item
@app.route('/inspiration/<int:item_id>/', methods=['GET', 'POST'])
def show_item(item_id):
    try:
        item = db_session.query(Item).filter_by(id=item_id).one()
    except:
        flash("This item does not exist")
        return redirect('/')
    if item.public or item.user_id == login_session.get('user_id'):
        return render_template('showitem.html', item=item)
    else:
        flash("This item is not public and/or belongs to somebody else.")
        return redirect('/')

# Create a new item
@app.route('/inspiration/new/', methods=['GET', 'POST'])
def new_item():
    if not 'user_id' in login_session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        link = ''
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'],
                                login_session['username'])
            save_path = os.path.join(path, filename)
            file.save(save_path)
            link = os.path.join('/', 'static', 'users', login_session['username'], filename)
        if not link:
            link = check_img_link(request.form.get('link'))
        if request.form['category'] == '0' and request.form['newcategory']:
            public = request.form.get('public-category')
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
            category_id = request.form['category']
        if not link:
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
        flash("Inspiration successfully saved")
        db_session.refresh(item)
        return redirect(url_for('show_item', item_id=item.id))
    else:
        return render_template('newitem.html')


# Edit an item
@app.route('/inspiration/<int:item_id>/edit/', methods=['GET', 'POST'])
def edit_item(item_id):
    if not 'user_id' in login_session:
        return redirect(url_for('login'))
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
        return render_template('edititem.html', item=item)


# delete an item
@app.route('/inspiration/<int:item_id>/delete/', methods=['GET', 'POST'])
def delete_item(item_id):
    if not 'user_id' in login_session:
        return redirect(url_for('login'))
    try:
        item = db_session.query(Item).filter_by(id=item_id).one()
    except:
        flash("This item does not exist")
        return redirect ('/')
    if item.user_id != login_session['user_id']:
        flash("You can only delete your own items!<br>")
        return redirect(url_for('show_item', item_id=item.id))
    if request.method == 'POST':
        delete_file_and_row(item)
        flash("Item %s deleted!" % item.title)
        return redirect('/')
    else:
        return render_template('deleteitem.html',
                               item=item)


def delete_file_and_row(item):
    """Function for deleting item entries from database as well as deleting
    an item's uploaded file if present.

    :param item: An Item instance
    :return: nothing to return
    """
    try:
        filename = item.link.rsplit('/', 1)[1]
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.user.username, filename))
    except:
        pass
    db_session.delete(item)
    db_session.commit()
    return
