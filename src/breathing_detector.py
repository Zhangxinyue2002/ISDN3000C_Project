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
        self.min_keypoints = self.config.get('min_keypoints', 5)  # minimum keypoints (lowered for clothing)
        
        # Initialize SIFT detector with lower contrast threshold for better feature detection
        try:
            self.sift = cv2.SIFT_create(contrastThreshold=0.03, edgeThreshold=15)
            logger.info("SIFT detector initialized (optimized for chest region)")
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
            # Step 3: Track chest motion using optical flow (no keypoint detection needed)
            logger.info("Tracking chest motion with optical flow...")
            motion_vectors = self._track_keypoints(
                chest_rois,
                None,  # Not used in optical flow method
                None   # Not used in optical flow method
            )
            
            if len(motion_vectors) < 10:
                logger.warning(f"Insufficient motion data: {len(motion_vectors)} samples")
                return {
                    'breathing_detected': False,
                    'confidence': 0.0,
                    'breathing_rate': 0.0,
                    'motion_amplitude': 0.0,
                    'num_frames_analyzed': len(video_frames),
                    'keypoints_tracked': 0,
                    'error': 'Insufficient motion data'
                }
            
            # Step 4: Analyze periodic motion using FFT
            breathing_rate, motion_amplitude = self._analyze_periodic_motion(motion_vectors)
            logger.info(f"📊 Motion amplitude: {motion_amplitude:.2f} px, Rate: {breathing_rate:.2f} BPM")
            
            # Step 5: Determine if breathing detected
            breathing_detected = self._is_breathing_detected(breathing_rate, motion_amplitude)
            
            # Calculate confidence based on motion amplitude and rate validity
            confidence = self._calculate_confidence(breathing_rate, motion_amplitude)
            
            # CRITICAL: Reject very low confidence detections
            MIN_CONFIDENCE_THRESHOLD = 0.2  # Balanced threshold
            if breathing_detected and confidence < MIN_CONFIDENCE_THRESHOLD:
                logger.warning(f"🚫 Low confidence {confidence:.2f} < {MIN_CONFIDENCE_THRESHOLD}, rejecting detection")
                breathing_detected = False
            
            result = {
                'breathing_detected': breathing_detected,
                'confidence': confidence,
                'breathing_rate': breathing_rate,
                'motion_amplitude': motion_amplitude,
                'num_frames_analyzed': len(video_frames),
                'keypoints_tracked': len(motion_vectors)  # Number of motion samples tracked
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
            
            # Enhance contrast to help SIFT find features on uniform clothing
            gray_roi = cv2.equalizeHist(gray_roi)
            
            chest_rois.append(gray_roi)
        
        return chest_rois
    
    def _track_keypoints(
        self,
        rois: List[np.ndarray],
        keypoints_first: List,
        descriptors_first: np.ndarray
    ) -> List[float]:
        """
        Track chest motion using Lucas-Kanade optical flow - more reliable than SIFT matching.
        
        Optical flow directly measures pixel movement between frames, which is more suitable
        for detecting subtle breathing motion compared to feature matching.
        
        Args:
            rois: List of grayscale ROI images
            keypoints_first: Not used (kept for compatibility)
            descriptors_first: Not used (kept for compatibility)
        
        Returns:
            List of vertical displacement values (pixels) representing chest movement
        """
        if len(rois) < 10:
            logger.warning("Not enough frames for optical flow analysis")
            return []
        
        motion_vectors = []
        
        # Lucas-Kanade optical flow parameters (optimized for low-res camera)
        lk_params = dict(
            winSize=(31, 31),  # Larger window for low-res
            maxLevel=4,  # More pyramid levels for better tracking
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.01)
        )
        
        # Create grid of tracking points in chest region (avoid edges)
        h, w = rois[0].shape
        y_start, y_end = int(h * 0.25), int(h * 0.75)
        x_start, x_end = int(w * 0.25), int(w * 0.75)
        
        # Sample 4x4 grid = 16 tracking points (reduced for low-res)
        y_points = np.linspace(y_start, y_end, 4, dtype=np.float32)
        x_points = np.linspace(x_start, x_end, 4, dtype=np.float32)
        
        p0 = []
        for y in y_points:
            for x in x_points:
                p0.append([[x, y]])
        p0 = np.array(p0, dtype=np.float32)
        
        prev_gray = rois[0]
        
        # Track through frames (process every 2nd frame for speed)
        for i in range(2, len(rois), 2):
            curr_gray = rois[i]
            
            try:
                # Calculate optical flow
                p1, status, err = cv2.calcOpticalFlowPyrLK(
                    prev_gray, curr_gray, p0, None, **lk_params
                )
                
                if p1 is None or status is None:
                    continue
                
                # Select successfully tracked points
                good_new = p1[status == 1]
                good_old = p0[status == 1]
                
                if len(good_new) < 6:  # Need at least 6 tracked points (lowered for low-res)
                    # Reset tracking if too many points lost
                    p0 = np.array([[[x, y]] for y in y_points for x in x_points], dtype=np.float32)
                    prev_gray = curr_gray
                    continue
                
                # Calculate VERTICAL displacement only (breathing is vertical motion)
                dy_values = good_new[:, 1] - good_old[:, 1]
                
                # Use median to reject outliers (more robust than mean)
                median_dy = np.median(dy_values)
                motion_vectors.append(median_dy)
                
                # Update for next iteration
                p0 = good_new.reshape(-1, 1, 2)
                prev_gray = curr_gray
                
            except Exception as e:
                logger.debug(f"Optical flow failed at frame {i}: {e}")
                continue
        
        logger.info(f"📊 Tracked {len(motion_vectors)} motion samples from {len(rois)} frames")
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
        
        # Apply FFT (accounting for frame step=3)
        fft_result = np.fft.fft(motion_array)
        effective_fps = self.fps / 3  # We process every 3rd frame
        frequencies = np.fft.fftfreq(len(motion_array), d=1.0/effective_fps)
        
        # Get magnitude spectrum (only positive frequencies)
        magnitude = np.abs(fft_result)
        positive_freqs = frequencies[:len(frequencies)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        # Filter frequencies to breathing range: 0.08-0.6 Hz (5-36 BPM)
        # This eliminates high-frequency noise
        min_freq = 0.08  # 5 BPM
        max_freq = 0.6   # 36 BPM
        
        # Find dominant frequency within breathing range
        valid_range = (positive_freqs >= min_freq) & (positive_freqs <= max_freq)
        
        if np.any(valid_range):
            # Get magnitudes only in valid frequency range
            valid_magnitude = positive_magnitude.copy()
            valid_magnitude[~valid_range] = 0  # Zero out invalid frequencies
            
            if np.max(valid_magnitude) > 0:
                peak_idx = np.argmax(valid_magnitude)
                peak_freq = positive_freqs[peak_idx]
                breathing_rate = abs(peak_freq) * 60
            else:
                breathing_rate = 0.0
        else:
            breathing_rate = 0.0
        
        logger.info(f"📊 FFT analysis: rate={breathing_rate:.2f} bpm, amplitude={motion_amplitude:.2f} px")
        
        return breathing_rate, motion_amplitude
    
    def _is_breathing_detected(
        self,
        breathing_rate: float,
        motion_amplitude: float
    ) -> bool:
        """
        Determine if breathing is detected based on rate and amplitude.
        
        Uses flexible logic:
        - If significant chest movement detected, accept wider rate range
        - Normal range: 8-25 BPM with min 1.5px amplitude
        - Relaxed range: 6-30 BPM with 2.5px+ amplitude (for slow/deep breathing)
        
        Args:
            breathing_rate: Detected breathing rate (breaths/min)
            motion_amplitude: Motion amplitude (pixels)
        
        Returns:
            True if breathing detected, False otherwise
        """
        # AMPLITUDE-BASED detection (primary) with rate as sanity check
        # For low-res cameras, focus on detecting ANY periodic motion
        
        # Reject suspiciously large motion (likely camera shake or body movement)
        if motion_amplitude > 5.0:
            logger.info(f"❌ Motion too large ({motion_amplitude:.2f}px) - likely camera shake or body movement")
            return False
        
        # Amplitude thresholds (sensitive for low-res)
        weak_motion = motion_amplitude >= 0.15    # Very sensitive
        clear_motion = motion_amplitude >= 0.30   # More confident
        strong_motion = motion_amplitude >= 0.50  # Very confident
        
        # Rate sanity check (very wide range, just eliminate obvious noise)
        rate_reasonable = 5 <= breathing_rate <= 35  # Extremely wide range
        rate_normal = 8 <= breathing_rate <= 25      # Normal range
        
        # Detection logic (amplitude-dominant):
        # 1. Strong motion (>0.5px) → accept if rate not crazy
        if strong_motion and rate_reasonable:
            logger.info(f"✅ STRONG motion {motion_amplitude:.2f}px, rate {breathing_rate:.1f} BPM")
            return True
        
        # 2. Clear motion (>0.3px) → accept if rate in normal range
        if clear_motion and rate_normal:
            logger.info(f"✅ CLEAR motion {motion_amplitude:.2f}px, rate {breathing_rate:.1f} BPM")
            return True
        
        # 3. Weak motion (>0.15px) → accept only with perfect rate
        if weak_motion and 10 <= breathing_rate <= 20:
            logger.info(f"✅ WEAK motion {motion_amplitude:.2f}px, perfect rate {breathing_rate:.1f} BPM")
            return True
        
        # Reject: insufficient motion or abnormal rate
        logger.info(f"❌ No breathing: motion={motion_amplitude:.2f}px, rate={breathing_rate:.1f}BPM")
        return False
    
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
        
        # Amplitude confidence (very sensitive for low-res camera)
        amplitude_confidence = min(1.0, motion_amplitude / 3.0)  # Lower threshold
        
        # Combined confidence (favor detection)
        confidence = (rate_confidence + amplitude_confidence) / 2.0 * 1.1  # Small boost
        
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
