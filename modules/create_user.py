# modules/create_user.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
import pymysql
from config import Config
import serial
import serial.tools.list_ports

# Create a Blueprint for this module
create_user_bp = Blueprint('create_user', __name__, template_folder='../templates')

def get_nfc_id():
    try:
        port = Config.SERIAL_PORT
        ser = serial.Serial(
            port=port,
            baudrate=Config.SERIAL_BAUDRATE,
            timeout=2  # Increased timeout to wait for Arduino response
        )
        
        # Send a trigger character to Arduino if needed
        ser.write(b'R')  # Request NFC data
        
        # Read until newline or timeout
        nfc_id = ser.readline().decode('utf-8').strip()
        ser.close()
        
        if not nfc_id:
            return None, "No NFC ID received (timeout)"
            
        # Validate the received ID (16 alphanumeric chars)
        if len(nfc_id) != 16 or not nfc_id.isalnum():
            return None, f"Invalid NFC ID format: {nfc_id}"
            
        return nfc_id, None
    except Exception as e:
        return None, str(e)

# Rest of the file remains the same...
@create_user_bp.route('/create_user', methods=['GET', 'POST'])
def create_user():
    nfc_id = None
    error = None
    
    if request.method == 'POST':
        # Get form data
        nfc_id = request.form.get('nfc_id')
        name = request.form.get('name')
        user_type = request.form.get('type')
        dept = request.form.get('dept')
        year = request.form.get('year')
        semester = request.form.get('semester')
        
        # Validate required fields
        if not all([nfc_id, name, user_type, dept]):
            flash('Please fill in all required fields', 'error')
        else:
            # Connect to MySQL database
            try:
                connection = pymysql.connect(
                    host=Config.MYSQL_HOST,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    database=Config.MYSQL_DB
                )
                
                with connection.cursor() as cursor:
                    # Prepare SQL query based on user type
                    if user_type == 'student':
                        sql = """
                        INSERT INTO users 
                        (nfc_id, name, type, dept, year, semester) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql, (nfc_id, name, user_type, dept, year, semester))
                    else:
                        sql = """
                        INSERT INTO users 
                        (nfc_id, name, type, dept) 
                        VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(sql, (nfc_id, name, user_type, dept))
                    
                    connection.commit()
                    flash('User created successfully!', 'success')
                    return redirect(url_for('create_user.create_user'))
                
            except pymysql.Error as e:
                flash(f'Database error: {e}', 'error')
            finally:
                if connection:
                    connection.close()
    
    # For GET requests or if form validation fails
    return render_template('create_user.html', 
                         nfc_id=nfc_id,
                         error=error,
                         user_types=['student', 'professor', 'assistant_professor', 'associate_professor'],
                         departments=['AI&DS', 'AI&ML', 'ECE', 'CSE', 'EEE'],
                         years=[1, 2, 3, 4],
                         semesters=[1, 2, 3, 4, 5, 6, 7, 8])

@create_user_bp.route('/get_nfc_id')
def fetch_nfc_id():
    nfc_id, error = get_nfc_id()
    if error:
        return {'success': False, 'error': error}
    return {'success': True, 'nfc_id': nfc_id}