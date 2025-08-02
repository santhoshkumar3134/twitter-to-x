import cv2
import mediapipe as mp
import numpy as np
import time
import math

class GazeTracker:
    def __init__(self):
        """Initialize gaze tracking using MediaPipe Face Mesh"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks indices for gaze tracking
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        # Face contour landmarks for head pose
        self.FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        
        # Alert tracking
        self.looking_away_start_time = None
        self.alert_threshold = 3  # seconds
        self.last_alert_time = 0
        self.alert_cooldown = 5  # seconds between alerts
        
        # Gaze thresholds
        self.gaze_threshold = 0.1  # Threshold for detecting looking away
        self.head_pose_threshold = 30  # degrees
        
    def track_gaze(self, frame):
        """
        Track gaze direction and head pose
        Returns: (processed_frame, alert_message)
        """
        alert_message = None
        current_time = time.time()
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Get image dimensions
                h, w, _ = frame.shape
                
                # Extract 3D landmarks
                landmarks_3d = []
                landmarks_2d = []
                
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    z = landmark.z
                    
                    landmarks_2d.append([x, y])
                    landmarks_3d.append([x, y, z])
                
                landmarks_2d = np.array(landmarks_2d, dtype=np.float64)
                landmarks_3d = np.array(landmarks_3d, dtype=np.float64)
                
                # Calculate head pose
                head_pose_angles = self.calculate_head_pose(landmarks_2d, landmarks_3d, frame.shape)
                
                # Calculate gaze direction
                gaze_direction = self.calculate_gaze_direction(landmarks_2d)
                
                # Check if looking away
                is_looking_away = self.is_looking_away(head_pose_angles, gaze_direction)
                
                # Draw face mesh (optional, can be disabled for performance)
                # self.mp_drawing.draw_landmarks(
                #     frame, face_landmarks, self.mp_face_mesh.FACEMESH_CONTOURS,
                #     None, self.mp_drawing_styles.get_default_face_mesh_contours_style())
                
                # Draw eye landmarks
                self.draw_eye_landmarks(frame, landmarks_2d)
                
                # Draw head pose information
                self.draw_head_pose_info(frame, head_pose_angles, gaze_direction, is_looking_away)
                
                # Handle alerts
                if is_looking_away:
                    if self.looking_away_start_time is None:
                        self.looking_away_start_time = current_time
                    elif (current_time - self.looking_away_start_time) > self.alert_threshold:
                        if (current_time - self.last_alert_time) > self.alert_cooldown:
                            alert_message = "STUDENT LOOKING AWAY - Possible cheating behavior detected"
                            self.last_alert_time = current_time
                    
                    # Draw warning
                    cv2.putText(frame, "LOOKING AWAY!", (50, 140), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    # Reset timer when looking at screen
                    self.looking_away_start_time = None
        
        return frame, alert_message
    
    def calculate_head_pose(self, landmarks_2d, landmarks_3d, image_shape):
        """Calculate head pose angles (pitch, yaw, roll)"""
        h, w, _ = image_shape
        
        # 3D model points of a generic face
        model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left Mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype=np.float64)
        
        # 2D image points from landmarks
        image_points = np.array([
            landmarks_2d[1],      # Nose tip
            landmarks_2d[152],    # Chin
            landmarks_2d[226],    # Left eye left corner
            landmarks_2d[446],    # Right eye right corner
            landmarks_2d[57],     # Left mouth corner
            landmarks_2d[287]     # Right mouth corner
        ], dtype=np.float64)
        
        # Camera matrix (assuming no lens distortion)
        focal_length = w
        center = (w/2, h/2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        
        # Distortion coefficients (assuming no distortion)
        dist_coeffs = np.zeros((4,1))
        
        # Solve PnP
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs)
        
        if success:
            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            
            # Extract angles
            angles = self.rotation_matrix_to_euler_angles(rotation_matrix)
            return angles
        
        return [0, 0, 0]  # Default if calculation fails
    
    def rotation_matrix_to_euler_angles(self, R):
        """Convert rotation matrix to Euler angles"""
        sy = math.sqrt(R[0,0] * R[0,0] + R[1,0] * R[1,0])
        
        singular = sy < 1e-6
        
        if not singular:
            x = math.atan2(R[2,1], R[2,2])
            y = math.atan2(-R[2,0], sy)
            z = math.atan2(R[1,0], R[0,0])
        else:
            x = math.atan2(-R[1,2], R[1,1])
            y = math.atan2(-R[2,0], sy)
            z = 0
        
        return [math.degrees(x), math.degrees(y), math.degrees(z)]
    
    def calculate_gaze_direction(self, landmarks_2d):
        """Calculate gaze direction based on eye landmarks"""
        # Get eye centers
        left_eye_center = np.mean([landmarks_2d[i] for i in self.LEFT_EYE[:6]], axis=0)
        right_eye_center = np.mean([landmarks_2d[i] for i in self.RIGHT_EYE[:6]], axis=0)
        
        # Calculate eye aspect ratios (for blink detection)
        left_ear = self.calculate_eye_aspect_ratio([landmarks_2d[i] for i in self.LEFT_EYE[:6]])
        right_ear = self.calculate_eye_aspect_ratio([landmarks_2d[i] for i in self.RIGHT_EYE[:6]])
        
        return {
            'left_eye_center': left_eye_center,
            'right_eye_center': right_eye_center,
            'left_ear': left_ear,
            'right_ear': right_ear
        }
    
    def calculate_eye_aspect_ratio(self, eye_landmarks):
        """Calculate Eye Aspect Ratio (EAR)"""
        eye_landmarks = np.array(eye_landmarks)
        
        # Vertical eye landmarks
        A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Horizontal eye landmark
        C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        # EAR calculation
        ear = (A + B) / (2.0 * C)
        return ear
    
    def is_looking_away(self, head_pose_angles, gaze_direction):
        """Determine if the person is looking away from the screen"""
        pitch, yaw, roll = head_pose_angles
        
        # Check head pose angles
        if abs(pitch) > self.head_pose_threshold or abs(yaw) > self.head_pose_threshold:
            return True
        
        # Check if eyes are closed (blinking)
        if gaze_direction['left_ear'] < 0.2 and gaze_direction['right_ear'] < 0.2:
            return False  # Don't flag as looking away if blinking
        
        return False
    
    def draw_eye_landmarks(self, frame, landmarks_2d):
        """Draw eye landmarks on the frame"""
        # Draw left eye
        left_eye_points = [landmarks_2d[i].astype(int) for i in self.LEFT_EYE[:6]]
        cv2.polylines(frame, [np.array(left_eye_points)], True, (0, 255, 0), 1)
        
        # Draw right eye
        right_eye_points = [landmarks_2d[i].astype(int) for i in self.RIGHT_EYE[:6]]
        cv2.polylines(frame, [np.array(right_eye_points)], True, (0, 255, 0), 1)
    
    def draw_head_pose_info(self, frame, head_pose_angles, gaze_direction, is_looking_away):
        """Draw head pose and gaze information on the frame"""
        pitch, yaw, roll = head_pose_angles
        
        # Display head pose angles
        cv2.putText(frame, f"Pitch: {pitch:.1f}°", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Yaw: {yaw:.1f}°", (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Roll: {roll:.1f}°", (10, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Display gaze status
        status_color = (0, 0, 255) if is_looking_away else (0, 255, 0)
        status_text = "LOOKING AWAY" if is_looking_away else "FOCUSED"
        cv2.putText(frame, f"Gaze: {status_text}", (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)