"""
Enhanced Fall Detector using YOLOv8 Pose Detection
Uses keypoint detection to determine if person has fallen

This is a ready-to-use fall detector that works immediately without
needing to download or train custom models.

Author: ISDN3000C Project Team
Date: 2025-12-10
"""

import cv2
import numpy as np
import logging
from typing import Dict, Tuple
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FallDetectorPose:
    """
    Fall detection using YOLOv8 pose estimation.
    
    Uses human keypoint detection to analyze body position and determine
    if a person has fallen based on body orientation and pose.
    """
    
    def __init__(self):
        """Initialize pose-based fall detector."""
        logger.info("Initializing YOLOv8 Pose Fall Detector...")
        
        try:
            from ultralytics import YOLO
            
            # Load YOLOv8 pose model (downloads automatically on first run ~6MB)
            logger.info("Loading YOLOv8 pose model (this may take a moment on first run)...")
            self.model = YOLO('yolov8n-pose.pt')  # Nano model (fast, good for RDK)
            # Alternative models:
            # 'yolov8s-pose.pt' - Small (better accuracy, slower)
            # 'yolov8m-pose.pt' - Medium (best accuracy, slowest)
            
            self.model_loaded = True
            logger.info("✓ YOLOv8 Pose model loaded successfully")
            
        except ImportError:
            logger.error("Ultralytics not installed. Run: pip install ultralytics")
            self.model_loaded = False
            return
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model_loaded = False
            return
        
        self.confidence_threshold = 0.5
        
        # COCO keypoint indices (YOLOv8 uses COCO format)
        self.KEYPOINTS = {
            'nose': 0,
            'left_eye': 1,
            'right_eye': 2,
            'left_ear': 3,
            'right_ear': 4,
            'left_shoulder': 5,
            'right_shoulder': 6,
            'left_elbow': 7,
            'right_elbow': 8,
            'left_wrist': 9,
            'right_wrist': 10,
            'left_hip': 11,
            'right_hip': 12,
            'left_knee': 13,
            'right_knee': 14,
            'left_ankle': 15,
            'right_ankle': 16
        }
        
        logger.info("Fall detector ready to use!")
    
    def detect_fall(self, frame: np.ndarray) -> Dict:
        """
        Detect if person has fallen based on pose.
        
        Args:
            frame: Input image (BGR format from OpenCV)
        
        Returns:
            Dictionary containing:
                - fall_detected: bool - True if fall detected
                - confidence: float - Detection confidence (0-1)
                - person_detected: bool - True if person found
                - bounding_box: tuple - (x1, y1, x2, y2) of detected person
                - class_label: str - Detected class (standing/sitting/fallen)
                - chest_bbox: tuple - Estimated chest region for breathing detection
                - inference_time: float - Time taken for detection (ms)
        """
        start_time = time.time()
        
        # Default result
        result = {
            'fall_detected': False,
            'confidence': 0.0,
            'person_detected': False,
            'bounding_box': None,
            'class_label': 'unknown',
            'chest_bbox': None,
            'inference_time': 0.0
        }
        
        if not self.model_loaded:
            logger.warning("Model not loaded")
            return result
        
        if frame is None or frame.size == 0:
            logger.warning("Invalid frame")
            return result
        
        try:
            # Run pose detection
            results = self.model(frame, verbose=False, conf=self.confidence_threshold)
            
            if len(results) == 0:
                return result
            
            # Get keypoints and boxes
            keypoints = results[0].keypoints
            boxes = results[0].boxes
            
            if keypoints is None or len(keypoints.data) == 0:
                return result
            
            if boxes is None or len(boxes) == 0:
                return result
            
            # Get first person detected
            kpts = keypoints.data[0].cpu().numpy()  # Shape: (17, 3) - x, y, confidence
            box = boxes[0]
            
            # Get bounding box
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            bbox = (int(x1), int(y1), int(x2), int(y2))
            conf = float(box.conf[0])
            
            result['person_detected'] = True
            result['bounding_box'] = bbox
            
            # Analyze pose for fall detection
            fall_detected, fall_confidence, pose_label = self._analyze_pose(kpts)
            
            result['fall_detected'] = fall_detected
            result['confidence'] = fall_confidence if fall_detected else conf
            result['class_label'] = pose_label
            result['chest_bbox'] = self._estimate_chest_region(bbox)
            
        except Exception as e:
            logger.error(f"Error during fall detection: {e}")
        
        # Calculate inference time
        result['inference_time'] = (time.time() - start_time) * 1000  # ms
        
        return result
    
    def _analyze_pose(self, keypoints: np.ndarray) -> Tuple[bool, float, str]:
        """
        Analyze pose keypoints to determine if person has fallen.
        
        Fall detection logic:
        1. Check body orientation (horizontal vs vertical)
        2. Check head position relative to hips
        3. Calculate aspect ratio (width vs height)
        
        Args:
            keypoints: Array of shape (17, 3) with x, y, confidence for each keypoint
        
        Returns:
            Tuple of (fall_detected, confidence, pose_label)
        """
        # Extract key points
        nose = keypoints[self.KEYPOINTS['nose']]
        left_shoulder = keypoints[self.KEYPOINTS['left_shoulder']]
        right_shoulder = keypoints[self.KEYPOINTS['right_shoulder']]
        left_hip = keypoints[self.KEYPOINTS['left_hip']]
        right_hip = keypoints[self.KEYPOINTS['right_hip']]
        
        # Check if keypoints are valid (confidence > 0.5)
        required_keypoints = [
            self.KEYPOINTS['nose'],
            self.KEYPOINTS['left_shoulder'],
            self.KEYPOINTS['right_shoulder'],
            self.KEYPOINTS['left_hip'],
            self.KEYPOINTS['right_hip']
        ]
        
        valid_points = all([keypoints[idx][2] > 0.5 for idx in required_keypoints])
        
        if not valid_points:
            return False, 0.0, 'unknown'
        
        # Calculate center points
        shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
        shoulder_center_y = (left_shoulder[1] + right_shoulder[1]) / 2
        hip_center_x = (left_hip[0] + right_hip[0]) / 2
        hip_center_y = (left_hip[1] + right_hip[1]) / 2
        head_x = nose[0]
        head_y = nose[1]
        
        # Calculate body dimensions
        body_height = abs(hip_center_y - head_y)
        body_width = abs(left_shoulder[0] - right_shoulder[0])
        torso_height = abs(shoulder_center_y - hip_center_y)
        
        # Avoid division by zero
        if body_height < 1:
            body_height = 1
        
        # Method 1: Aspect ratio (width vs height)
        # If person is horizontal, width > height
        aspect_ratio = body_width / body_height
        
        # Method 2: Head position relative to hips
        # If fallen, head and hips are at similar height
        head_hip_distance = abs(head_y - hip_center_y)
        
        # Method 3: Torso angle
        # Calculate angle of torso relative to vertical
        if torso_height > 0:
            torso_angle = np.arctan2(
                abs(shoulder_center_x - hip_center_x),
                torso_height
            ) * 180 / np.pi
        else:
            torso_angle = 0
        
        # Thresholds for fall detection
        FALL_ASPECT_RATIO = 1.2      # Width > 1.2x height suggests horizontal
        FALL_HEAD_HIP_DISTANCE = 80  # pixels - head close to hips
        FALL_TORSO_ANGLE = 45        # degrees - torso tilted significantly
        
        # Determine if fallen based on multiple criteria
        is_horizontal = aspect_ratio > FALL_ASPECT_RATIO
        head_near_hips = head_hip_distance < FALL_HEAD_HIP_DISTANCE
        torso_tilted = torso_angle > FALL_TORSO_ANGLE
        
        # Combine criteria
        fall_score = 0
        if is_horizontal:
            fall_score += 0.4
        if head_near_hips:
            fall_score += 0.4
        if torso_tilted:
            fall_score += 0.2
        
        if fall_score >= 0.5:
            # Person is likely fallen
            confidence = min(0.95, 0.5 + fall_score)
            return True, confidence, 'fallen'
        else:
            # Not fallen - normal state
            return False, 0.85, 'normal'
    
    def _estimate_chest_region(self, person_bbox: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """
        Estimate chest region from person bounding box.
        
        The chest is typically in the upper-middle third of the body.
        
        Args:
            person_bbox: (x1, y1, x2, y2) of person
        
        Returns:
            (x1, y1, x2, y2) of estimated chest region
        """
        x1, y1, x2, y2 = person_bbox
        
        width = x2 - x1
        height = y2 - y1
        
        # Chest region: upper-middle portion, centered horizontally, 60% width
        chest_x1 = int(x1 + width * 0.2)
        chest_y1 = int(y1 + height * 0.2)
        chest_x2 = int(x2 - width * 0.2)
        chest_y2 = int(y1 + height * 0.5)
        
        return (chest_x1, chest_y1, chest_x2, chest_y2)
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        info = {
            'model_type': 'YOLOv8 Pose Detection',
            'model_name': 'yolov8n-pose.pt',
            'model_loaded': self.model_loaded,
            'confidence_threshold': self.confidence_threshold,
            'detection_method': 'pose_keypoints',
            'num_keypoints': 17,
            'keypoints_format': 'COCO'
        }
        
        return info


# Test function
def test_fall_detector():
    """Test fall detector with webcam."""
    print("="*60)
    print("YOLOv8 Pose Fall Detector - Live Test")
    print("="*60)
    
    # Initialize detector
    print("\nInitializing detector...")
    detector = FallDetectorPose()
    
    if not detector.model_loaded:
        print("✗ Failed to load model")
        return
    
    # Print model info
    print("\nModel Information:")
    info = detector.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test with webcam
    print("\n" + "="*60)
    print("Starting webcam test...")
    print("Instructions:")
    print("  - Stand normally to see 'standing' detection")
    print("  - Lie down or simulate fall to trigger fall detection")
    print("  - Press 'q' to quit")
    print("="*60)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("✗ Cannot open webcam")
        return
    
    fps_counter = 0
    fps_start = time.time()
    fps_display = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        # Detect fall
        result = detector.detect_fall(frame)
        
        # Calculate FPS
        fps_counter += 1
        if time.time() - fps_start > 1:
            fps_display = fps_counter
            fps_counter = 0
            fps_start = time.time()
        
        # Draw results
        if result['person_detected']:
            x1, y1, x2, y2 = result['bounding_box']
            
            # Color based on detection
            if result['fall_detected']:
                color = (0, 0, 255)  # Red for fall
                status = "FALL DETECTED!"
            else:
                color = (0, 255, 0)  # Green for normal
                status = result['class_label'].upper()
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{result['class_label']}: {result['confidence']:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Draw chest region (for breathing detection)
            if result['chest_bbox']:
                cx1, cy1, cx2, cy2 = result['chest_bbox']
                cv2.rectangle(frame, (cx1, cy1), (cx2, cy2), (255, 255, 0), 1)
            
            # Large status text
            if result['fall_detected']:
                cv2.putText(frame, status, (50, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        
        # Display info
        cv2.putText(frame, f"FPS: {fps_display}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Inference: {result['inference_time']:.1f}ms", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Show frame
        cv2.imshow('YOLOv8 Pose Fall Detection', frame)
        
        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n✓ Test complete!")
    print("\nIf the test worked well, you can now use this detector in your main system.")


if __name__ == '__main__':
    test_fall_detector()
