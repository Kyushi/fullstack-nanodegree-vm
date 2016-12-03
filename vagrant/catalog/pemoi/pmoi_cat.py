"""Module to handle all things category."""

from flask import flash, \
                  render_template, \
                  redirect, \
                  request, \
                  url_for, \
                  session as login_session, \
                  jsonify

from database_setup import Category, Item
from pmoi_db_session import db_session
from pemoi import app

### Helpers for categories

# Check category name
def name_exists(name, id=-1):
    """Check if category name exists in db.

    Arguments: name as String, optional id as Integer
    Public categories are not allowed to appear more than once. Private
    categories can be duplicates.
    """
    try:
        c = db_session.query(Category).filter(Category.name==name,\
            Category.public==True, Category.id!=id).one()
    except:
        c = None
    if c:
        return True
    return False

def get_categories(only_own=False):
    """Get categories from database.

    Gets passed as context_processor for use in menu and otherwise.
    Returns: List of Category objects. Categories are public, public and private
    or only own. Categories must have id > 0 because category with ID 0 is the
    "No Category" catchall.
    """
    user_id = login_session.get('user_id')
    if not user_id:
        return db_session.query(Category).filter(Category.public==True,
                                                 Category.id > 0).all()
    # Return only the owner's categories
    if only_own:
        return db_session.query(Category).filter_by(user_id=user_id).all()
    # Return public and owner's private categories
    return db_session.query(Category).filter(
                           (Category.public==True)|
                           (Category.user_id==login_session['user_id']),
                           Category.id > 0
                           ).all()


# JSON endpoints
@app.route('/category/<int:category_id>/json/')
def category_json(category_id):
    """Return a category in JSON format"""
    items = db_session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(CategoryItems = [i.serialize for i in items])

@app.route('/categories/json/')
def categories_json():
    """Return all public categories in JSON format"""
    categories = db_session.query(Category).all()
    return jsonify(Categories = [c.serialize for c in categories])

# Routes

# Route for ajax check
@app.route('/checkcatname', methods=['POST'])
def check_catname():
    """Check that no public category name is double"""
    data = request.json
    catname = request.json['catname']
    catid = request.json.get('catid', -1)
    double = name_exists(catname, int(catid))
    if double:
        return "Bad category name"
    return "OK"

@app.route('/categories/')
def show_categories():
    """Show all categories"""
    return render_template('categories.html')

@app.route('/inspiration/myinspirations/')
def show_own():
    """Show user's own categories."""
    if not 'user_id' in login_session:
        flash("Please log in to view your items")
        return redirect(url_for('login'))
    items = db_session.query(Item).filter_by(user_id=login_session['user_id'])\
            .all()
    return render_template('index.html', items=items)


@app.route('/category/<int:category_id>/')
def show_category(category_id):
    """Show one category.

    Checks for user ID to ensure that a user can only see their own private
    categories.
    """
    user_id = login_session.get('user_id')
    try:
        category = db_session.query(Category).filter_by(id=category_id).one()
    except:
        flash("Category does not exist or is private")
        return redirect(url_for('index'))
    if not (category.public or category.user_id == user_id):
        flash("Category does not exist or is private")
        return redirect(url_for('index'))
    items = db_session.query(Item).filter(\
                                (Item.category_id==category.id)\
                                &((Item.public==True)\
                                |(Item.user_id==user_id)))\
                                .all()
    return render_template('showcategory.html',
                            category=category,
                            items=items)

@app.route('/category/new/', methods=['GET', 'POST'])
def new_category():
    """Create new category or render page for submiting a new category"""
    if 'user_id' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        public = True if request.form.get('public') else False
        category = Category(name=request.form['name'],
                            description=request.form['description'],
                            user_id=login_session['user_id'],
                            public=public)
        # Make sure that another public category of the same name doesn't exist.
        if not category.name or (name_exists(category.name) and public):
            flash("""The category has no name or another public category
                    of the same name already exists.""")
            return render_template('editcategory.html',
                                    category=category)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return redirect(url_for('show_category', category_id=category.id))
    else:
        return render_template('newcategory.html')

@app.route('/category/<int:category_id>/edit/', methods={'GET', 'POST'})
def edit_category(category_id):
    """Edit category or render page for editing category"""
    try:
        category = db_session.query(Category).filter_by(id=category_id).one()
    except:
        flash("This category does not exist yet")
        return redirect('/')
    if 'user_id' not in login_session:
        flash("Please log in to edit categories.")
        return redirect('/login')
    # Make sure that user can only their own categories
    elif login_session['user_id'] != category.user_id:
        flash("You can only edit categories that you have created yourself")
        return redirect("/category/%s" % category_id)
    else:
        if request.method == 'POST':
            name = request.form['name']
            if category.allow_private():
                category.public = True if request.form.get('public') else False
            else:
                category.public = True
            if category.public and name_exists(name, category_id):
                flash("This public category already exists")
                return render_template('editcategory.html', category=category)
            category.name = name
            category.description = request.form['description']
            db_session.add(category)
            db_session.commit()
            return redirect("/category/%s" % category_id)
        else:
            return render_template('editcategory.html',
                                    category=category)

@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def delete_category(category_id):
    """Delete a category or render page for category deletion"""
    try:
        category = db_session.query(Category).filter_by(id=category_id).one()
    except:
        flash("This category does not exist yet")
        return redirect('/')
    if 'user_id' not in login_session:
        flash("Please log in to delete categories.")
        return redirect('/login')
    elif login_session['user_id'] != category.user_id:
        flash("You can only delete categories that you have created yourself")
        return redirect("/category/%s" % category_id)
    elif category.items:
        flash("""This category has items in it. You can only delete an empty
              category (There may be private items in there)""")
        return redirect(url_for('show_category', category_id=category_id))
    else:
        if request.method == 'POST':
            db_session.delete(category)
            db_session.commit()
            return redirect('/')
        else:
            return render_template('deletecategory.html',
                                    category=category)
