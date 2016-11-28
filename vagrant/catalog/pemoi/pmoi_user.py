__author__ = 'Akechi'
import os
from flask import render_template, \
                  flash, \
                  redirect, \
                  request, \
                  url_for, \
                  session as login_session

from pemoi import app
from pmoi_auth import get_user_info, verify_username
from pmoi_db_session import db_session
from database_setup import Category, Item, User
from pmoi_item import delete_file_and_row

@app.route('/profile/<int:user_id>/')
def show_profile(user_id):
    try:
        user = get_user_info(user_id)
        return render_template('profile.html',
                               user=user)
    except:
        flash("This user does not exist")
        return redirect(url_for('index'))


@app.route('/profile/<int:user_id>/edit/', methods=['GET', 'POST'])
def edit_profile(user_id):
    if 'user_id' not in login_session:
        return redirect('/login')
    if user_id != login_session['user_id']:
        flash("You can only edit your own profile")
        return redirect(url_for('show_profile', user_id=user_id))
    try:
        user = get_user_info(user_id)
        if request.method == 'POST':
            users = db_session.query(User).all()
            name = request.form['name']
            username = request.form['username']
            picture = request.form['picture']
            about = request.form['about']
            email = request.form['email']
            if not user.username == username:
                if not verify_username(username, users):
                    error = "The username is not available or does not meet \
                            specifications"
                    return render_template('editprofile.html',
                                           error=error,
                                           user=user)
            user.name = name
            user.username = username
            user.picture = picture
            user.about = about
            user.email = email
            login_session['name'] = name
            login_session['username'] = username
            login_session['picture'] = picture
            login_session['email'] = email
            db_session.add(user)
            db_session.commit()
            return redirect(url_for('show_profile', user_id=user.id))
        else:
            return render_template('editprofile.html', user=user)
    except:
        flash("This user does not exist")
        return redirect(url_for('index'))

@app.route('/profile/<int:user_id>/delete/', methods=['GET', 'POST'])
def delete_profile(user_id):
    if not 'user_id' in login_session:
        return redirect(url_for('login'))
    if user_id != login_session["user_id"]:
        flash("You can only delete your own profile.")
        return redirect(url_for('index'))
    user = get_user_info(user_id)
    if request.method == 'POST':
        deleted = delete_user(user)
        if not deleted:
            flash("Oh. Looks like there was a problem with this.")
            return redirect(url_for('delete_profile'), user.id)
        flash("We are crying bitter tears to see you leaving. Please come back one day.")
        return redirect('/')
    else:
        return render_template('deleteprofile.html',
                               user=user,
                               my_categories=get_user_categories(user.id, False),
                               items=get_user_items(user.id))


# Get user categories
def get_user_categories(user_id, public=False):
    return db_session.query(Category).filter((Category.user_id==user_id)&(Category.public==public)).all()

# Get user items
def get_user_items(user_id):
    return db_session.query(Item).filter_by(user_id=user_id).all()

# Function to "delete" user
def delete_user(user):
    items = get_user_items(user.id)
    private_categories = get_user_categories(user.id, False)
    public_categories = get_user_categories(user.id, True)
    for item in items:
                delete_file_and_row(item)
    for cat in private_categories:
        db_session.delete(cat)
        db_session.commit()
    for cat in public_categories:
        cat.user_id = 1
        db_session.add(cat)
        db_session.commit()
    try:
        os.rmdir(os.path.join(app.config['UPLOAD_FOLDER'], user.username))
    except OSError as err:
        return False
    user.name = ''
    user.email = 'user_%s_@deleted' % user.id
    user.username = 'user_%s_deleted' % user.id
    user.about = ''
    user.picture = '/static/users/deleteduser.svg'
    db_session.add(user)
    db_session.commit()
    login_session.clear()
    return True
