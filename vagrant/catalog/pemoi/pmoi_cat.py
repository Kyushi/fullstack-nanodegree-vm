__author__ = 'Akechi'

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
def name_exists(name, public):
    if public:
        try:
            c = db_session.query(Category).filter_by(name=name).one()
        except:
            c = None
        if c:
            return True
    return False

def get_categories(only_own=False):
    user_id = login_session.get('user_id')
    if not user_id:
        return db_session.query(Category).filter_by(public=True).all()
    if only_own:
        return db_session.query(Category).filter_by(user_id=user_id).all()
    return db_session.query(Category).filter(
                           (Category.public==True)|
                           (Category.user_id==login_session['user_id'])
                           ).all()


# JSON endpoints
@app.route('/category/<int:category_id>/json/')
def category_json(category_id):
    items = db_session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(CategoryItems = [i.serialize for i in items])

@app.route('/categories/json/')
def categories_json():
    categories = db_session.query(Category).all()
    return jsonify(Categories = [c.serialize for c in categories])

# Routes

# Route for ajax check
@app.route('/checkcatname', methods=['POST'])
def check_catname():
    catname = request.data
    unique = name_exists(catname, True)
    if not unique:
        return "Bad category name"
    return "OK"

@app.route('/categories/')
def show_categories():
    return render_template('categories.html')

@app.route('/inspiration/myinspirations/')
def show_own():
    if not 'user_id' in login_session:
        flash("Please log in to view your items")
        return redirect(url_for('login'))
    items = db_session.query(Item).filter_by(user_id=login_session['user_id'])\
            .all()
    return render_template('index.html', items=items)


@app.route('/category/<int:category_id>/')
def show_category(category_id):
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
    if 'user_id' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        public = True if request.form.get('public') else False
        category = Category(name=request.form['name'],
                            description=request.form['description'],
                            user_id=login_session['user_id'],
                            public=public)
        if not category.name or name_exists(category.name, public):
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
    try:
        category = db_session.query(Category).filter_by(id=category_id).one()
    except:
        flash("This category does not exist yet")
        return redirect('/')
    if 'user_id' not in login_session:
        flash("Please log in to edit categories.")
        return redirect('/login')
    elif login_session['user_id'] != category.user_id:
        flash("You can only edit categories that you have created yourself")
        return redirect("/category/%s" % category_id)
    else:
        if request.method == 'POST':
            category.name = request.form['name']
            category.description = request.form['description']
            if category.allow_private():
                category.public = True if request.form.get('public') else False
            else:
                category.public = True
            db_session.add(category)
            db_session.commit()
            return redirect("/category/%s" % category_id)
        else:
            return render_template('editcategory.html',
                                    category=category)

@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def delete_category(category_id):
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
