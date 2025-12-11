"""
Fall Detection using YOLO Model

This module provides an interface for fall detection using a YOLO-based model.
The actual model file should be provided by your teammate.

Author: ISDN3000C Project Team
Date: 2025-12-10
"""

import cv2
import numpy as np
import logging
from typing import Dict, Tuple, Optional, List
import yaml
from pathlib import Path
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FallDetector:
    """
    Fall detection using YOLO model.
    
    This class provides a clean interface for integrating your teammate's
    fall detection model. It handles model loading, inference, and result parsing.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize fall detector.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.config = config.get('fall_detection', {})
        else:
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            self.config = {}
        
        # Configuration parameters
        self.model_path = self.config.get('model_path', 'models/fall_detection.pt')
        self.confidence_threshold = self.config.get('confidence_threshold', 0.75)
        self.enabled = self.config.get('enabled', True)
        self.use_bpu = self.config.get('use_bpu', False)  # RDK X5 BPU acceleration
        
        # Model state
        self.model = None
        self.model_loaded = False
        self.mock_mode = False
        
        # Class labels (to be confirmed with teammate)
        self.classes = {
            0: 'standing',
            1: 'sitting',
            2: 'fallen',
            3: 'lying'  # May differ based on teammate's model
        }
        
        # Try to load model
        if self.enabled:
            self._load_model()
        else:
            logger.info("Fall detection disabled in configuration")
    
    def _load_model(self):
        """Load YOLO model from file."""
        model_file = Path(self.model_path)
        
        if not model_file.exists():
            logger.warning(f"Model file not found: {self.model_path}")
            logger.warning("Running in MOCK mode - will simulate fall detection")
            self.mock_mode = True
            return
        
        try:
            # Try loading with Ultralytics YOLO
            from ultralytics import YOLO
            logger.info(f"Loading YOLO model from {self.model_path}...")
            self.model = YOLO(self.model_path)
            self.model_loaded = True
            logger.info("✓ YOLO model loaded successfully")
            
        except ImportError:
            logger.error("Ultralytics not installed. Install with: pip install ultralytics")
            logger.warning("Running in MOCK mode")
            self.mock_mode = True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.warning("Running in MOCK mode")
            self.mock_mode = True
    
    def detect_fall(self, frame: np.ndarray) -> Dict:
        """
        Detect if a person has fallen in the given frame.
        
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
        
        # Validate input
        if frame is None or frame.size == 0:
            logger.warning("Invalid frame provided to fall detector")
            return result
        
        # Mock mode for testing
        if self.mock_mode:
            return self._mock_detection(frame, start_time)
        
        # Real detection
        if not self.model_loaded:
            logger.warning("Model not loaded, cannot perform detection")
            return result
        
        try:
            # Run inference
            results = self.model(frame, verbose=False)
            
            # Parse results
            for r in results:
                boxes = r.boxes
                
                if len(boxes) == 0:
                    continue
                
                # Get highest confidence detection
                for box in boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    
                    if conf < self.confidence_threshold:
                        continue
                    
                    # Get bounding box
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    bbox = (int(x1), int(y1), int(x2), int(y2))
                    
                    # Determine class
                    class_label = self.classes.get(cls, 'unknown')
                    
                    # Check if fall detected
                    fall_detected = class_label in ['fallen', 'lying']
                    
                    # Estimate chest region (upper 1/3 of bounding box)
                    chest_bbox = self._estimate_chest_region(bbox)
                    
                    # Update result
                    result.update({
                        'fall_detected': fall_detected,
                        'confidence': conf,
                        'person_detected': True,
                        'bounding_box': bbox,
                        'class_label': class_label,
                        'chest_bbox': chest_bbox
                    })
                    
                    break  # Use first detection
        
        except Exception as e:
            logger.error(f"Error during fall detection: {e}")
        
        # Calculate inference time
        result['inference_time'] = (time.time() - start_time) * 1000  # ms
        
        return result
    
    def _mock_detection(self, frame: np.ndarray, start_time: float) -> Dict:
        """
        Mock detection for testing without model.
        
        Simulates a person detection based on simple image analysis.
        """
        # Simulate processing time
        time.sleep(0.05)
        
        # Simple heuristic: detect if image has enough content
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        # Simulate person in center of frame
        h, w = frame.shape[:2]
        person_bbox = (w // 4, h // 4, 3 * w // 4, 3 * h // 4)
        chest_bbox = self._estimate_chest_region(person_bbox)
        
        # Random detection for testing (change this for your tests)
        person_detected = mean_brightness > 30  # Not completely dark
        
        inference_time = (time.time() - start_time) * 1000
        
        result = {
            'fall_detected': False,  # Change to True to test fall scenarios
            'confidence': 0.85,
            'person_detected': person_detected,
            'bounding_box': person_bbox if person_detected else None,
            'class_label': 'standing',  # Change to 'fallen' to test
            'chest_bbox': chest_bbox if person_detected else None,
            'inference_time': inference_time
        }
        
        logger.debug(f"[MOCK] Detection result: {result['class_label']}, conf={result['confidence']:.2f}")
        
        return result
    
    def _estimate_chest_region(self, person_bbox: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """
        Estimate chest region from person bounding box.
        
        The chest is typically in the upper 1/3 of the body,
        centered horizontally.
        
        Args:
            person_bbox: (x1, y1, x2, y2) of person
        
        Returns:
            (x1, y1, x2, y2) of estimated chest region
        """
        x1, y1, x2, y2 = person_bbox
        
        width = x2 - x1
        height = y2 - y1
        
        # Chest region: upper 1/3, centered horizontally, 60% width
        chest_x1 = int(x1 + width * 0.2)
        chest_y1 = int(y1 + height * 0.2)
        chest_x2 = int(x2 - width * 0.2)
        chest_y2 = int(y1 + height * 0.5)
        
        return (chest_x1, chest_y1, chest_x2, chest_y2)
    
    def set_mock_fall_state(self, fall_detected: bool):
        """
        Set mock fall state for testing.
        Only works in mock mode.
        
        Args:
            fall_detected: Whether to simulate fall detection
        """
        if self.mock_mode:
            self._mock_fall_state = fall_detected
            logger.info(f"Mock fall state set to: {fall_detected}")
        else:
            logger.warning("set_mock_fall_state() only works in mock mode")
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        info = {
            'model_path': self.model_path,
            'model_loaded': self.model_loaded,
            'mock_mode': self.mock_mode,
            'enabled': self.enabled,
            'confidence_threshold': self.confidence_threshold,
            'classes': self.classes,
            'use_bpu': self.use_bpu
        }
        
        return info


# Standalone test function
def test_fall_detector():
    """Test fall detector with sample image."""
    print("="*60)
    print("Fall Detector Test")
    print("="*60)
    
    detector = FallDetector()
    info = detector.get_model_info()
    
    print("\nModel Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test with blank image
    print("\nTesting with sample frame...")
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    test_frame[:] = (100, 100, 100)  # Gray background
    
    result = detector.detect_fall(test_frame)
    
    print("\nDetection Result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Test complete!")
    print("\nNote: To use real fall detection, your teammate must provide:")
    print("  1. Model file: models/fall_detection.pt")
    print("  2. Model specifications (classes, input size, preprocessing)")
    print("  3. Expected accuracy and inference time")


if __name__ == '__main__':
    test_fall_detector()
