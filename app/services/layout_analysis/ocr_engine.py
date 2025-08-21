import logging
import easyocr
import pytesseract
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
from typing import List, Dict, Any
from transformers import (
    TrOCRProcessor,
    VisionEncoderDecoderModel
)
from .bounding_box import BoundingBox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCREngine:
    """Multi-engine OCR implementation supporting PaddleOCR, Tesseract, and TrOCR"""
    
    def __init__(self, engines: List[str] = ['paddleocr', 'tesseract']):
        self.engines = engines
        self.ocr_instances = {}
        self.setup_engines()
    
    def setup_engines(self):
        """Initialize OCR engines"""
        for engine in self.engines:
            try:
                if engine == 'paddleocr':
                    self.ocr_instances['paddleocr'] = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
                elif engine == 'easyocr':
                    self.ocr_instances['easyocr'] = easyocr.Reader(['en'])
                elif engine == 'tesseract':
                    # Tesseract is called directly, no initialization needed
                    self.ocr_instances['tesseract'] = True
                elif engine == 'trocr':
                    self.setup_trocr()
                    
                logger.info(f"Initialized {engine} OCR engine")
            except Exception as e:
                logger.warning(f"Failed to initialize {engine}: {e}")
    
    def setup_trocr(self):
        """Setup TrOCR model"""
        try:
            self.trocr_processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
            self.trocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")
            self.ocr_instances['trocr'] = True
            logger.info("TrOCR model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load TrOCR: {e}")
    
    def extract_text_paddleocr(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Extract text using PaddleOCR"""
        try:
            results = self.ocr_instances['paddleocr'].ocr(image, cls=True)
            
            elements = []
            if results and results[0]:
                for line in results[0]:
                    bbox, (text, confidence) = line
                    
                    # Convert bbox to proper format
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    bounding_box = BoundingBox(
                        x1=int(min(x_coords)),
                        y1=int(min(y_coords)),
                        x2=int(max(x_coords)),
                        y2=int(max(y_coords))
                    )
                    
                    elements.append({
                        'bounding_box': bounding_box.coordinates,
                        'text': text.strip(),
                        'confidence': float(confidence),
                        'engine': 'paddleocr'
                    })
            
            return elements
        except Exception as e:
            logger.error(f"PaddleOCR extraction failed: {e}")
            return []
    
    def extract_text_tesseract(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Extract text using Tesseract"""
        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            elements = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # Confidence threshold
                    text = data['text'][i].strip()
                    if text:  # Only include non-empty text
                        bounding_box = BoundingBox(
                            x1=data['left'][i],
                            y1=data['top'][i],
                            x2=data['left'][i] + data['width'][i],
                            y2=data['top'][i] + data['height'][i]
                        )
                        
                        elements.append({
                            'bounding_box': bounding_box.coordinates,
                            'text': text,
                            'confidence': float(data['conf'][i]) / 100.0,
                            'engine': 'tesseract'
                        })
            
            return elements
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            return []
    
    def extract_text_easyocr(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Extract text using EasyOCR"""
        try:
            results = self.ocr_instances['easyocr'].readtext(image)
            
            elements = []
            for (bbox, text, confidence) in results:
                # Convert bbox format
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                bounding_box = BoundingBox(
                    x1=int(min(x_coords)),
                    y1=int(min(y_coords)),
                    x2=int(max(x_coords)),
                    y2=int(max(y_coords))
                )
                
                elements.append({
                    'bounding_box': bounding_box.coordinates,
                    'text': text.strip(),
                    'confidence': float(confidence),
                    'engine': 'easyocr'
                })
            
            return elements
        except Exception as e:
            logger.error(f"EasyOCR extraction failed: {e}")
            return []
    
    def extract_text_trocr(self, image: np.ndarray, bboxes: List[BoundingBox]) -> List[Dict[str, Any]]:
        """Extract text using TrOCR for specific bounding boxes"""
        if 'trocr' not in self.ocr_instances:
            return []
        
        try:
            elements = []
            pil_image = Image.fromarray(image)
            
            for bbox in bboxes:
                # Crop the region
                cropped = pil_image.crop((bbox.x1, bbox.y1, bbox.x2, bbox.y2))
                
                # Process with TrOCR
                pixel_values = self.trocr_processor(cropped, return_tensors="pt").pixel_values
                generated_ids = self.trocr_model.generate(pixel_values)
                generated_text = self.trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                
                elements.append({
                    'bounding_box': bbox.coordinates,
                    'text': generated_text.strip(),
                    'confidence': 0.9,  # TrOCR doesn't provide confidence scores
                    'engine': 'trocr'
                })
            
            return elements
        except Exception as e:
            logger.error(f"TrOCR extraction failed: {e}")
            return []
    
    def extract_text(self, image: np.ndarray, engine: str = 'paddleocr') -> List[Dict[str, Any]]:
        """Extract text using specified engine"""
        if engine == 'paddleocr' and 'paddleocr' in self.ocr_instances:
            return self.extract_text_paddleocr(image)
        elif engine == 'tesseract' and 'tesseract' in self.ocr_instances:
            return self.extract_text_tesseract(image)
        elif engine == 'easyocr' and 'easyocr' in self.ocr_instances:
            return self.extract_text_easyocr(image)
        else:
            logger.warning(f"Engine {engine} not available, falling back to available engines")
            for available_engine in self.engines:
                if available_engine in self.ocr_instances:
                    return self.extract_text(image, available_engine)
            return []