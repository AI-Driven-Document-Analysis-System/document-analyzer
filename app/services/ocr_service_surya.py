import os
import logging
import re
from typing import Dict, Any, List, Optional
from enum import Enum

from .layout_analysis.surya_processor import SuryaDocumentProcessor  
from .aws_textract_service import AWSTextractService


logger = logging.getLogger(__name__)

class OCRProvider(str, Enum):
    """OCR provider options"""
    SURYA = "surya"
    AWS_TEXTRACT = "aws_textract"

class OCRService:
    """
    Surya-only OCR service
    """

    def __init__(self, provider: OCRProvider = OCRProvider.SURYA):
        """
        Initialize OCR service with Surya 
        
        Args:
            provider: OCR provider to use (defaults to Surya)
        """
        self.provider = provider 
        self.surya_service = None
        self.aws_service = None
        
        # Initialize the Surya processor
        self._init_surya()
        
        logger.info(f"OCR Service initialized with provider: {self.provider}")
    
    def _init_surya(self):
        """Initialize Surya processor"""
        try:
            self.surya_service = SuryaDocumentProcessor(preprocess_scanned=True)
            logger.info("Surya processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Surya processor: {e}")
            logger.info("Falling back to AWS Textract")
            self.provider = OCRProvider.AWS_TEXTRACT
            self._init_aws_textract()
    
    def _init_aws_textract(self):
        """Initialize AWS Textract service"""
        try:
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_region = os.getenv("AWS_REGION", "us-east-1")
            
            self.aws_service = AWSTextractService(
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
            logger.info("AWS Textract service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS Textract: {e}")
    
    
    def process_document(self, file_path: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process document using the configured OCR provider
        
        Args:
            file_path: Path to the document file
            document_id: Unique identifier for the document
            
        Returns:
            Dictionary containing extracted text, layout elements, and metadata
        """
        try:
            if not self.surya_service:
                raise RuntimeError("Surya processor not initialized")
            
            return self._process_with_surya(file_path, document_id)
        
        except Exception as e:
            logger.error(f"OCR processing failed with {self.provider}: {e}")
            
            # Fallback to the other provider if available
            if self.provider == OCRProvider.SURYA and self.aws_service:
                logger.info("Falling back to AWS Textract")
                return self._process_with_aws(file_path, document_id)
            
    def _process_with_surya(self, file_path: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Process document with Surya"""
        logger.info(f"Processing document with Surya: {file_path}")
        
        all_pages_elements = self.surya_service.process_document(
            file_path, 
            document_id
        )
        
        # Extract full text
        extracted_text = ""
        total_elements = 0
        layout_sections = []
        
        for page_elements in all_pages_elements:
            page_text = []
            for element in page_elements:
                if element.get('extracted_text'):
                    page_text.append(element['extracted_text'])
                layout_sections.append({
                "page_number": element.get("page_number"),
                "element_type": element.get("element_type"),
                "bounding_box": element.get("bounding_box"),
                "text": element.get("extracted_text"),
                "confidence": element.get("confidence") 
                })
            extracted_text += "\n".join(page_text) + "\n\n"
            total_elements += len(page_elements)
        
        # Calculate average confidence
        all_confidences = []
        for page_elements in all_pages_elements:
            for element in page_elements:
                if element.get('confidence'):
                    all_confidences.append(element['confidence'])
        
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        # Check for tables and images
        has_tables = any(
            'table' in element.get('element_type', '').lower()
            for page_elements in all_pages_elements 
            for element in page_elements
        )
        
        has_images = any(
            'image' in element.get('element_type', '').lower() or 'figure' in element.get('element_type', '').lower()
            for page_elements in all_pages_elements 
            for element in page_elements
        )
        
        return {
            'extracted_text': self._clean_text_for_search(extracted_text.strip()),
            'searchable_content': self._clean_text_for_search(extracted_text.strip()),
            'layout_sections': layout_sections,
            'ocr_confidence_score': avg_confidence,
            'has_tables': has_tables,
            'has_images': has_images,
            'provider': 'surya',
            'document_id': document_id,
            'processing_metadata': {
                'file_path': file_path,
                'provider': 'surya',
                'success': True
            }
        }
        
    
    def _process_with_aws(self, file_path: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Process document with AWS Textract"""
        logger.info(f"Processing document with AWS Textract: {file_path}")
        
        # Use AWS Textract service - process_document returns pages with layout elements
        pages = self.aws_service.process_document(file_path, document_id, use_layout_analysis=True)
        
        # Aggregate text from all pages
        text_parts = []
        layout_sections = []
        confidences = []
        has_tables = False
        has_images = False
        
        for page_num, page in enumerate(pages, start=1):
            for elem in page:
                txt = elem.get("extracted_text") or ""
                if txt:
                    text_parts.append(txt)
                conf = elem.get("confidence")
                if conf is not None:
                    confidences.append(conf)
                etype = (elem.get("element_type") or "").lower()
                if "table" in etype:
                    has_tables = True
                if any(k in etype for k in ["image", "figure"]):
                    has_images = True
                layout_sections.append({
                    "page_number": page_num,
                    "element_type": elem.get("element_type"),
                    "bounding_box": elem.get("bounding_box"),
                    "text": txt,
                    "confidence": conf
                })
        
        full_text = "\n".join(text_parts) if text_parts else ""
        avg_conf = sum(confidences)/len(confidences) if confidences else 0.0
        
        # Format result for consistency
        return {
            'extracted_text': self._clean_text_for_search(full_text),
            'searchable_content': self._clean_text_for_search(full_text),
            'layout_sections': layout_sections,
            'ocr_confidence_score': avg_conf,
            'has_tables': has_tables,
            'has_images': has_images,
            'provider': 'aws_textract',
            'document_id': document_id,
            'processing_metadata': {
                'file_path': file_path,
                'provider': 'aws_textract',
                'success': True
            }
        }
    
    
    def _clean_text_for_search(self, text: str) -> str:
        """
        Clean extracted text for better search functionality.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text suitable for search indexing
        """
        if not text:
            return ""
        
        # Fix word-per-line format by reconstructing sentences
        text = self._reconstruct_sentences(text)
        
        # Remove excessive whitespace and normalize line breaks
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = ' '.join(lines)
        
        # Remove multiple spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text.strip()
    
    def _reconstruct_sentences(self, text: str) -> str:
        """
        Reconstruct proper sentences from word-per-line OCR format.
        
        Args:
            text: Raw OCR text with potential word-per-line format
            
        Returns:
            Text with reconstructed sentences
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        reconstructed_lines = []
        current_sentence = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # If line is a single word or very short, likely part of fragmented sentence
            if len(line.split()) <= 2 and len(line) < 20:
                current_sentence.append(line)
            else:
                # Complete sentence or paragraph
                if current_sentence:
                    # Join accumulated words and add to result
                    reconstructed_lines.append(' '.join(current_sentence))
                    current_sentence = []
                reconstructed_lines.append(line)
        
        # Add any remaining accumulated words
        if current_sentence:
            reconstructed_lines.append(' '.join(current_sentence))
        
        return '\n'.join(reconstructed_lines)

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current OCR provider"""
        return {
            'provider': self.provider,
            'aws_available': self.aws_service is not None,
            'surya_available': self.surya_service is not None
        }
