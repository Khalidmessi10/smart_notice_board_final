# modules/record_attendance.py
from flask import Blueprint, jsonify
from config import Config
import pymysql
import serial
from datetime import datetime, date

record_attendance_bp = Blueprint('record_attendance', __name__)

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

def update_attendance_flags():
    """Update flags for previous days' attendance records"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        today = date.today()
        cursor.execute(
            "UPDATE attendance SET flag = 0 WHERE date < %s AND flag = 1",
            (today,)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

@record_attendance_bp.route('/record_attendance', methods=['POST'])
def record_attendance():
    nfc_id, error = get_nfc_id()
    if error:
        return jsonify({'success': False, 'message': f"Scan failed: {error}"})
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Update flags for previous days
        update_attendance_flags()
        
        # Check if user exists and get type
        cursor.execute("""
            SELECT id, type, name 
            FROM users 
            WHERE nfc_id = %s
        """, (nfc_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': "User not registered"})
        
        today = date.today()
        
        # Check if attendance already recorded today
        cursor.execute("""
            SELECT 1 FROM attendance 
            WHERE nfc_id = %s AND date = %s AND flag = 1
        """, (nfc_id, today))
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': f"{user['type'].capitalize()} {user['name']} already recorded attendance today"
            })
        
        # Record new attendance
        now = datetime.now()
        cursor.execute("""
            INSERT INTO attendance 
            (nfc_id, user_id, time_recorded, date, month, day, flag)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """, (nfc_id, user['id'], now, today, now.month, now.day))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f"Attendance recorded for {user['type']} {user['name']}",
            'time': now.strftime("%Y-%m-%d %H:%M:%S"),
            'user_type': user['type']
        })
    except pymysql.err.IntegrityError as e:
        conn.rollback()
        if 'unique_active_attendance' in str(e):
            return jsonify({
                'success': False,
                'message': f"{user['type'].capitalize()} {user['name']} already recorded attendance today"
            })
        return jsonify({'success': False, 'message': f"Database error: {str(e)}"})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f"Error: {str(e)}"})
    finally:
        cursor.close()
        conn.close()