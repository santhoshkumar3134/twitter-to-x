import cv2
import numpy as np
from ultralytics import YOLO
import time
import os

class YOLODetector:
    def __init__(self):
        """Initialize YOLOv10 object detection"""
        try:
            # Try to load YOLOv10 model, fallback to YOLOv8 if not available
            model_path = "models/yolov10n.pt"
            if not os.path.exists(model_path):
                # Download YOLOv8 nano model as fallback
                self.model = YOLO('yolov8n.pt')
            else:
                self.model = YOLO(model_path)
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            # Use YOLOv8 as fallback
            self.model = YOLO('yolov8n.pt')
        
        # Suspicious objects to detect
        self.suspicious_classes = {
            'cell phone': 67,  # COCO class ID for cell phone
            'book': 84,        # COCO class ID for book
            'laptop': 63,      # COCO class ID for laptop
            'person': 0        # COCO class ID for person
        }
        
        # Alert tracking
        self.last_alert_time = 0
        self.alert_cooldown = 5  # seconds between alerts
        self.detection_threshold = 0.5
        
        # COCO class names
        self.class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
            'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
            'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
            'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
            'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]
    
    def detect_objects(self, frame):
        """
        Detect suspicious objects in the frame
        Returns: (processed_frame, alert_message)
        """
        alert_message = None
        current_time = time.time()
        
        try:
            # Run YOLO detection
            results = self.model(frame, conf=self.detection_threshold, verbose=False)
            
            suspicious_detections = []
            person_count = 0
            
            # Process detections
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get class ID and confidence
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        # Get class name
                        class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"class_{class_id}"
                        
                        # Check for suspicious objects
                        if class_name == 'person':
                            person_count += 1
                            # Draw person detection in green
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, f'Person: {confidence:.2f}', 
                                       (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        elif class_name in ['cell phone', 'book', 'laptop']:
                            suspicious_detections.append({
                                'class': class_name,
                                'confidence': confidence,
                                'bbox': (x1, y1, x2, y2)
                            })
                            
                            # Draw suspicious object in red
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            cv2.putText(frame, f'{class_name}: {confidence:.2f}', 
                                       (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Generate alerts
            if person_count > 1:
                if (current_time - self.last_alert_time) > self.alert_cooldown:
                    alert_message = f"MULTIPLE PEOPLE DETECTED - {person_count} people in frame"
                    self.last_alert_time = current_time
                
                # Draw warning
                cv2.putText(frame, f"MULTIPLE PEOPLE: {person_count}", (50, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            if suspicious_detections:
                if (current_time - self.last_alert_time) > self.alert_cooldown:
                    objects_detected = [det['class'] for det in suspicious_detections]
                    alert_message = f"SUSPICIOUS OBJECTS DETECTED - {', '.join(set(objects_detected))}"
                    self.last_alert_time = current_time
                
                # Draw warning
                cv2.putText(frame, f"SUSPICIOUS OBJECTS: {len(suspicious_detections)}", (50, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Display detection count
            cv2.putText(frame, f"People: {person_count} | Objects: {len(suspicious_detections)}", 
                       (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
        except Exception as e:
            print(f"YOLO detection error: {e}")
            cv2.putText(frame, "YOLO Detection Error", (50, 140), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return frame, alert_message
    
    def download_model(self):
        """Download YOLOv10 model if not present"""
        try:
            # Create models directory
            os.makedirs('models', exist_ok=True)
            
            # Download YOLOv10 nano model
            model_url = "https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10n.pt"
            model_path = "models/yolov10n.pt"
            
            if not os.path.exists(model_path):
                print("Downloading YOLOv10 model...")
                import urllib.request
                urllib.request.urlretrieve(model_url, model_path)
                print("YOLOv10 model downloaded successfully!")
                
        except Exception as e:
            print(f"Error downloading YOLOv10 model: {e}")
            print("Using YOLOv8 as fallback...")