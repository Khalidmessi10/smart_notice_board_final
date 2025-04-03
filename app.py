# app.py
from flask import Flask
from config import Config
from modules.create_user import create_user_bp
from modules.upload_notice import upload_notice_bp
import os

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Register blueprints
app.register_blueprint(create_user_bp)
app.register_blueprint(upload_notice_bp)

@app.route('/')
def index():
    return redirect('/create_user')

if __name__ == '__main__':
    app.run(debug=True)