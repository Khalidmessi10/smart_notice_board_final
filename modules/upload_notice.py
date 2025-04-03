# modules/upload_notice.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
import pymysql
from config import Config
from datetime import datetime
import os
from werkzeug.utils import secure_filename

upload_notice_bp = Blueprint('upload_notice', __name__, template_folder='../templates')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@upload_notice_bp.route('/upload_notice', methods=['GET', 'POST'])
def upload_notice():
    if request.method == 'POST':
        # Get form data
        notice_type = request.form.get('notice_type')
        dept = request.form.get('dept')
        name = request.form.get('name')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        year = request.form.get('year') if notice_type == 'student' else None
        
        # Validate required fields
        if not all([notice_type, dept, name, from_date, to_date]):
            flash('Please fill in all required fields', 'error')
            return redirect(request.url)
            
        # Check if the post request has the file part
        if 'notice_image' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
            
        file = request.files['notice_image']
        
        # If user does not select file, browser submits empty file
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            try:
                # Create upload directory if it doesn't exist
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                
                # Secure the filename and save
                filename = secure_filename(file.filename)
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Connect to MySQL database
                connection = pymysql.connect(
                    host=Config.MYSQL_HOST,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    database=Config.MYSQL_DB
                )
                
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO notices 
                    (notice_type, dept, name, image_path, from_date, to_date, year) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        notice_type, 
                        dept, 
                        name, 
                        filepath, 
                        from_date, 
                        to_date, 
                        year
                    ))
                    
                    connection.commit()
                    flash('Notice uploaded successfully!', 'success')
                    return redirect(url_for('upload_notice.upload_notice'))
                
            except pymysql.Error as e:
                flash(f'Database error: {e}', 'error')
                # Clean up uploaded file if database operation failed
                if 'filepath' in locals() and os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
                # Clean up uploaded file if any error occurred
                if 'filepath' in locals() and os.path.exists(filepath):
                    os.remove(filepath)
            finally:
                if 'connection' in locals() and connection:
                    connection.close()
        else:
            flash('Allowed file types are png, jpg, jpeg', 'error')
    
    # For GET requests or if form validation fails
    return render_template('upload_notice.html',
                         notice_types=['event', 'announcement', 'staff', 'student'],
                         departments=['AI&DS', 'AI&ML', 'ECE', 'CSE', 'EEE'],
                         years=[1, 2, 3, 4])