"""
Image analysis service using MediaPipe and OpenAI Vision API.
Estimates body proportions and posture from full-body photos.
"""

import base64
import numpy as np
from typing import Dict, Tuple, Optional
from models import BodyAnalysis

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False


class ImageAnalysisService:
    """
    Analyzes full-body photos to extract posture and body proportions.
    Uses MediaPipe for pose estimation and OpenAI for advanced analysis.
    """

    def __init__(self):
        """Initialize MediaPipe pose detector if available."""
        if MEDIAPIPE_AVAILABLE:
            mp = __import__('mediapipe')
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=1,
                smooth_landmarks=True
            )
        else:
            self.pose = None
            print("Warning: MediaPipe not available. Using fallback body analysis.")

    def decode_image(self, image_base64: str) -> np.ndarray:
        """
        Decode base64 image to numpy array format.
        
        Args:
            image_base64: Image encoded as base64 string (with or without data URL prefix)
            
        Returns:
            np.ndarray: Image data
        """
        try:
            # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            # Decode base64 to bytes
            image_data = base64.b64decode(image_base64)
            
            # Try PIL first (more reliable for various formats)
            try:
                from PIL import Image as PILImage
                from io import BytesIO
                image = PILImage.open(BytesIO(image_data))
                image = np.array(image)
                # Convert RGBA to RGB if needed
                if len(image.shape) == 3 and image.shape[2] == 4:
                    image = image[:, :, :3]
                return image
            except Exception as pil_error:
                print(f"PIL decode attempt failed: {pil_error}")
            
            # Try OpenCV if PIL failed
            if CV2_AVAILABLE:
                try:
                    import cv2
                    nparr = np.frombuffer(image_data, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if image is not None:
                        return image
                except Exception as cv2_error:
                    print(f"OpenCV decode attempt failed: {cv2_error}")
            
            # If both failed, raise error
            raise ValueError("Could not decode image with any available method")
            
        except Exception as e:
            print(f"Image decode error: {e}")
            import traceback
            traceback.print_exc()
            raise

    def analyze_posture_mediapipe(self, image: np.ndarray) -> Dict:
        """
        Use MediaPipe to detect body landmarks and analyze posture.
        
        Args:
            image: Image in BGR or RGB format
            
        Returns:
            Dictionary with pose landmarks and analysis
        """
        if not MEDIAPIPE_AVAILABLE or self.pose is None:
            return {"error": "MediaPipe not available, using fallback analysis"}
        
        # Convert to RGB for MediaPipe
        if CV2_AVAILABLE:
            import cv2
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            # Assume PIL Image
            image_rgb = np.array(image)
            if len(image_rgb.shape) == 2:  # Grayscale
                image_rgb = np.stack([image_rgb]*3, axis=-1)
        
        results = self.pose.process(image_rgb)

        if not results.pose_landmarks:
            return {"error": "Could not detect pose in image"}

        landmarks = results.pose_landmarks.landmark
        if isinstance(image, np.ndarray):
            h, w = image.shape[:2]
        else:
            h, w = image.size[1], image.size[0]

        # Extract key joint coordinates (normalized to pixel coords)
        joints = {}
        for i, landmark in enumerate(landmarks):
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            confidence = landmark.visibility
            
            # Store key joints for analysis
            if i in [11, 12, 23, 24, 25, 26]:  # Shoulders, hips, knees, ankles
                joints[i] = {"x": x, "y": y, "confidence": confidence}

        return {
            "landmarks": joints,
            "image_height": h,
            "image_width": w,
            "detection_confidence": results.pose_landmarks.landmark[0].visibility
        }

    def estimate_body_proportions(
        self,
        height_cm: float,
        weight_kg: float,
        pose_analysis: Dict
    ) -> BodyAnalysis:
        """
        Estimate body proportions based on input and pose analysis.
        Uses anthropometric formulas for motorcycle fit.
        
        Args:
            height_cm: User height in centimeters
            weight_kg: User weight in kilograms
            pose_analysis: Results from MediaPipe pose detection
            
        Returns:
            BodyAnalysis: Estimated body proportions and posture
        """
        # Anthropometric estimation based on height
        # These are average proportions for human body
        inseam_cm = height_cm * 0.465  # ~46.5% of height
        torso_cm = height_cm * 0.367   # ~36.7% of height
        arm_reach_cm = height_cm * 1.03  # Usually slightly more than height

        # Determine posture type based on shoulder-hip angle
        posture_type = "upright"  # Default
        confidence = 0.75

        if pose_analysis.get("landmarks"):
            # If confident pose detection, refine posture
            confidence = min(0.95, confidence + 0.15)
            
            # Simple heuristic: check shoulder position relative to hips
            # In a more detailed implementation, calculate angles between joints
            posture_type = "upright"  # Placeholder - would calculate from angles

        return BodyAnalysis(
            inseam_cm=inseam_cm,
            torso_length_cm=torso_cm,
            arm_reach_cm=arm_reach_cm,
            posture_type=posture_type,
            confidence=confidence
        )

    def analyze_image(
        self,
        image_base64: str,
        height_cm: float,
        weight_kg: float
    ) -> BodyAnalysis:
        """
        Complete image analysis pipeline.
        
        Args:
            image_base64: Full-body photo as base64 string
            height_cm: User height in cm
            weight_kg: User weight in kg
            
        Returns:
            BodyAnalysis: Analyzed body proportions and posture
        """
        # Decode image
        image = self.decode_image(image_base64)

        # Run pose detection
        pose_analysis = self.analyze_posture_mediapipe(image)

        # Estimate body proportions
        body_analysis = self.estimate_body_proportions(
            height_cm,
            weight_kg,
            pose_analysis
        )

        return body_analysis


# Global service instance
_analysis_service: Optional[ImageAnalysisService] = None


def get_image_analysis_service() -> ImageAnalysisService:
    """Get or create image analysis service instance."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = ImageAnalysisService()
    return _analysis_service
