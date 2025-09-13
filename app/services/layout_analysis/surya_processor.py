import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
import pdf2image
import numpy as np
from PIL import Image
import gc
import torch
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# Surya imports
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from surya.layout import LayoutPredictor

from .document_preprocessor import DocumentPreprocessor


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

    def convert_pdf_to_images(self, pdf_path: str, dpi: int = 150) -> List[Image.Image]:
        """Convert PDF pages to PIL images for Surya processing (optimized DPI)"""
        try:
            # Set Poppler path for pdf2image - reduced DPI for faster processing
            poppler_path = r"C:\Users\sahan\OneDrive\Desktop\document-analyzer\poppler\poppler-23.01.0\Library\bin"
            images = pdf2image.convert_from_path(
                pdf_path, 
                dpi=dpi, 
                fmt="RGB", 
                poppler_path=poppler_path,
                thread_count=min(4, multiprocessing.cpu_count())  # Use multiple threads
            )
            logger.info(f"Converted PDF to {len(images)} PIL images at {dpi} DPI")
            return images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return []

    def load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load image file as PIL Image with optimization"""
        try:
            image = Image.open(image_path)
            
            # Optimize image size for faster processing
            max_dimension = 2048  # Reduce max size for faster OCR
            if max(image.size) > max_dimension:
                ratio = max_dimension / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {new_size} for faster processing")
            
            logger.info(f"Loaded image: {image_path}")
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None
        
    def preprocess_pil_image(self, pil_image: Image.Image, force_preprocess: bool = False) -> Image.Image:
        """
        Preprocess a PIL image if it's detected as scanned (optimized)
        
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
            
            # Skip expensive preprocessing for digital-born documents to save time
            np_image = np.array(pil_image)
            
            # Only apply preprocessing if absolutely necessary
            if (self.preprocess_scanned or force_preprocess) and self._is_likely_scanned(np_image):
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
    
    def _is_likely_scanned(self, np_image: np.ndarray) -> bool:
        """Quick check if image is likely scanned (to skip preprocessing)"""
        try:
            # Quick Laplacian variance check
            gray = np.mean(np_image, axis=2) if len(np_image.shape) == 3 else np_image
            laplacian_var = np.var(gray[::4, ::4])  # Sample every 4th pixel for speed
            return laplacian_var < 1000  # Threshold for scanned documents
        except:
            return True  # Default to preprocessing if check fails

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
        Optimized for faster processing.
        
        Args:
            images: List of PIL images to process
            
        Returns:
            List of pages, each containing list of elements with layout and text info
        """
        try:
            # Preprocess all images with parallel processing
            preprocessed_images = []
            
            # Use ThreadPoolExecutor for parallel preprocessing
            with ThreadPoolExecutor(max_workers=min(4, len(images))) as executor:
                preprocessing_futures = []
                for i, image in enumerate(images):
                    future = executor.submit(self.preprocess_pil_image, image)
                    preprocessing_futures.append(future)
                
                for i, future in enumerate(preprocessing_futures):
                    logger.info(f"Preprocessing image {i+1}/{len(images)}")
                    preprocessed = future.result()
                    preprocessed_images.append(preprocessed)
            
            # Set torch to use all available CPU cores
            torch.set_num_threads(multiprocessing.cpu_count())
            
            logger.info("Running Surya layout analysis on preprocessed images")
            layout_results = self.layout_predictor(preprocessed_images)
            
            logger.info("Running Surya OCR text extraction on preprocessed images")
            # Process in smaller batches to avoid memory issues and improve speed
            batch_size = 1  # Process one image at a time for better memory management
            ocr_results = []
            
            for i in range(0, len(preprocessed_images), batch_size):
                batch = preprocessed_images[i:i+batch_size]
                logger.info(f"Processing OCR batch {i//batch_size + 1}/{(len(preprocessed_images) + batch_size - 1)//batch_size}")
                
                batch_results = self.recognition_predictor(
                    batch, 
                    det_predictor=self.detection_predictor
                )
                ocr_results.extend(batch_results)
                
                # Clean up memory after each batch
                gc.collect()

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
            # Clean up memory on error
            gc.collect()
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
            
            # Clean up memory after processing
            self._cleanup_memory()

            return all_pages_elements

        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            # Clean up memory even on error
            self._cleanup_memory()
            raise
    
    def _cleanup_memory(self):
        """Clean up GPU/CPU memory after processing"""
        try:
            # Clear any cached tensors
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Clear PyTorch cache even on CPU
            if hasattr(torch.backends, 'mkldnn'):
                torch.backends.mkldnn.enabled = False
                torch.backends.mkldnn.enabled = True
            
            # Force multiple garbage collections
            for _ in range(3):
                gc.collect()
            
            # Reset torch thread count to default
            torch.set_num_threads(1)
            
            logger.debug("Memory cleanup completed")
            
        except Exception as e:
            logger.warning(f"Error during memory cleanup: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self._cleanup_memory()
        except:
            pass
