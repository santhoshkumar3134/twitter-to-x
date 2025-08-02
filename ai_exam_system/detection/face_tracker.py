import cv2
import mediapipe as mp
import numpy as np
import time

class FaceTracker:
    def __init__(self):
        """Initialize face detection using MediaPipe Face Detection"""
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5)
        
        # Alert tracking
        self.no_face_start_time = None
        self.multiple_faces_start_time = None
        self.alert_threshold = 5  # seconds
        self.last_alert_time = 0
        self.alert_cooldown = 3  # seconds between alerts
        
    def detect_faces(self, frame):
        """
        Detect faces in the frame and return alerts if necessary
        Returns: (processed_frame, alert_message)
        """
        alert_message = None
        current_time = time.time()
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        face_count = 0
        if results.detections:
            face_count = len(results.detections)
            
            # Draw bounding boxes around detected faces
            for detection in results.detections:
                self.mp_drawing.draw_detection(frame, detection)
                
                # Get bounding box coordinates
                bbox = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Draw rectangle and confidence score
                confidence = detection.score[0]
                cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
                cv2.putText(frame, f'Face: {confidence:.2f}', 
                           (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Check for no face detected
        if face_count == 0:
            if self.no_face_start_time is None:
                self.no_face_start_time = current_time
            elif (current_time - self.no_face_start_time) > self.alert_threshold:
                if (current_time - self.last_alert_time) > self.alert_cooldown:
                    alert_message = "NO FACE DETECTED - Student may have left the exam area"
                    self.last_alert_time = current_time
            
            # Reset multiple faces timer
            self.multiple_faces_start_time = None
            
            # Draw warning on frame
            cv2.putText(frame, "NO FACE DETECTED!", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                       
        elif face_count == 1:
            # Reset both timers when exactly one face is detected
            self.no_face_start_time = None
            self.multiple_faces_start_time = None
            
        elif face_count > 1:
            if self.multiple_faces_start_time is None:
                self.multiple_faces_start_time = current_time
            elif (current_time - self.multiple_faces_start_time) > self.alert_threshold:
                if (current_time - self.last_alert_time) > self.alert_cooldown:
                    alert_message = f"MULTIPLE FACES DETECTED - {face_count} people in frame"
                    self.last_alert_time = current_time
            
            # Reset no face timer
            self.no_face_start_time = None
            
            # Draw warning on frame
            cv2.putText(frame, f"MULTIPLE FACES: {face_count}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Display face count
        cv2.putText(frame, f"Faces: {face_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame, alert_message
    
    def reset_timers(self):
        """Reset all alert timers"""
        self.no_face_start_time = None
        self.multiple_faces_start_time = None
        self.last_alert_time = 0