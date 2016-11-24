from pemoi import app
# import secret
from pemoi.config import SECRET, UPLOAD_FOLDER

app.secret_key = SECRET


# Config upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


# Start app
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
