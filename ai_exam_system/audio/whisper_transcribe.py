import whisper
import pyaudio
import wave
import numpy as np
import threading
import time
import sqlite3
import datetime
import os
from collections import deque
import speech_recognition as sr

class AudioSurveillance:
    def __init__(self):
        """Initialize audio surveillance system"""
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Audio recording parameters
        self.chunk_size = 1024
        self.sample_format = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = 16000
        self.record_seconds = 5  # Record in 5-second chunks
        
        # Initialize Whisper model (use tiny model for speed)
        try:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("tiny")
            self.use_whisper = True
            print("Whisper model loaded successfully!")
        except Exception as e:
            print(f"Failed to load Whisper: {e}")
            print("Falling back to SpeechRecognition...")
            self.use_whisper = False
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
        
        # Suspicious keywords to detect
        self.suspicious_keywords = [
            'help', 'answer', 'tell me', 'what is', 'how to', 'search', 'google',
            'phone', 'call', 'text', 'message', 'whatsapp', 'telegram',
            'copy', 'paste', 'share', 'send', 'email', 'screenshot',
            'exam', 'test', 'question', 'solution', 'cheat', 'cheating'
        ]
        
        # Alert tracking
        self.last_alert_time = 0
        self.alert_cooldown = 10  # seconds between alerts
        self.silence_threshold = 500  # RMS threshold for silence detection
        
        # Audio buffer for continuous monitoring
        self.audio_buffer = deque(maxlen=10)  # Keep last 10 chunks
        
    def start_monitoring(self, student_id):
        """Start audio monitoring in a separate thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.student_id = student_id
            self.monitoring_thread = threading.Thread(target=self._monitor_audio)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            print(f"Audio monitoring started for student: {student_id}")
    
    def stop_monitoring(self):
        """Stop audio monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        print("Audio monitoring stopped")
    
    def _monitor_audio(self):
        """Main audio monitoring loop"""
        try:
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Open microphone stream
            stream = audio.open(
                format=self.sample_format,
                channels=self.channels,
                rate=self.sample_rate,
                frames_per_buffer=self.chunk_size,
                input=True
            )
            
            print("Audio monitoring active...")
            
            while self.is_monitoring:
                # Record audio chunk
                audio_data = self._record_chunk(stream)
                
                if audio_data is not None:
                    # Add to buffer
                    self.audio_buffer.append(audio_data)
                    
                    # Check if audio contains speech
                    if self._contains_speech(audio_data):
                        # Transcribe audio
                        transcription = self._transcribe_audio(audio_data)
                        
                        if transcription and len(transcription.strip()) > 0:
                            print(f"Detected speech: {transcription}")
                            
                            # Check for suspicious keywords
                            alert_message = self._check_suspicious_content(transcription)
                            
                            if alert_message:
                                self._log_audio_alert(alert_message, transcription)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Audio monitoring error: {e}")
        finally:
            # Cleanup
            try:
                stream.stop_stream()
                stream.close()
                audio.terminate()
            except:
                pass
    
    def _record_chunk(self, stream):
        """Record a chunk of audio data"""
        try:
            frames = []
            for _ in range(0, int(self.sample_rate / self.chunk_size * self.record_seconds)):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
            
            # Convert to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            return audio_data
            
        except Exception as e:
            print(f"Audio recording error: {e}")
            return None
    
    def _contains_speech(self, audio_data):
        """Check if audio data contains speech (simple RMS-based detection)"""
        try:
            # Calculate RMS (Root Mean Square) for volume detection
            rms = np.sqrt(np.mean(audio_data**2))
            return rms > self.silence_threshold
        except:
            return False
    
    def _transcribe_audio(self, audio_data):
        """Transcribe audio data to text"""
        try:
            if self.use_whisper:
                return self._transcribe_with_whisper(audio_data)
            else:
                return self._transcribe_with_sr(audio_data)
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def _transcribe_with_whisper(self, audio_data):
        """Transcribe using Whisper"""
        try:
            # Convert to float32 and normalize
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(audio_float, language='en')
            return result['text'].strip()
            
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return ""
    
    def _transcribe_with_sr(self, audio_data):
        """Transcribe using SpeechRecognition as fallback"""
        try:
            # Save audio data to temporary file
            temp_filename = "temp_audio.wav"
            
            # Save as WAV file
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            # Transcribe using SpeechRecognition
            with sr.AudioFile(temp_filename) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                
            # Clean up temp file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
            return text
            
        except sr.UnknownValueError:
            # No speech detected
            return ""
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return ""
        except Exception as e:
            print(f"SR transcription error: {e}")
            return ""
    
    def _check_suspicious_content(self, transcription):
        """Check transcription for suspicious keywords"""
        text_lower = transcription.lower()
        
        detected_keywords = []
        for keyword in self.suspicious_keywords:
            if keyword in text_lower:
                detected_keywords.append(keyword)
        
        if detected_keywords:
            current_time = time.time()
            if (current_time - self.last_alert_time) > self.alert_cooldown:
                self.last_alert_time = current_time
                return f"SUSPICIOUS SPEECH DETECTED - Keywords: {', '.join(detected_keywords)}"
        
        # Check for continuous talking (potential conversation)
        if len(transcription.split()) > 10:  # More than 10 words
            current_time = time.time()
            if (current_time - self.last_alert_time) > self.alert_cooldown:
                self.last_alert_time = current_time
                return "CONTINUOUS SPEECH DETECTED - Possible conversation"
        
        return None
    
    def _log_audio_alert(self, alert_message, transcription):
        """Log audio alert to database"""
        try:
            conn = sqlite3.connect('logs/exam_logs.db')
            cursor = conn.cursor()
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            cursor.execute('''
                INSERT INTO alerts (student_id, timestamp, alert_type, message, screenshot_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.student_id, timestamp, "AUDIO_DETECTION", 
                 f"{alert_message} | Transcription: {transcription}", None))
            
            conn.commit()
            conn.close()
            
            print(f"Audio alert logged: {alert_message}")
            
        except Exception as e:
            print(f"Error logging audio alert: {e}")
    
    def get_audio_stats(self):
        """Get current audio monitoring statistics"""
        return {
            'is_monitoring': self.is_monitoring,
            'buffer_size': len(self.audio_buffer),
            'last_alert_time': self.last_alert_time,
            'use_whisper': self.use_whisper
        }