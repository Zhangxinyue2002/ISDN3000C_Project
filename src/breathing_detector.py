"""
Breathing Detector using SIFT Keypoint Tracking and FFT Analysis

This module analyzes chest movement to detect breathing in fallen persons.
Algorithm:
1. Extract chest ROI from fallen person bounding box
2. Detect SIFT keypoints in chest area
3. Track keypoint motion across multiple frames
4. Apply FFT to detect periodic breathing motion
5. Validate breathing rate is within normal range (12-20 breaths/min)

Author: ISDN3000C Project Team
Date: 2025-11-30
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
import yaml
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BreathingDetector:
    """
    Detects breathing in fallen persons using SIFT keypoint tracking and FFT analysis.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize breathing detector.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.config = config.get('breathing_detection', {})
        else:
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            self.config = {}
        
        # Algorithm parameters
        self.min_breathing_rate = self.config.get('min_breathing_rate', 12)  # breaths/min
        self.max_breathing_rate = self.config.get('max_breathing_rate', 20)  # breaths/min
        self.min_motion_amplitude = self.config.get('min_motion_amplitude', 2.0)  # pixels
        self.capture_duration = self.config.get('capture_duration', 12)  # seconds
        self.fps = self.config.get('fps', 30)  # frames per second
        self.min_keypoints = self.config.get('min_keypoints', 10)  # minimum keypoints needed
        
        # Initialize SIFT detector
        try:
            self.sift = cv2.SIFT_create()
            logger.info("SIFT detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SIFT: {e}")
            raise
        
        # BFMatcher for keypoint matching
        self.bf_matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        
        logger.info(f"BreathingDetector initialized with rate range: {self.min_breathing_rate}-{self.max_breathing_rate} breaths/min")
    
    def analyze_breathing(
        self,
        video_frames: List[np.ndarray],
        chest_bbox: Tuple[int, int, int, int]
    ) -> Dict:
        """
        Analyze breathing from video frames.
        
        Args:
            video_frames: List of video frames (BGR images)
            chest_bbox: Bounding box of chest region [x1, y1, x2, y2]
        
        Returns:
            Dictionary containing:
                - breathing_detected: bool
                - confidence: float (0-1)
                - breathing_rate: float (breaths per minute)
                - motion_amplitude: float (pixels)
                - num_frames_analyzed: int
                - keypoints_tracked: int
        """
        logger.info(f"Analyzing breathing from {len(video_frames)} frames")
        
        # Validate input
        if len(video_frames) < 10:
            logger.warning("Insufficient frames for breathing analysis")
            return {
                'breathing_detected': False,
                'confidence': 0.0,
                'breathing_rate': 0.0,
                'motion_amplitude': 0.0,
                'num_frames_analyzed': len(video_frames),
                'keypoints_tracked': 0,
                'error': 'Insufficient frames'
            }
        
        try:
            # Step 1: Extract chest ROI from all frames
            chest_rois = self._extract_chest_rois(video_frames, chest_bbox)
            
            # Step 2: Detect keypoints in first frame
            first_frame = chest_rois[0]
            keypoints_first, descriptors_first = self.sift.detectAndCompute(first_frame, None)
            
            if keypoints_first is None or len(keypoints_first) < self.min_keypoints:
                logger.warning(f"Insufficient keypoints detected: {len(keypoints_first) if keypoints_first else 0}")
                return {
                    'breathing_detected': False,
                    'confidence': 0.0,
                    'breathing_rate': 0.0,
                    'motion_amplitude': 0.0,
                    'num_frames_analyzed': len(video_frames),
                    'keypoints_tracked': len(keypoints_first) if keypoints_first else 0,
                    'error': 'Insufficient keypoints'
                }
            
            logger.info(f"Detected {len(keypoints_first)} keypoints in first frame")
            
            # Step 3: Track keypoints across frames
            motion_vectors = self._track_keypoints(
                chest_rois,
                keypoints_first,
                descriptors_first
            )
            
            if len(motion_vectors) < 10:
                logger.warning(f"Insufficient motion data: {len(motion_vectors)} frames")
                return {
                    'breathing_detected': False,
                    'confidence': 0.0,
                    'breathing_rate': 0.0,
                    'motion_amplitude': 0.0,
                    'num_frames_analyzed': len(video_frames),
                    'keypoints_tracked': len(keypoints_first),
                    'error': 'Insufficient motion data'
                }
            
            # Step 4: Analyze periodic motion using FFT
            breathing_rate, motion_amplitude = self._analyze_periodic_motion(motion_vectors)
            
            # Step 5: Determine if breathing detected
            breathing_detected = self._is_breathing_detected(breathing_rate, motion_amplitude)
            
            # Calculate confidence based on motion amplitude and rate validity
            confidence = self._calculate_confidence(breathing_rate, motion_amplitude)
            
            result = {
                'breathing_detected': breathing_detected,
                'confidence': confidence,
                'breathing_rate': breathing_rate,
                'motion_amplitude': motion_amplitude,
                'num_frames_analyzed': len(video_frames),
                'keypoints_tracked': len(keypoints_first)
            }
            
            logger.info(f"Breathing analysis complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error during breathing analysis: {e}", exc_info=True)
            return {
                'breathing_detected': False,
                'confidence': 0.0,
                'breathing_rate': 0.0,
                'motion_amplitude': 0.0,
                'num_frames_analyzed': len(video_frames),
                'keypoints_tracked': 0,
                'error': str(e)
            }
    
    def _extract_chest_rois(
        self,
        frames: List[np.ndarray],
        bbox: Tuple[int, int, int, int]
    ) -> List[np.ndarray]:
        """
        Extract chest region of interest from all frames.
        
        Args:
            frames: List of video frames
            bbox: Chest bounding box [x1, y1, x2, y2]
        
        Returns:
            List of grayscale ROI images
        """
        x1, y1, x2, y2 = bbox
        chest_rois = []
        
        for frame in frames:
            # Extract ROI
            h, w = frame.shape[:2]
            x1_clip = max(0, min(x1, w))
            x2_clip = max(0, min(x2, w))
            y1_clip = max(0, min(y1, h))
            y2_clip = max(0, min(y2, h))
            
            roi = frame[y1_clip:y2_clip, x1_clip:x2_clip]
            
            # Convert to grayscale
            if len(roi.shape) == 3:
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            else:
                gray_roi = roi
            
            chest_rois.append(gray_roi)
        
        return chest_rois
    
    def _track_keypoints(
        self,
        rois: List[np.ndarray],
        keypoints_first: List,
        descriptors_first: np.ndarray
    ) -> List[float]:
        """
        Track keypoint motion across frames.
        
        Args:
            rois: List of grayscale ROI images
            keypoints_first: Keypoints from first frame
            descriptors_first: Descriptors from first frame
        
        Returns:
            List of average motion values (vertical displacement in pixels)
        """
        motion_vectors = []
        
        for i in range(1, len(rois)):
            # Detect keypoints in current frame
            keypoints_curr, descriptors_curr = self.sift.detectAndCompute(rois[i], None)
            
            if keypoints_curr is None or descriptors_curr is None:
                continue
            
            if len(keypoints_curr) < self.min_keypoints:
                continue
            
            # Match keypoints using k-nearest neighbors
            try:
                matches = self.bf_matcher.knnMatch(descriptors_first, descriptors_curr, k=2)
            except Exception as e:
                logger.debug(f"Matching failed for frame {i}: {e}")
                continue
            
            # Apply Lowe's ratio test
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.75 * n.distance:
                        good_matches.append(m)
            
            if len(good_matches) < self.min_keypoints:
                continue
            
            # Calculate vertical motion (breathing mainly causes vertical chest movement)
            vertical_motion = []
            for match in good_matches:
                pt_first = keypoints_first[match.queryIdx].pt
                pt_curr = keypoints_curr[match.trainIdx].pt
                
                # Calculate vertical displacement
                dy = pt_curr[1] - pt_first[1]
                vertical_motion.append(dy)
            
            # Average vertical motion for this frame
            avg_motion = np.mean(vertical_motion)
            motion_vectors.append(avg_motion)
        
        return motion_vectors
    
    def _analyze_periodic_motion(
        self,
        motion_vectors: List[float]
    ) -> Tuple[float, float]:
        """
        Apply FFT to detect breathing frequency and amplitude.
        
        Args:
            motion_vectors: List of motion values over time
        
        Returns:
            Tuple of (breathing_rate, motion_amplitude)
        """
        # Convert to numpy array
        motion_array = np.array(motion_vectors)
        
        # Calculate motion amplitude
        motion_amplitude = np.ptp(motion_array)  # peak-to-peak amplitude
        
        # Apply FFT
        fft_result = np.fft.fft(motion_array)
        frequencies = np.fft.fftfreq(len(motion_array), d=1.0/self.fps)
        
        # Get magnitude spectrum (only positive frequencies)
        magnitude = np.abs(fft_result)
        positive_freqs = frequencies[:len(frequencies)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        # Find dominant frequency (ignore DC component at index 0)
        if len(positive_magnitude) > 1:
            peak_idx = np.argmax(positive_magnitude[1:]) + 1
            peak_freq = positive_freqs[peak_idx]
            
            # Convert to breaths per minute
            breathing_rate = abs(peak_freq) * 60
        else:
            breathing_rate = 0.0
        
        logger.debug(f"FFT analysis: rate={breathing_rate:.2f} bpm, amplitude={motion_amplitude:.2f} px")
        
        return breathing_rate, motion_amplitude
    
    def _is_breathing_detected(
        self,
        breathing_rate: float,
        motion_amplitude: float
    ) -> bool:
        """
        Determine if breathing is detected based on rate and amplitude.
        
        Args:
            breathing_rate: Detected breathing rate (breaths/min)
            motion_amplitude: Motion amplitude (pixels)
        
        Returns:
            True if breathing detected, False otherwise
        """
        rate_valid = self.min_breathing_rate <= breathing_rate <= self.max_breathing_rate
        amplitude_valid = motion_amplitude >= self.min_motion_amplitude
        
        return rate_valid and amplitude_valid
    
    def _calculate_confidence(
        self,
        breathing_rate: float,
        motion_amplitude: float
    ) -> float:
        """
        Calculate confidence score for breathing detection.
        
        Args:
            breathing_rate: Detected breathing rate (breaths/min)
            motion_amplitude: Motion amplitude (pixels)
        
        Returns:
            Confidence score (0-1)
        """
        # Rate confidence (how close to expected range)
        if self.min_breathing_rate <= breathing_rate <= self.max_breathing_rate:
            rate_confidence = 1.0
        else:
            # Calculate distance from valid range
            if breathing_rate < self.min_breathing_rate:
                distance = self.min_breathing_rate - breathing_rate
            else:
                distance = breathing_rate - self.max_breathing_rate
            
            rate_confidence = max(0.0, 1.0 - distance / 10.0)
        
        # Amplitude confidence (normalized by expected amplitude)
        amplitude_confidence = min(1.0, motion_amplitude / 10.0)
        
        # Combined confidence
        confidence = (rate_confidence + amplitude_confidence) / 2.0
        
        return confidence
    
    def capture_and_analyze(
        self,
        camera,
        chest_bbox: Tuple[int, int, int, int],
        duration: Optional[float] = None
    ) -> Dict:
        """
        Capture video frames from camera and analyze breathing.
        
        Args:
            camera: OpenCV VideoCapture object or camera service
            chest_bbox: Chest bounding box [x1, y1, x2, y2]
            duration: Capture duration in seconds (uses config default if None)
        
        Returns:
            Breathing analysis result dictionary
        """
        if duration is None:
            duration = self.capture_duration
        
        num_frames = int(duration * self.fps)
        frames = []
        
        logger.info(f"Capturing {num_frames} frames over {duration} seconds...")
        
        # Capture frames
        for i in range(num_frames):
            ret, frame = camera.read()
            
            if not ret:
                logger.warning(f"Failed to capture frame {i}")
                continue
            
            frames.append(frame.copy())
            
            # Sleep to maintain target FPS
            cv2.waitKey(int(1000 / self.fps))
        
        logger.info(f"Captured {len(frames)} frames")
        
        # Analyze breathing
        return self.analyze_breathing(frames, chest_bbox)


def main():
    """
    Test breathing detector with simulated data or camera.
    """
    print("=" * 60)
    print("Breathing Detector Test")
    print("=" * 60)
    
    # Initialize detector
    detector = BreathingDetector()
    
    # Test with simulated breathing motion
    print("\n1. Testing with simulated breathing motion...")
    
    # Create simulated frames with breathing motion
    num_frames = 360  # 12 seconds at 30 fps
    frames = []
    
    # Simulate chest region (200x200 pixels)
    base_frame = np.ones((200, 200, 3), dtype=np.uint8) * 128
    
    for i in range(num_frames):
        frame = base_frame.copy()
        
        # Simulate breathing motion (16 breaths per minute = 0.267 Hz)
        breathing_freq = 16 / 60  # Hz
        phase = 2 * np.pi * breathing_freq * i / 30
        displacement = int(5 * np.sin(phase))  # 5 pixel amplitude
        
        # Shift frame vertically to simulate chest movement
        if displacement > 0:
            frame = np.roll(frame, displacement, axis=0)
        elif displacement < 0:
            frame = np.roll(frame, displacement, axis=0)
        
        frames.append(frame)
    
    # Analyze simulated breathing
    chest_bbox = (0, 0, 200, 200)
    result = detector.analyze_breathing(frames, chest_bbox)
    
    print(f"\nSimulated Breathing Results:")
    print(f"  Breathing Detected: {result['breathing_detected']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Breathing Rate: {result['breathing_rate']:.2f} breaths/min (expected: 16)")
    print(f"  Motion Amplitude: {result['motion_amplitude']:.2f} pixels")
    print(f"  Frames Analyzed: {result['num_frames_analyzed']}")
    print(f"  Keypoints Tracked: {result['keypoints_tracked']}")
    
    # Test with static frames (no breathing)
    print("\n2. Testing with static frames (no breathing)...")
    static_frames = [base_frame.copy() for _ in range(num_frames)]
    result_static = detector.analyze_breathing(static_frames, chest_bbox)
    
    print(f"\nStatic Frame Results:")
    print(f"  Breathing Detected: {result_static['breathing_detected']}")
    print(f"  Confidence: {result_static['confidence']:.2f}")
    print(f"  Breathing Rate: {result_static['breathing_rate']:.2f} breaths/min")
    print(f"  Motion Amplitude: {result_static['motion_amplitude']:.2f} pixels")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
