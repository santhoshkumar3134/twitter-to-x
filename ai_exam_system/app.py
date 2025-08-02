from flask import Flask, render_template, request, jsonify, session, Response, redirect, url_for
import sqlite3
import cv2
import threading
import datetime
import os
import json
import base64
from io import BytesIO
from PIL import Image
import numpy as np

# Import detection modules
from detection.face_tracker import FaceTracker
from detection.yolo_detector import YOLODetector
from detection.gaze_tracker import GazeTracker
from audio.whisper_transcribe import AudioSurveillance

app = Flask(__name__)
app.secret_key = 'ai_exam_system_secret_key_2024'

# Global variables for video streaming
camera = None
face_tracker = None
yolo_detector = None
gaze_tracker = None
audio_surveillance = None
video_thread = None
alert_count = 0

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
    def __del__(self):
        self.video.release()
        
    def get_frame(self):
        success, image = self.video.read()
        if not success:
            return None
        return image
        
    def get_encoded_frame(self):
        frame = self.get_frame()
        if frame is None:
            return None
            
        # Process frame through detection modules
        processed_frame = self.process_detections(frame)
        
        ret, jpeg = cv2.imencode('.jpg', processed_frame)
        return jpeg.tobytes()
        
    def process_detections(self, frame):
        global alert_count, face_tracker, yolo_detector, gaze_tracker
        
        # Face detection
        if face_tracker:
            frame, face_alerts = face_tracker.detect_faces(frame)
            if face_alerts:
                self.log_alert("FACE_DETECTION", face_alerts, frame)
                
        # Object detection with YOLO
        if yolo_detector:
            frame, object_alerts = yolo_detector.detect_objects(frame)
            if object_alerts:
                self.log_alert("OBJECT_DETECTION", object_alerts, frame)
                
        # Gaze tracking
        if gaze_tracker:
            frame, gaze_alerts = gaze_tracker.track_gaze(frame)
            if gaze_alerts:
                self.log_alert("GAZE_TRACKING", gaze_alerts, frame)
                
        return frame
        
    def log_alert(self, alert_type, alert_message, frame):
        global alert_count
        alert_count += 1
        
        # Save screenshot
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"logs/alert_{timestamp}_{alert_count}.jpg"
        cv2.imwrite(screenshot_path, frame)
        
        # Log to database
        conn = sqlite3.connect('logs/exam_logs.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (student_id, timestamp, alert_type, message, screenshot_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (session.get('student_id', 'unknown'), timestamp, alert_type, alert_message, screenshot_path))
        conn.commit()
        conn.close()

def init_database():
    """Initialize SQLite database for logging alerts"""
    conn = sqlite3.connect('logs/exam_logs.db')
    cursor = conn.cursor()
    
    # Create alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            screenshot_path TEXT
        )
    ''')
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            login_time TEXT,
            exam_status TEXT DEFAULT 'not_started'
        )
    ''')
    
    conn.commit()
    conn.close()

def generate_frames():
    """Generator function for video streaming"""
    global camera
    while True:
        if camera is None:
            break
            
        frame = camera.get_encoded_frame()
        if frame is None:
            break
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        
        if student_id and student_name:
            # Store in session
            session['student_id'] = student_id
            session['student_name'] = student_name
            session['login_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Store in database
            conn = sqlite3.connect('logs/exam_logs.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO students (student_id, name, login_time, exam_status)
                VALUES (?, ?, ?, ?)
            ''', (student_id, student_name, session['login_time'], 'logged_in'))
            conn.commit()
            conn.close()
            
            return redirect(url_for('exam'))
        else:
            return render_template('login.html', error='Please fill all fields')
    
    return render_template('login.html')

@app.route('/exam')
def exam():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    global camera, face_tracker, yolo_detector, gaze_tracker, audio_surveillance
    
    # Initialize detection modules
    if camera is None:
        camera = VideoCamera()
        face_tracker = FaceTracker()
        yolo_detector = YOLODetector()
        gaze_tracker = GazeTracker()
        audio_surveillance = AudioSurveillance()
        
        # Start audio surveillance in background
        audio_thread = threading.Thread(target=audio_surveillance.start_monitoring, 
                                       args=(session['student_id'],))
        audio_thread.daemon = True
        audio_thread.start()
    
    return render_template('exam.html', 
                         student_name=session['student_name'],
                         student_id=session['student_id'])

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_alert_count')
def get_alert_count():
    """API endpoint to get current alert count"""
    global alert_count
    return jsonify({'alert_count': alert_count})

@app.route('/admin')
def admin():
    """Admin dashboard to monitor all students and alerts"""
    conn = sqlite3.connect('logs/exam_logs.db')
    cursor = conn.cursor()
    
    # Get all students
    cursor.execute('SELECT * FROM students ORDER BY login_time DESC')
    students = cursor.fetchall()
    
    # Get recent alerts
    cursor.execute('''
        SELECT * FROM alerts 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''')
    alerts = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin.html', students=students, alerts=alerts)

@app.route('/student_report/<student_id>')
def student_report(student_id):
    """Generate detailed report for a specific student"""
    conn = sqlite3.connect('logs/exam_logs.db')
    cursor = conn.cursor()
    
    # Get student info
    cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
    student = cursor.fetchone()
    
    # Get all alerts for this student
    cursor.execute('SELECT * FROM alerts WHERE student_id = ? ORDER BY timestamp', (student_id,))
    alerts = cursor.fetchall()
    
    conn.close()
    
    if not student:
        return "Student not found", 404
    
    return render_template('student_report.html', student=student, alerts=alerts)

@app.route('/logout')
def logout():
    global camera, alert_count
    
    # Clean up resources
    if camera:
        del camera
        camera = None
    
    alert_count = 0
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    print("🎓 AI-Protected Online Exam System Starting...")
    print("📊 Admin Dashboard: http://localhost:5000/admin")
    print("🔐 Student Login: http://localhost:5000/login")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)