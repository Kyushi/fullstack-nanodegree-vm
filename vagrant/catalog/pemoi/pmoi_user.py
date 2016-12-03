"""Module to handles all user pages."""

import os
from flask import render_template, \
                  flash, \
                  redirect, \
                  request, \
                  url_for, \
                  session as login_session

from pemoi import app
from pmoi_auth import get_user_info
from pmoi_helpers import username_error
from pmoi_cat import get_categories
from pmoi_db_session import db_session
from pmoi_item import delete_file_and_row
from database_setup import Category, Item, User

@app.route('/profile/<int:user_id>/')
def show_profile(user_id):
    """Show the user profile."""
    try:
        user = get_user_info(user_id)
        return render_template('profile.html',
                               user=user)
    except:
        flash("This user does not exist")
        return redirect(url_for('index'))


@app.route('/profile/<int:user_id>/edit/', methods=['GET', 'POST'])
def edit_profile(user_id):
    """Edit a user's information.

    Users can edit the information that they have entered on our site:
    Username, and 'about'.
    """
    if 'user_id' not in login_session:
        return redirect('/login')
    if user_id != login_session['user_id']:
        flash("You can only edit your own profile")
        return redirect(url_for('show_profile', user_id=user_id))
    try:
        user = get_user_info(user_id)
    except:
        flash("This user does not exist")
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        about = request.form['about']
        if not user.username == username:
            # Verify the changed username
            error = username_error(username)
            if error:
                flash(error)
                return render_template('editprofile.html',
                                       user=user)
        try:
            # Rename the user's upload directory.
            olddir = os.path.join(app.config['UPLOAD_FOLDER'], user.username)
            newdir = os.path.join(app.config['UPLOAD_FOLDER'], username)
            os.rename(olddir, newdir)
        except OSError as err:
            # If there is a problem renaming the directory, throw an error.
            # This will have to be handled manually for now.
            raise
        user.username = username
        user.about = about
        login_session['username'] = username
        login_session['about'] = about
        db_session.add(user)
        db_session.commit()
        return redirect(url_for('show_profile', user_id=user.id))
    else:
        return render_template('editprofile.html', user=user)

@app.route('/profile/<int:user_id>/delete/', methods=['GET', 'POST'])
def delete_profile(user_id):
    """Delete a user profile.

    A user is able to delete all their information. Personal data will be
    renamed, all saved items, private categories and empty public categories
    will be deleted, public categories with other users' items in them are
    adopted by the admin.
    """
    if not 'user_id' in login_session:
        return redirect(url_for('login'))
    if user_id != login_session["user_id"]:
        flash("You can only delete your own profile.")
        return redirect(url_for('index'))
    user = get_user_info(user_id)
    if request.method == 'POST':
        deleted = delete_user(user)
        if not deleted:
            flash("Oh. Looks like there was a problem with this. Please contact\
                   the site admin")
            return redirect(url_for('delete_profile'), user.id)
        flash("We are crying bitter tears to see you leaving. Please come back one day.")
        return redirect('/')
    else:
        return render_template('deleteprofile.html',
                               user=user,
                               my_categories=get_user_categories(user.id,
                                                                 False),
                               my_public_categories=get_user_categories(user.id,
                                                                        True),
                               items=get_user_items(user.id))


# Helper functions for deleting a user profile.
# Get user categories
def get_user_categories(user_id, public=False):
    """Get a user's categories.

    Arguments: user_id as int, Boolean 'public' (optional).
    Returns list of Category objects. Either all private or all public.
    """
    return db_session.query(Category).filter((Category.user_id==user_id)&(Category.public==public)).all()

# Get user items
def get_user_items(user_id):
    """Get all user items.

    Argument: user_id as int
    Return: List of Item objects.
    """
    return db_session.query(Item).filter_by(user_id=user_id).all()

# Function to "delete" user
def delete_user(user):
    """Delete a user's profile

    Argument: User object.
    Return: Boolean, indicating success or failure.
    """
    items = get_user_items(user.id)
    private_categories = get_user_categories(user.id, False)
    public_categories = get_user_categories(user.id, True)
    for item in items:
                delete_file_and_row(item)
    for cat in private_categories:
        db_session.delete(cat)
        db_session.commit()
    for cat in public_categories:
        if not cat.items:
            # Delete public category if empty.
            db_session.delete(cat)
            db_session.commit()
        else:
            # Change owner to admin account if not empty.
            cat.user_id = 0
            db_session.add(cat)
            db_session.commit()
    try:
        os.rmdir(os.path.join(app.config['UPLOAD_FOLDER'], user.username))
    except OSError as err:
        return False
    # Replace user's personal information with anonymous unique info.
    user.name = ''
    user.email = 'user_%s_@deleted' % user.id
    user.username = 'user_%s_deleted' % user.id
    user.about = ''
    user.picture = '/static/users/deleteduser.svg'
    if 'provider' in login_session:
        provider = login_session['provider']
        if provider == 'Google':
            gdisconnect()
        elif provider == 'Facebook':
            fbdisconnect()
    db_session.add(user)
    db_session.commit()
    login_session.clear()
    return True
