#!/usr/bin/env python3
"""
Setup script for AI-Protected Online Exam System
Handles installation and initial configuration.
"""

import os
import sys
import subprocess
import platform

def create_virtual_environment():
    """Create a virtual environment for the project"""
    print("🔧 Creating virtual environment...")
    try:
        subprocess.check_call([sys.executable, '-m', 'venv', 'venv'])
        print("✅ Virtual environment created successfully!")
        
        # Provide activation instructions
        if platform.system() == "Windows":
            activate_cmd = "venv\\Scripts\\activate"
        else:
            activate_cmd = "source venv/bin/activate"
        
        print(f"📝 To activate the virtual environment, run:")
        print(f"   {activate_cmd}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment!")
        return False

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages!")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating project directories...")
    directories = [
        'logs',
        'models',
        'static/css',
        'static/js', 
        'static/images'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   Created: {directory}")
    
    print("✅ All directories created!")

def download_models():
    """Download required AI models"""
    print("🤖 Downloading AI models...")
    try:
        # Import after packages are installed
        from ultralytics import YOLO
        import whisper
        
        # Download YOLO model
        print("   Downloading YOLOv8 model...")
        model = YOLO('yolov8n.pt')
        
        # Download Whisper model
        print("   Downloading Whisper model...")
        whisper_model = whisper.load_model("tiny")
        
        print("✅ AI models downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to download models: {e}")
        return False

def run_tests():
    """Run system tests"""
    print("🧪 Running system tests...")
    try:
        result = subprocess.run([sys.executable, 'test_system.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed!")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def display_completion_message():
    """Display setup completion message"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("🚀 To start the AI-Protected Exam System:")
    print("   python run.py")
    print("   or")
    print("   python app.py")
    print("\n🌐 Access the system at:")
    print("   • Student Login: http://localhost:5000")
    print("   • Admin Dashboard: http://localhost:5000/admin")
    print("\n📚 For more information, check README.md")
    print("="*60)

def main():
    """Main setup function"""
    print("🎓🔐 AI-PROTECTED ONLINE EXAM SYSTEM - SETUP")
    print("="*50)
    
    # Check Python version
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    
    # Setup steps
    steps = [
        ("Creating directories", create_directories),
        ("Installing requirements", install_requirements),
        ("Downloading AI models", download_models),
        ("Running tests", run_tests)
    ]
    
    # Ask user if they want to create virtual environment
    create_venv = input("\n🤔 Create virtual environment? (recommended) [y/N]: ")
    if create_venv.lower() in ['y', 'yes']:
        if not create_virtual_environment():
            print("⚠️  Continuing without virtual environment...")
    
    # Execute setup steps
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    # Display completion message
    display_completion_message()

if __name__ == "__main__":
    main()