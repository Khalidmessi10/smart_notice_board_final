# config.py
import os

class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'  # replace with your MySQL username
    MYSQL_PASSWORD = ''  # replace with your MySQL password
    MYSQL_DB = 'smart_notice_board'
    SECRET_KEY = 'your-secret-key-here'
    SERIAL_PORT = 'COM12'
    SERIAL_BAUDRATE = 9600
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'notices')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB max