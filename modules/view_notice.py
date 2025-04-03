from flask import Blueprint, render_template, jsonify
from config import Config
import pymysql
import serial
from datetime import datetime

view_notice_bp = Blueprint('view_notice', __name__)

def get_db_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )

def get_nfc_id():
    try:
        port = Config.SERIAL_PORT
        ser = serial.Serial(
            port=port,
            baudrate=Config.SERIAL_BAUDRATE,
            timeout=2
        )
        ser.write(b'R')  # Request NFC data
        nfc_id = ser.readline().decode('utf-8').strip()
        ser.close()
        
        if not nfc_id:
            return None, "No NFC ID received (timeout)"
            
        if len(nfc_id) != 16 or not nfc_id.isalnum():
            return None, f"Invalid NFC ID format: {nfc_id}"
            
        return nfc_id, None
    except Exception as e:
        return None, str(e)

def get_user_type(nfc_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT type FROM users WHERE nfc_id = %s", (nfc_id,))
        user = cursor.fetchone()
        return user['type'] if user else None
    finally:
        cursor.close()
        conn.close()

@view_notice_bp.route('/view_notices')
def view_notices():
    today = datetime.now().date()
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Get all active notices
        query = """
        SELECT id, notice_type, image_path, name, from_date, to_date 
        FROM notices 
        WHERE from_date <= %s AND to_date >= %s
        ORDER BY created_at DESC
        """
        cursor.execute(query, (today, today))
        notices = cursor.fetchall()
        
        # Process notices
        processed_notices = []
        for notice in notices:
            notice['image_path'] = notice['image_path'].split('\\')[-1]  # Extract filename
            notice['from_date'] = notice['from_date'].strftime('%Y-%m-%d')
            notice['to_date'] = notice['to_date'].strftime('%Y-%m-%d')
            processed_notices.append(notice)
        
        # Separate by type
        events = [n for n in processed_notices if n['notice_type'] == 'event']
        announcements = [n for n in processed_notices if n['notice_type'] == 'announcement']
        
        return render_template('view_notices.html', 
                            events=events if events else [],
                            announcements=announcements if announcements else [],
                            display_duration=Config.NOTICE_DISPLAY_DURATION)
    
    except Exception as e:
        print(f"Error fetching notices: {str(e)}")
        return render_template('view_notices.html',
                            events=[],
                            announcements=[],
                            display_duration=Config.NOTICE_DISPLAY_DURATION)
    finally:
        cursor.close()
        conn.close()

@view_notice_bp.route('/scan_nfc', methods=['POST'])
def scan_nfc():
    nfc_id, error = get_nfc_id()
    if error:
        return jsonify({'success': False, 'error': error})
    
    user_type = get_user_type(nfc_id)
    if not user_type:
        return jsonify({'success': False, 'error': 'User not found'})
    
    notice_type = 'student' if user_type == 'student' else 'staff'
    today = datetime.now().date()
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
        SELECT id, notice_type, image_path, name, from_date, to_date
        FROM notices 
        WHERE from_date <= %s AND to_date >= %s AND notice_type = %s
        ORDER BY created_at DESC
        """
        cursor.execute(query, (today, today, notice_type))
        notices = cursor.fetchall()
        
        # Process notices
        processed_notices = []
        for notice in notices:
            notice['image_path'] = notice['image_path'].split('\\')[-1]
            notice['from_date'] = notice['from_date'].strftime('%Y-%m-%d')
            notice['to_date'] = notice['to_date'].strftime('%Y-%m-%d')
            processed_notices.append(notice)
        
        return jsonify({
            'success': True,
            'notices': processed_notices,
            'user_type': user_type,
            'notice_type': notice_type
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()