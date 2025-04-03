# app.py
from flask import Flask, jsonify
from config import Config
from modules.create_user import create_user_bp
from modules.upload_notice import upload_notice_bp
from modules.record_attendance import record_attendance_bp
from modules.view_notice import view_notice_bp
from modules.voice import voice_bp
import os

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Register blueprints
app.register_blueprint(create_user_bp)
app.register_blueprint(upload_notice_bp)
app.register_blueprint(view_notice_bp)  # Add this line
app.register_blueprint(record_attendance_bp)

# Add this with your other blueprint registrations
app.register_blueprint(voice_bp)

if __name__ == '__main__':
    app.run(debug=True)