import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import (
    LayoutLMv3Processor,
    LayoutLMv3ForTokenClassification,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LayoutAnalyzer:
    """Document layout analysis using LayoutLMv3 and DocFormer"""
    
    def __init__(self, model_name: str = "microsoft/layoutlmv3-base"):
        self.model_name = model_name
        self.processor = None
        self.model = None
        self.setup_model()
    
    def setup_model(self):
        """Initialize LayoutLM model"""
        try:
            self.processor = LayoutLMv3Processor.from_pretrained(self.model_name)
            self.model = LayoutLMv3ForTokenClassification.from_pretrained(self.model_name)
            logger.info(f"LayoutLM model {self.model_name} loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load LayoutLM model: {e}")
            self.use_rule_based_layout = True
    
    def analyze_layout_rule_based(self, image: np.ndarray, ocr_results: List[Dict]) -> List[Dict[str, Any]]:
        """Rule-based layout analysis as fallback"""
        layout_elements = []
        
        if not ocr_results:
            return layout_elements
        
        # Group OCR results by vertical proximity
        sorted_results = sorted(ocr_results, key=lambda x: (x['bounding_box'][1], x['bounding_box'][0]))
        
        current_line = []
        current_y = sorted_results[0]['bounding_box'][1]
        line_threshold = 20  # Pixels
        
        for result in sorted_results:
            bbox = result['bounding_box']
            
            # Check if this element is on the same line
            if abs(bbox[1] - current_y) < line_threshold:
                current_line.append(result)
            else:
                # Process current line
                if current_line:
                    layout_elements.extend(self.classify_line_elements(current_line, image.shape))
                
                current_line = [result]
                current_y = bbox[1]
        
        # Process the last line
        if current_line:
            layout_elements.extend(self.classify_line_elements(current_line, image.shape))
        
        return layout_elements
    
    def classify_line_elements(self, line_elements: List[Dict], image_shape: Tuple) -> List[Dict[str, Any]]:
        """Classify elements in a line based on position and characteristics"""
        classified_elements = []
        
        for element in line_elements:
            bbox = element['bounding_box']
            text = element['text']
            
            # Simple classification rules
            element_type = self.classify_element_type(text, bbox, image_shape)
            
            classified_elements.append({
                'bounding_box': bbox,
                'text': text,
                'element_type': element_type,
                'confidence': element['confidence'],
                'metadata': {
                    'engine': element.get('engine', 'unknown'),
                    'classification_method': 'rule_based'
                }
            })
        
        return classified_elements
    
    def classify_element_type(self, text: str, bbox: List[int], image_shape: Tuple) -> str:
        """Classify element type based on text and position characteristics"""
        height, width = image_shape[:2]
        
        # Calculate relative position
        rel_x = bbox[0] / width
        rel_y = bbox[1] / height
        
        # Element dimensions
        elem_width = bbox[2] - bbox[0]
        elem_height = bbox[3] - bbox[1]
        
        # Classification logic
        if rel_y < 0.1:
            return "header"
        elif rel_y > 0.9:
            return "footer"
        elif len(text) > 100:
            return "paragraph"
        elif text.isupper() and len(text.split()) <= 5:
            return "title"
        elif any(keyword in text.lower() for keyword in ['table', 'figure', 'chart']):
            return "caption"
        elif elem_width / width > 0.8:
            return "paragraph"
        elif elem_height > 50 and elem_width > 200:
            return "paragraph"
        else:
            return "text"
    
    def analyze_layout_layoutlm(self, image: np.ndarray, ocr_results: List[Dict]) -> List[Dict[str, Any]]:
        """Advanced layout analysis using LayoutLM"""
        if not self.processor or not self.model:
            return self.analyze_layout_rule_based(image, ocr_results)
        
        try:
            # Prepare data for LayoutLM
            words = []
            boxes = []
            
            for result in ocr_results:
                words.append(result['text'])
                bbox = result['bounding_box']
                # Normalize bounding box coordinates
                normalized_box = [
                    int(bbox[0]), int(bbox[1]),
                    int(bbox[2]), int(bbox[3])
                ]
                boxes.append(normalized_box)
            
            if not words:
                return []
            
            # Convert image to PIL
            pil_image = Image.fromarray(image).convert('RGB')
            
            # Process with LayoutLM
            encoding = self.processor(
                pil_image,
                words,
                boxes=boxes,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            
            with torch.no_grad():
                outputs = self.model(**encoding)
                predictions = outputs.logits.argmax(-1).squeeze().tolist()
            
            # Map predictions to elements
            layout_elements = []
            label_map = {
                0: "other",
                1: "header",
                2: "question",
                3: "answer",
                4: "paragraph",
                5: "title"
            }
            
            for i, (word, box, pred) in enumerate(zip(words, boxes, predictions)):
                element_type = label_map.get(pred, "text")
                
                layout_elements.append({
                    'bounding_box': box,
                    'text': word,
                    'element_type': element_type,
                    'confidence': 0.85,  # LayoutLM doesn't provide direct confidence
                    'metadata': {
                        'engine': 'layoutlm',
                        'prediction_id': pred
                    }
                })
            
            return layout_elements
            
        except Exception as e:
            logger.error(f"LayoutLM analysis failed: {e}")
            return self.analyze_layout_rule_based(image, ocr_results)
    
    def analyze_layout(self, image: np.ndarray, ocr_results: List[Dict]) -> List[Dict[str, Any]]:
        """Main layout analysis method"""
        if self.processor and self.model:
            return self.analyze_layout_layoutlm(image, ocr_results)
        else:
            return self.analyze_layout_rule_based(image, ocr_results)