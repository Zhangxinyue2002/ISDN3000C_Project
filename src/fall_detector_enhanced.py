"""
Enhanced Fall Detector with Improved Camera Image Detection
Uses YOLOv8 Pose Detection with adjusted thresholds for real camera images

This version is specifically tuned for camera captures with:
- Lower confidence thresholds
- More flexible fall detection criteria
- Better handling of different camera angles
- Detailed logging for debugging

Author: ISDN3000C Project Team
Date: 2025-12-11
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


class FallDetectorEnhanced:
    """
    Enhanced fall detection using YOLOv8 pose estimation.
    
    Improved for real camera captures with:
    - Lower detection thresholds for camera images
    - Multiple fall criteria (more sensitive)
    - Detailed debug logging
    """
    
    def __init__(self, debug_mode=True):
        """Initialize enhanced pose-based fall detector."""
        logger.info("Initializing Enhanced YOLOv8 Pose Fall Detector...")
        
        self.debug_mode = debug_mode
        
        try:
            from ultralytics import YOLO
            
            # Load YOLOv8 pose model
            logger.info("Loading YOLOv8 pose model...")
            self.model = YOLO('yolov8n-pose.pt')
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
        
        # LOWER confidence threshold for better camera image detection
        self.confidence_threshold = 0.3  # Reduced from 0.5
        
        # COCO keypoint indices
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
        
        logger.info("Enhanced fall detector ready!")
    
    def detect_fall(self, frame: np.ndarray) -> Dict:
        """
        Detect if person has fallen based on pose.
        
        Args:
            frame: Input image (BGR format from OpenCV)
        
        Returns:
            Dictionary containing detection results
        """
        start_time = time.time()
        
        # Default result
        result = {
            'fall_detected': False,
            'confidence': 0.0,
            'person_detected': False,
            'bounding_box': None,
            'pose_label': 'unknown',
            'chest_bbox': None,
            'inference_time': 0.0,
            'debug_info': {}
        }
        
        if not self.model_loaded:
            logger.warning("Model not loaded")
            return result
        
        if frame is None or frame.size == 0:
            logger.warning("Invalid frame")
            return result
        
        try:
            # Run pose detection with LOWER confidence threshold
            results = self.model(frame, verbose=False, conf=self.confidence_threshold)
            
            if len(results) == 0:
                if self.debug_mode:
                    logger.debug("No detection results")
                return result
            
            # Get keypoints and boxes
            keypoints = results[0].keypoints
            boxes = results[0].boxes
            
            if keypoints is None or len(keypoints.data) == 0:
                if self.debug_mode:
                    logger.debug("No keypoints detected")
                return result
            
            if boxes is None or len(boxes) == 0:
                if self.debug_mode:
                    logger.debug("No boxes detected")
                return result
            
            # Get first person detected
            kpts = keypoints.data[0].cpu().numpy()  # Shape: (17, 3)
            box = boxes[0]
            
            # Get bounding box
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            bbox = (int(x1), int(y1), int(x2), int(y2))
            conf = float(box.conf[0])
            
            result['person_detected'] = True
            result['bounding_box'] = bbox
            
            # Analyze pose for fall detection
            fall_detected, fall_confidence, pose_label, debug_info = self._analyze_pose_enhanced(kpts, bbox)
            
            result['fall_detected'] = fall_detected
            result['confidence'] = fall_confidence if fall_detected else conf
            result['pose_label'] = pose_label
            result['chest_bbox'] = self._estimate_chest_region(bbox)
            result['debug_info'] = debug_info
            
            # Log debug information
            if self.debug_mode:
                logger.info(f"Detection: {pose_label} | Fall: {fall_detected} | Conf: {fall_confidence:.2f}")
                logger.info(f"Debug: {debug_info}")
            
        except Exception as e:
            logger.error(f"Error during fall detection: {e}", exc_info=True)
        
        # Calculate inference time
        result['inference_time'] = (time.time() - start_time) * 1000  # ms
        
        return result
    
    def _analyze_pose_enhanced(self, keypoints: np.ndarray, bbox: Tuple[int, int, int, int]) -> Tuple[bool, float, str, dict]:
        """
        Enhanced pose analysis with MORE SENSITIVE fall detection.
        
        Uses multiple criteria with LOWER thresholds:
        1. Body orientation (horizontal vs vertical)
        2. Head position relative to body
        3. Aspect ratio of bounding box
        4. Vertical extent of person
        5. Keypoint distribution
        
        Args:
            keypoints: Array of shape (17, 3) with x, y, confidence
            bbox: Bounding box (x1, y1, x2, y2)
        
        Returns:
            Tuple of (fall_detected, confidence, pose_label, debug_info)
        """
        debug_info = {}
        
        # Extract key points
        nose = keypoints[self.KEYPOINTS['nose']]
        left_shoulder = keypoints[self.KEYPOINTS['left_shoulder']]
        right_shoulder = keypoints[self.KEYPOINTS['right_shoulder']]
        left_hip = keypoints[self.KEYPOINTS['left_hip']]
        right_hip = keypoints[self.KEYPOINTS['right_hip']]
        left_knee = keypoints[self.KEYPOINTS['left_knee']]
        right_knee = keypoints[self.KEYPOINTS['right_knee']]
        
        # LOWER keypoint confidence threshold
        KEYPOINT_CONF_THRESHOLD = 0.3  # Reduced from 0.5
        
        # Check which keypoints are valid
        valid_nose = nose[2] > KEYPOINT_CONF_THRESHOLD
        valid_shoulders = left_shoulder[2] > KEYPOINT_CONF_THRESHOLD and right_shoulder[2] > KEYPOINT_CONF_THRESHOLD
        valid_hips = left_hip[2] > KEYPOINT_CONF_THRESHOLD and right_hip[2] > KEYPOINT_CONF_THRESHOLD
        
        debug_info['valid_nose'] = valid_nose
        debug_info['valid_shoulders'] = valid_shoulders
        debug_info['valid_hips'] = valid_hips
        
        # Need at least some valid keypoints
        if not (valid_shoulders or valid_hips):
            return False, 0.0, 'unknown', debug_info
        
        # Calculate center points
        if valid_shoulders:
            shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
            shoulder_center_y = (left_shoulder[1] + right_shoulder[1]) / 2
        else:
            shoulder_center_x = shoulder_center_y = 0
        
        if valid_hips:
            hip_center_x = (left_hip[0] + right_hip[0]) / 2
            hip_center_y = (left_hip[1] + right_hip[1]) / 2
        else:
            hip_center_x = hip_center_y = 0
        
        # Bounding box dimensions
        x1, y1, x2, y2 = bbox
        bbox_width = x2 - x1
        bbox_height = y2 - y1
        bbox_aspect_ratio = bbox_width / max(bbox_height, 1)
        
        debug_info['bbox_aspect_ratio'] = bbox_aspect_ratio
        debug_info['bbox_width'] = bbox_width
        debug_info['bbox_height'] = bbox_height
        
        # Criterion 1: Bounding box aspect ratio
        # If person is horizontal, width > height
        fall_criterion_1 = bbox_aspect_ratio > 0.8  # LOWERED from 1.2
        debug_info['criterion_1_bbox_horizontal'] = fall_criterion_1
        
        # Criterion 2: Head position relative to hips
        if valid_nose and valid_hips:
            head_y = nose[1]
            head_hip_distance = abs(head_y - hip_center_y)
            head_below_hips = head_y > hip_center_y - 50  # Head not much above hips
            
            debug_info['head_hip_distance'] = head_hip_distance
            debug_info['head_below_hips'] = head_below_hips
            
            # INCREASED threshold for more sensitivity
            fall_criterion_2 = head_hip_distance < 120  # INCREASED from 80
        else:
            fall_criterion_2 = False
        
        debug_info['criterion_2_head_near_hips'] = fall_criterion_2
        
        # Criterion 3: Body height vs width
        if valid_nose and valid_hips:
            body_height = abs(nose[1] - hip_center_y)
            if valid_shoulders:
                body_width = abs(left_shoulder[0] - right_shoulder[0])
            else:
                body_width = bbox_width * 0.6
            
            body_aspect_ratio = body_width / max(body_height, 1)
            fall_criterion_3 = body_aspect_ratio > 0.6  # LOWERED from 1.2
            
            debug_info['body_height'] = body_height
            debug_info['body_width'] = body_width
            debug_info['body_aspect_ratio'] = body_aspect_ratio
        else:
            fall_criterion_3 = False
        
        debug_info['criterion_3_body_horizontal'] = fall_criterion_3
        
        # Criterion 4: Vertical extent (person should be low in frame when fallen)
        vertical_position = (y1 + y2) / 2  # Center Y position
        frame_is_low = y2 > bbox_height * 0.6  # Bottom of bbox is low in frame
        fall_criterion_4 = bbox_height < bbox_width * 1.3  # Not very tall
        
        debug_info['criterion_4_not_tall'] = fall_criterion_4
        debug_info['vertical_position'] = vertical_position
        
        # Criterion 5: Torso angle (if shoulders and hips available)
        if valid_shoulders and valid_hips:
            torso_height = abs(shoulder_center_y - hip_center_y)
            torso_width = abs(shoulder_center_x - hip_center_x)
            
            if torso_height > 10:
                torso_angle = np.arctan2(torso_width, torso_height) * 180 / np.pi
            else:
                torso_angle = 90  # Nearly horizontal
            
            fall_criterion_5 = torso_angle > 30  # LOWERED from 45
            
            debug_info['torso_angle'] = torso_angle
        else:
            fall_criterion_5 = False
        
        debug_info['criterion_5_torso_tilted'] = fall_criterion_5
        
        # SCORING: Count how many criteria are met
        fall_score = 0
        criteria_met = []
        
        if fall_criterion_1:
            fall_score += 0.25
            criteria_met.append('bbox_horizontal')
        if fall_criterion_2:
            fall_score += 0.25
            criteria_met.append('head_near_hips')
        if fall_criterion_3:
            fall_score += 0.25
            criteria_met.append('body_horizontal')
        if fall_criterion_4:
            fall_score += 0.15
            criteria_met.append('not_tall')
        if fall_criterion_5:
            fall_score += 0.10
            criteria_met.append('torso_tilted')
        
        debug_info['fall_score'] = fall_score
        debug_info['criteria_met'] = criteria_met
        
        # LOWERED threshold: Need only 0.4 score (was 0.5)
        if fall_score >= 0.4:
            # Person is likely fallen
            confidence = min(0.95, 0.45 + fall_score)
            return True, confidence, 'fallen', debug_info
        else:
            # Not fallen
            return False, 0.85, 'normal', debug_info
    
    def _estimate_chest_region(self, person_bbox: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Estimate chest region from person bounding box."""
        x1, y1, x2, y2 = person_bbox
        
        width = x2 - x1
        height = y2 - y1
        
        # Chest region: upper-middle portion
        chest_x1 = int(x1 + width * 0.2)
        chest_y1 = int(y1 + height * 0.2)
        chest_x2 = int(x2 - width * 0.2)
        chest_y2 = int(y1 + height * 0.5)
        
        return (chest_x1, chest_y1, chest_x2, chest_y2)
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        info = {
            'model_type': 'YOLOv8 Pose Detection (Enhanced)',
            'model_name': 'yolov8n-pose.pt',
            'model_loaded': self.model_loaded,
            'confidence_threshold': self.confidence_threshold,
            'detection_method': 'enhanced_pose_analysis',
            'num_keypoints': 17,
            'keypoints_format': 'COCO',
            'debug_mode': self.debug_mode
        }
        
        return info


if __name__ == "__main__":
    print("Enhanced Fall Detector - Testing Mode")
    print("Use test_fall_model.py for image testing")
