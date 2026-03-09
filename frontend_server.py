from flask import Flask, send_from_directory
import os

app = Flask(__name__)

WEB_FOLDER  = '/home/dirlei/alpha-dolar-2.0/web'
ROOT_FOLDER = '/home/dirlei/alpha-dolar-2.0'

@app.route('/')
def index():
    return send_from_directory(WEB_FOLDER, 'dashboard-fixed.html')

@app.route('/login')
def login():
    return send_from_directory(ROOT_FOLDER, 'login.html')

@app.route('/home')
def home():
    return send_from_directory(WEB_FOLDER, 'index.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory(WEB_FOLDER, 'dashboard-fixed.html')

@app.route('/videos')
def videos():
    # videos pode estar na raiz ou em /web
    if os.path.exists(os.path.join(WEB_FOLDER, 'videos.html')):
        return send_from_directory(WEB_FOLDER, 'videos.html')
    return send_from_directory(ROOT_FOLDER, 'vídeos.html')

@app.route('/<path:path>')
def serve_file(path):
    # Tenta /web primeiro, depois raiz
    if os.path.exists(os.path.join(WEB_FOLDER, path)):
        return send_from_directory(WEB_FOLDER, path)
    return send_from_directory(ROOT_FOLDER, path)

if __name__ == '__main__':
    app.run()
