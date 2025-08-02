#!/usr/bin/env python3
"""
Test script for AI-Protected Online Exam System
Verifies that all components are working correctly.
"""

import sys
import os
import sqlite3
import cv2
import numpy as np

def test_database():
    """Test database functionality"""
    print("🗄️  Testing Database...")
    try:
        # Create test database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                student_id TEXT UNIQUE,
                name TEXT,
                login_time TEXT,
                exam_status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY,
                student_id TEXT,
                timestamp TEXT,
                alert_type TEXT,
                message TEXT,
                screenshot_path TEXT
            )
        ''')
        
        # Test insert
        cursor.execute("INSERT INTO students (student_id, name, exam_status) VALUES (?, ?, ?)",
                      ("TEST001", "Test Student", "testing"))
        
        cursor.execute("INSERT INTO alerts (student_id, alert_type, message) VALUES (?, ?, ?)",
                      ("TEST001", "TEST", "Test alert message"))
        
        conn.commit()
        
        # Test select
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        
        cursor.execute("SELECT * FROM alerts")
        alerts = cursor.fetchall()
        
        conn.close()
        
        if len(students) == 1 and len(alerts) == 1:
            print("✅ Database - Working correctly")
            return True
        else:
            print("❌ Database - Test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database - Error: {e}")
        return False

def test_opencv():
    """Test OpenCV functionality"""
    print("📷 Testing OpenCV...")
    try:
        # Test basic OpenCV operations
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        
        # Test image encoding
        ret, encoded = cv2.imencode('.jpg', test_image)
        
        if ret and encoded is not None:
            print("✅ OpenCV - Working correctly")
            return True
        else:
            print("❌ OpenCV - Test failed")
            return False
            
    except Exception as e:
        print(f"❌ OpenCV - Error: {e}")
        return False

def test_mediapipe():
    """Test MediaPipe functionality"""
    print("🎭 Testing MediaPipe...")
    try:
        import mediapipe as mp
        
        # Initialize face detection
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5)
        
        # Test with dummy image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_image)
        
        print("✅ MediaPipe - Working correctly")
        return True
        
    except Exception as e:
        print(f"❌ MediaPipe - Error: {e}")
        return False

def test_yolo():
    """Test YOLO functionality"""
    print("🎯 Testing YOLO...")
    try:
        from ultralytics import YOLO
        
        # Load model (will download if not present)
        model = YOLO('yolov8n.pt')
        
        # Test with dummy image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        results = model(test_image, verbose=False)
        
        if results:
            print("✅ YOLO - Working correctly")
            return True
        else:
            print("❌ YOLO - Test failed")
            return False
            
    except Exception as e:
        print(f"❌ YOLO - Error: {e}")
        return False

def test_whisper():
    """Test Whisper functionality"""
    print("🎤 Testing Whisper...")
    try:
        import whisper
        
        # Load tiny model for testing
        model = whisper.load_model("tiny")
        
        # Create dummy audio data
        sample_rate = 16000
        duration = 1  # 1 second
        dummy_audio = np.zeros(sample_rate * duration, dtype=np.float32)
        
        # Test transcription
        result = model.transcribe(dummy_audio)
        
        if result is not None:
            print("✅ Whisper - Working correctly")
            return True
        else:
            print("❌ Whisper - Test failed")
            return False
            
    except Exception as e:
        print(f"❌ Whisper - Error: {e}")
        return False

def test_flask_imports():
    """Test Flask and related imports"""
    print("🌐 Testing Flask imports...")
    try:
        from flask import Flask, render_template, request, jsonify, session, Response
        import datetime
        import threading
        import json
        
        print("✅ Flask - All imports working")
        return True
        
    except Exception as e:
        print(f"❌ Flask - Import error: {e}")
        return False

def test_detection_modules():
    """Test custom detection modules"""
    print("🔍 Testing Detection Modules...")
    try:
        # Test imports of custom modules
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from detection.face_tracker import FaceTracker
        from detection.yolo_detector import YOLODetector
        from detection.gaze_tracker import GazeTracker
        from audio.whisper_transcribe import AudioSurveillance
        
        # Initialize modules
        face_tracker = FaceTracker()
        yolo_detector = YOLODetector()
        gaze_tracker = GazeTracker()
        audio_surveillance = AudioSurveillance()
        
        print("✅ Detection Modules - All imports working")
        return True
        
    except Exception as e:
        print(f"❌ Detection Modules - Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 AI-PROTECTED EXAM SYSTEM - COMPONENT TESTS")
    print("="*60)
    
    tests = [
        test_flask_imports,
        test_database,
        test_opencv,
        test_mediapipe,
        test_yolo,
        test_whisper,
        test_detection_modules
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

def main():
    """Main test function"""
    success = run_all_tests()
    
    if success:
        print("\n🚀 You can now start the system with:")
        print("   python app.py")
        print("   or")
        print("   python run.py")
    else:
        print("\n🔧 Please install missing dependencies:")
        print("   pip install -r requirements.txt")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())