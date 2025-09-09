import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
import pdf2image
import requests
import numpy as np
from PIL import Image

# Surya imports
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from surya.layout import LayoutPredictor

from document_element import DocumentElement
from document_preprocessor import DocumentPreprocessor


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SuryaDocumentProcessor:
    """
    Document processor using Surya's advanced layout analysis and OCR capabilities.
    """

    def __init__(self,  preprocess_scanned: bool = True):
        """
        Initialize Surya document processor.
        
        """
        # Initialize Surya components
        self.foundation_predictor = FoundationPredictor()
        self.recognition_predictor = RecognitionPredictor(self.foundation_predictor)
        self.detection_predictor = DetectionPredictor()
        self.layout_predictor = LayoutPredictor()

        self.preprocess_scanned = preprocess_scanned
        self.preprocessor = DocumentPreprocessor()
        
        logger.info("Surya document processor initialized")

    def convert_pdf_to_images(self, pdf_path: str, dpi: int = 200) -> List[Image.Image]:
        """Convert PDF pages to PIL images for Surya processing"""
        try:
            images = pdf2image.convert_from_path(pdf_path, dpi=dpi, fmt="RGB")
            logger.info(f"Converted PDF to {len(images)} PIL images")
            return images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return []

    def load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load image file as PIL Image"""
        try:
            image = Image.open(image_path)
            logger.info(f"Loaded image: {image_path}")
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None
        
    def preprocess_pil_image(self, pil_image: Image.Image, force_preprocess: bool = False) -> Image.Image:
        """
        Preprocess a PIL image if it's detected as scanned
        
        Args:
            pil_image: PIL Image to preprocess
            force_preprocess: Force preprocessing regardless of scan detection
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert PIL to numpy array
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            np_image = np.array(pil_image)
            
            # Apply preprocessing if needed
            if self.preprocess_scanned or force_preprocess:
                processed_np = self.preprocessor.preprocess_image(np_image, force_preprocess)
                
                # Convert back to PIL
                if len(processed_np.shape) == 2:  # Grayscale
                    processed_pil = Image.fromarray(processed_np, mode='L')
                else:  # RGB
                    processed_pil = Image.fromarray(processed_np, mode='RGB')
                
                return processed_pil
            else:
                return pil_image
                
        except Exception as e:
            logger.error(f"Error in image preprocessing: {e}")
            return pil_image

    def iou(self, boxA: List[float], boxB: List[float]) -> float:
        """Compute IoU (intersection over union) between two bounding boxes"""
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0:
            return 0.0

        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        return interArea / float(boxAArea + boxBArea - interArea)

    def extract_layout_and_text(self, images: List[Image.Image]) -> List[List[Dict[str, Any]]]:
        """
        Run layout analysis and OCR on preprocessed images, then combine results.
        
        Args:
            images: List of PIL images to process
            
        Returns:
            List of pages, each containing list of elements with layout and text info
        """
        try:
            # Preprocess all images first
            preprocessed_images = []
            for i, image in enumerate(images):
                logger.info(f"Preprocessing image {i+1}/{len(images)}")
                preprocessed = self.preprocess_pil_image(image)
                preprocessed_images.append(preprocessed)
            
            logger.info("Running Surya layout analysis on preprocessed images")
            layout_results = self.layout_predictor(preprocessed_images)
            
            logger.info("Running Surya OCR text extraction on preprocessed images")
            ocr_results = self.recognition_predictor(
                preprocessed_images, 
                det_predictor=self.detection_predictor
            )

            all_pages_elements = []
            
            # Combine layout and OCR results
            for page_idx, (layout_page, ocr_page) in enumerate(zip(layout_results, ocr_results)):
                page_elements = []
                
                for block in layout_page.bboxes:
                    # Find overlapping text lines using IoU
                    block_texts = []
                    overlapping_lines = []
                    
                    for line in ocr_page.text_lines:
                        iou_score = self.iou(block.bbox, line.bbox)
                        if iou_score > 0:  # 0% overlap threshold
                            block_texts.append(line.text)
                            overlapping_lines.append({
                                'text': line.text,
                                'bbox': line.bbox,
                                'confidence': line.confidence,
                                'iou': iou_score
                            })
                    
                    # Calculate average confidence
                    avg_confidence = np.mean([line['confidence'] for line in overlapping_lines]) if overlapping_lines else 1.0
                    
                    element = {
                        "bounding_box": block.bbox,
                        "element_type": block.label,
                        "extracted_text": " ".join(block_texts),
                        "confidence": float(avg_confidence)
                    }
                    page_elements.append(element)
                
                all_pages_elements.append(page_elements)
                logger.info(f"Processed page {page_idx + 1}: {len(page_elements)} elements")
            
            return all_pages_elements

        except Exception as e:
            logger.error(f"Error in integrated processing: {e}")
            raise


    def process_document(self, 
                        file_path: str, 
                        document_id: Optional[str] = None, 
                        return_elements: bool = False,
                        force_preprocess: bool = False):
        """
        Process a complete document with preprocessing and Surya analysis.
        
        Args:
            file_path: Path to the document file
            document_id: Unique identifier for the document
            return_elements: Whether to return elements in memory
            force_preprocess: Force preprocessing even for digital-born documents
        """
        if document_id is None:
            document_id = str(uuid.uuid4())

        try:
            file_extension = Path(file_path).suffix.lower()

            # Load images based on file type
            if file_extension == ".pdf":
                images = self.convert_pdf_to_images(file_path)
            elif file_extension in [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]:
                image = self.load_image(file_path)
                images = [image] if image is not None else []
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

            if not images:
                raise ValueError("No images to process")

            # Process all pages with integrated pipeline
            all_pages_elements = self.extract_layout_and_text(images)
            


            logger.info(f"Integrated document processing completed. Total elements: {len(all_pages_elements)}")


            return all_pages_elements

        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise
