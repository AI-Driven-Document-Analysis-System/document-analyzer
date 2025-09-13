import os
import logging
from typing import Dict, Any, List, Optional
from enum import Enum

from .aws_textract_service import AWSTextractService

logger = logging.getLogger(__name__)

class OCRProvider(str, Enum):
    """OCR provider options"""
    AWS_TEXTRACT = "aws_textract"

class OCRService:
    """
    AWS-only OCR service using Textract
    """
    
    def __init__(self, provider: OCRProvider = OCRProvider.AWS_TEXTRACT):
        """
        Initialize OCR service with AWS Textract
        
        Args:
            provider: OCR provider to use (AWS Textract only)
        """
        self.provider = provider
        self.aws_service = None
        
        # Initialize AWS Textract service
        self._init_aws_textract()
    
    def _init_aws_textract(self):
        """Initialize AWS Textract service"""
        try:
            # Check for AWS credentials
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            
            if not aws_access_key or not aws_secret_key:
                raise ValueError("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
            
            self.aws_service = AWSTextractService()
            logger.info("AWS Textract service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS Textract: {e}")
            raise
    
    def process_document(self, file_path: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process document using AWS Textract
        
        Args:
            file_path: Path to the document file
            document_id: Optional document ID for tracking
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            logger.info(f"Processing document with AWS Textract: {file_path}")
            
            if not self.aws_service:
                raise RuntimeError("AWS Textract service not initialized")
            
            return self._process_with_aws_textract(file_path, document_id)
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise
    
    def _process_with_aws_textract(self, file_path: str, document_id: Optional[str] = None) -> Dict[str, Any]:
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
            'extracted_text': full_text,
            'searchable_content': full_text,
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
