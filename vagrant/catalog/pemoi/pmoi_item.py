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

@app.route('/inspiration/<int:item_id>/json/')
def item_json(item_id):
    item = db_session.query(Item).filter_by(id=item_id).one()
    print item.id
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
        print "Something was POSTed"
        link = ''
        file = request.files['file']
        print "File found: %s" % file.filename
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print filename
            path = os.path.join(app.config['UPLOAD_FOLDER'],
                                login_session['username'])
            save_path = os.path.join(path, filename)
            file.save(save_path)
            print "File saved at %s" % save_path
            link = os.path.join('/', 'static', 'users', login_session['username'], filename)
            print "Link: %s" % link
        if not link:
            link = check_img_link(request.form.get('link'))
        if request.form['category'] == '0' and request.form['newcategory']:
            public = request.form.get('public-category')
            if name_exists(request.form['newcategory'], public):
                return "This public category exists already"
            category = Category(name=request.form['newcategory'],
                                user_id=login_session['user_id'],
                                public=True if public else False)
            db_session.add(category)
            db_session.commit()
            db_session.refresh(category)
            category_id = category.id
            print "Category ID: %s, Category name: %s" % (category_id, category.name)
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
        print "Item populated"
        db_session.add(item)
        print "Item added"
        db_session.commit()
        print "Session committed"
        flash("Inspiration successfully saved")
        db_session.refresh(item)
        return redirect(url_for('show_item', item_id=item.id))
    else:
        categories = db_session.query(Category).filter((Category.public==True)|(Category.user_id==login_session['user_id']))
        return render_template('newitem.html', categories=categories)


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
        item.link = request.form['link']
        item.title = request.form['title']
        item.artist = request.form['artist']
        item.note = request.form['note']
        item.keywords = request.form['keywords']
        item.category_id = request.form['category']
        item.user_id = login_session['user_id']
        item.public = True if request.form.get('public') else False
        db_session.add(item)
        print "Item edited"
        db_session.commit()
        print "Session committed"
        flash("Inspiration successfully saved")
        db_session.refresh(item)
        return redirect(url_for('show_item', item_id=item.id))
    else:
        categories = db_session.query(Category).filter((Category.public==True)|(Category.user_id==login_session['user_id']))
        return render_template('edititem.html', categories=categories, item=item)


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
    item_title = item.title
    if item.user_id != login_session['user_id']:
        flash("You can only delete your own items!<br>")
        return redirect(url_for('show_item', item_id=item_id))
    if request.method == 'POST':
        delete_file_and_row(item)
        flash("Item %s deleted!" % item_title)
        return redirect('/')
    else:
        return render_template('deleteitem.html', item_title=item_title)


def delete_file_and_row(item):
    """Function for deleting item entries from database as well as deleting
    an item's uploaded file if present.

    :param item: An Item instance
    :return: nothing to return
    """
    try:
        filename = item.link.rsplit('/', 1)[1]
        print filename
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.user.username, filename))
        print "Item removed!"
    except:
        print "No item to remove, %s %s" % (item.id, item.link)
        pass
    db_session.delete(item)
    db_session.commit()
    return