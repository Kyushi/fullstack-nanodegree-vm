# PeMoI #

## Your Personal Museum of Inspiration ##

##### Save things that inspire you, add notes and share with the public or keep it just personal #####

Version 0.1
___
### About ###

The Personal Museum of Inspiration serves as a place to collect images that inspire you. The target audience are artists that would like to create a collection of artworks for personal use or to share with others.
Each saved artwork can be either stored privately or publicly, in a category which can be public or private as well.

Users can sign up with their Facebook, Google or github accounts.
___
### Requirements ###
- ability to run vagrant
- Python 2.7
- Web browser
- Shell
- Google, Facebook or github account

### Dependencies ###

- flask
- SQLAlchemy
- Httplib2
- urllib


### Quickstart ###

- Clone repository: `git clone https://github.com/Kyushi/fullstack-nanodegree-vm.git`.

- After installation of the required modules, run `python runserver.py`
- The required database `pemoi.db` will be created at root level
- Use your browser to open `localhost:5000`

You will find an empty page. Use the 'login or sign up' link at the top right to sign up with one of the possible OAuth services. After your initial sign up, you will be redirected to a sign up page to complete your registration. You can now create a new category or save a new image (you can create a category at this point as well).
Required fields for categories are category name, for images ("Inspirations") only the link is required. Everything is private by default, but can be made public by checking the checkbox accordingly.

Upon your first visit of the index page, an admin and a catchall category with ID 0 are created. These serve as fallbacks, if i.e. a user forgets to select a category, or if a user deletes their account and they still have public categories that are in use by someone else. In that case, the admin account gets ownership for the public category.

### TODO ###

- Improve form validation by use of (more ajax)
- Add local accounts (allow local login, non-OAuth)
- Allow uploading/linking of texts (txt, pdf) and video
