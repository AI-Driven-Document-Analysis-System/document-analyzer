import logging
import numpy as np
import cv2

# Surya imports
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from surya.layout import LayoutPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentPreprocessor:
    """Handles document image preprocessing and enhancement"""
    
    @staticmethod
    def enhance_image(image: np.ndarray) -> np.ndarray:
        """Apply image enhancement techniques"""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Noise removal
        denoised = cv2.medianBlur(gray, 3)
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        return sharpened
    
    @staticmethod
    def correct_skew(image: np.ndarray) -> np.ndarray:
        """Correct document skew"""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image
            
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        if abs(angle) > 0.5:  # Only correct if skew is significant
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
        
        return image
    
    @staticmethod
    def detect_if_scanned(image: np.ndarray, threshold: float = 0.1) -> bool:
        """
        Detect if an image is likely a scanned document vs digital-born
        Uses Laplacian variance to measure image sharpness
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Calculate Laplacian variance (measure of image sharpness)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Lower variance suggests blurrier image (likely scanned)
        # You may need to adjust this threshold based on your data
        is_scanned = laplacian_var < (threshold * 1000)
        
        logger.info(f"Laplacian variance: {laplacian_var:.2f}, Is scanned: {is_scanned}")
        return is_scanned
    
    @staticmethod
    def preprocess_image(image: np.ndarray, force_preprocess: bool = False) -> np.ndarray:
        """
        Complete preprocessing pipeline for document images
        
        Args:
            image: Input image as numpy array
            force_preprocess: If True, preprocess regardless of scan detection
        
        Returns:
            Preprocessed image as numpy array
        """
        # Check if image needs preprocessing
        if not force_preprocess and not DocumentPreprocessor.detect_if_scanned(image):
            logger.info("Image appears to be digital-born, skipping preprocessing")
            return image
        
        logger.info("Applying image preprocessing...")
        
        # Apply enhancement
        enhanced = DocumentPreprocessor.enhance_image(image)
        
        # Correct skew
        corrected = DocumentPreprocessor.correct_skew(enhanced)
        
        logger.info("Image preprocessing completed")
        return corrected
