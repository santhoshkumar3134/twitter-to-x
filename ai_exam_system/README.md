# 🎓🔐 AI-Protected Online Exam System

A comprehensive, intelligent platform designed to conduct secure and fair remote examinations using real-time AI-powered monitoring.

## 🌟 Features

### 🔍 Real-Time Monitoring
- **Face Detection**: Ensures only one person is present during the exam
- **Object Detection**: Detects suspicious items (phones, books, laptops) using YOLOv8/YOLOv10
- **Gaze Tracking**: Monitors if students look away from the screen
- **Audio Surveillance**: Analyzes speech for suspicious keywords and conversations

### 🎯 AI-Powered Security
- **YOLOv10 Integration**: Advanced object detection for cheating prevention
- **MediaPipe Face Mesh**: Precise facial landmark detection and head pose estimation
- **Whisper AI**: State-of-the-art speech recognition for audio monitoring
- **Real-time Alerts**: Immediate notification of suspicious behavior

### 📊 Comprehensive Dashboard
- **Admin Panel**: Monitor multiple students simultaneously
- **Detailed Reports**: Individual student analysis with risk assessment
- **Alert Timeline**: Chronological view of all security incidents
- **Export Functionality**: PDF reports and data export

### 🔒 Security Features
- **Session Management**: Secure student authentication
- **Screenshot Capture**: Automatic evidence collection
- **Database Logging**: Complete audit trail of all activities
- **Fullscreen Enforcement**: Prevents tab switching and browser manipulation

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask (Python) |
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript |
| **AI/ML** | YOLOv8/YOLOv10, MediaPipe, OpenAI Whisper |
| **Computer Vision** | OpenCV |
| **Database** | SQLite |
| **Audio Processing** | PyAudio, SpeechRecognition |
| **Charts** | Chart.js |

## 📋 Prerequisites

- Python 3.8 or higher
- Webcam and microphone
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai_exam_system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download AI Models (Optional)
The system will automatically download required models on first run:
- YOLOv8 nano model (automatic)
- Whisper tiny model (automatic)
- MediaPipe models (automatic)

### 5. Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## 📱 Usage Guide

### For Students

1. **Login**: Navigate to `http://localhost:5000` and enter your Student ID and Name
2. **Permissions**: Allow webcam and microphone access when prompted
3. **Exam Environment**: 
   - Ensure you're in a well-lit room
   - Remove all unauthorized materials
   - Stay in view of the camera
   - Minimize background noise
4. **Take Exam**: Answer questions while being monitored by AI systems

### For Administrators

1. **Dashboard**: Access admin panel at `http://localhost:5000/admin`
2. **Monitor Students**: View real-time statistics and active sessions
3. **Review Alerts**: Check recent security incidents
4. **Generate Reports**: Click "View Report" for detailed student analysis
5. **Export Data**: Download PDF reports for record keeping

## 🔧 Configuration

### Alert Thresholds
Modify these values in the respective modules:

```python
# Face Detection (detection/face_tracker.py)
self.alert_threshold = 5  # seconds before alert

# Object Detection (detection/yolo_detector.py)
self.alert_cooldown = 5  # seconds between alerts

# Gaze Tracking (detection/gaze_tracker.py)
self.head_pose_threshold = 30  # degrees

# Audio Surveillance (audio/whisper_transcribe.py)
self.alert_cooldown = 10  # seconds between alerts
```

### Suspicious Keywords
Add or modify keywords in `audio/whisper_transcribe.py`:

```python
self.suspicious_keywords = [
    'help', 'answer', 'tell me', 'search', 'google',
    # Add more keywords as needed
]
```

## 📁 Project Structure

```
ai_exam_system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── login.html        # Student login page
│   ├── exam.html         # Exam interface
│   ├── admin.html        # Admin dashboard
│   └── student_report.html # Individual reports
├── static/               # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── detection/            # AI detection modules
│   ├── __init__.py
│   ├── face_tracker.py   # Face detection
│   ├── yolo_detector.py  # Object detection
│   └── gaze_tracker.py   # Gaze tracking
├── audio/                # Audio surveillance
│   ├── __init__.py
│   └── whisper_transcribe.py
├── logs/                 # Database and screenshots
│   ├── exam_logs.db      # SQLite database
│   └── alert_*.jpg       # Screenshot evidence
└── models/               # AI model files
    └── yolov10n.pt       # YOLO model (auto-downloaded)
```

## 🚨 Alert Types

### Face Detection Alerts
- **No Face Detected**: Student not visible for >5 seconds
- **Multiple Faces**: More than one person detected

### Object Detection Alerts
- **Suspicious Objects**: Phone, book, or laptop detected
- **Multiple People**: Additional persons in frame

### Gaze Tracking Alerts
- **Looking Away**: Head turned away from screen for >3 seconds
- **Extreme Head Pose**: Unusual head positioning

### Audio Surveillance Alerts
- **Suspicious Speech**: Detected keywords related to cheating
- **Continuous Speech**: Extended conversation detected

## 📊 Database Schema

### Students Table
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    student_id TEXT UNIQUE,
    name TEXT,
    login_time TEXT,
    exam_status TEXT
);
```

### Alerts Table
```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY,
    student_id TEXT,
    timestamp TEXT,
    alert_type TEXT,
    message TEXT,
    screenshot_path TEXT
);
```

## 🔒 Security Considerations

1. **Data Privacy**: All recordings and screenshots are stored locally
2. **Secure Sessions**: Student sessions are properly managed
3. **Evidence Collection**: Screenshots automatically saved for verification
4. **Audit Trail**: Complete logging of all activities
5. **Browser Security**: Prevents common cheating methods

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
For production deployment, consider:
- Using a production WSGI server (Gunicorn, uWSGI)
- Setting up HTTPS/SSL certificates
- Configuring a reverse proxy (Nginx)
- Using a more robust database (PostgreSQL, MySQL)
- Implementing proper backup strategies

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🔧 Troubleshooting

### Common Issues

1. **Camera Not Working**
   - Check browser permissions
   - Ensure camera is not used by other applications
   - Try different browsers

2. **Audio Not Recording**
   - Grant microphone permissions
   - Check system audio settings
   - Install PyAudio dependencies

3. **YOLO Model Loading Issues**
   - Ensure stable internet connection for model download
   - Check disk space for model storage
   - Verify ultralytics installation

4. **Performance Issues**
   - Reduce video resolution in `VideoCamera` class
   - Adjust detection confidence thresholds
   - Use smaller AI models (tiny versions)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI Whisper** for speech recognition
- **Ultralytics YOLO** for object detection
- **MediaPipe** for face mesh and pose estimation
- **OpenCV** for computer vision processing
- **Flask** for web framework
- **Bootstrap** for responsive design

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the configuration options

---

**⚠️ Important Note**: This system is designed for educational and legitimate proctoring purposes. Always ensure compliance with privacy laws and institutional policies when deploying in production environments.

**🎯 Built with AI • Secured by Design • Fair for All**