#!/usr/bin/env python3
"""
AI-Protected Online Exam System - Startup Script
This script helps users start the exam system with proper checks and setup.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'opencv-python', 'mediapipe', 'ultralytics',
        'openai-whisper', 'numpy', 'pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - Installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("\n🔧 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies!")
        return False

def check_system_requirements():
    """Check system requirements"""
    print("\n🖥️  System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    
    # Check for camera/microphone (basic check)
    if platform.system() == "Linux":
        if os.path.exists("/dev/video0"):
            print("✅ Camera device detected")
        else:
            print("⚠️  Camera device not found - Please ensure webcam is connected")
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'models', 'static/css', 'static/js', 'static/images']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def display_startup_info():
    """Display startup information"""
    print("\n" + "="*60)
    print("🎓🔐 AI-PROTECTED ONLINE EXAM SYSTEM")
    print("="*60)
    print("🌟 Features:")
    print("   • Real-time face detection and tracking")
    print("   • Object detection (phones, books, laptops)")
    print("   • Gaze tracking and head pose monitoring")
    print("   • Audio surveillance with keyword detection")
    print("   • Comprehensive admin dashboard")
    print("   • Detailed student reports")
    print("\n🔗 Access Points:")
    print("   • Student Login: http://localhost:5000")
    print("   • Admin Dashboard: http://localhost:5000/admin")
    print("\n⚠️  Important:")
    print("   • Ensure webcam and microphone are connected")
    print("   • Grant browser permissions for camera/microphone")
    print("   • Use in well-lit environment for best results")
    print("="*60)

def main():
    """Main startup function"""
    print("🚀 Starting AI-Protected Online Exam System...")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check system requirements
    check_system_requirements()
    
    # Check dependencies
    print("\n📦 Checking Dependencies:")
    missing = check_dependencies()
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        response = input("\n🔧 Install missing dependencies? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if not install_dependencies():
                sys.exit(1)
        else:
            print("❌ Cannot start without required dependencies!")
            sys.exit(1)
    
    # Create directories
    print("\n📁 Setting up directories...")
    create_directories()
    
    # Display startup information
    display_startup_info()
    
    # Start the Flask application
    print("\n🔥 Starting Flask server...")
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down AI-Protected Exam System...")
        print("Thank you for using our secure examination platform!")
    except Exception as e:
        print(f"\n❌ Error starting the application: {e}")
        print("Please check the installation and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()