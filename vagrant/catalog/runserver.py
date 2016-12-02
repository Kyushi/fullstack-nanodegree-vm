#!/usr/bin/env python
"""Set up the app config, run server locally"""

from pemoi import app

# app.secret_key = app.config['SECRET_KEY']


# Start app locally
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
