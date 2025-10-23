import os
import logging
import re
from typing import Dict, Any, List, Optional
from enum import Enum

from .aws_textract_service import AWSTextractService
# from .layout_analysis.surya_processor import SuryaDocumentProcessor  # Removed - AWS only

logger = logging.getLogger(__name__)

class OCRProvider(str, Enum):
    """OCR provider options"""
    AWS_TEXTRACT = "aws_textract"
    SURYA = "surya"

class OCRService:
    """
    Unified OCR service that can use either AWS Textract or Surya
    """
    
    def __init__(self, provider: OCRProvider = None):
        """
        Initialize OCR service with specified provider
        
        Args:
            provider: OCR provider to use (defaults to AWS if credentials available, else Surya)
        """
        self.provider = provider or self._determine_default_provider()
        self.aws_service = None
        self.surya_service = None
        
        # Initialize the selected provider
        if self.provider == OCRProvider.AWS_TEXTRACT:
            self._init_aws_textract()
        else:
            self._init_surya()
        
        logger.info(f"OCR Service initialized with provider: {self.provider}")
    
    def _determine_default_provider(self) -> OCRProvider:
        """Determine which OCR provider to use by default"""
        # Check if AWS credentials are available
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        if aws_access_key and aws_secret_key:
            logger.info("AWS credentials found, defaulting to AWS Textract")
            return OCRProvider.AWS_TEXTRACT
        else:
            logger.info("No AWS credentials found, defaulting to Surya")
            return OCRProvider.SURYA
    
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
            logger.info("Falling back to Surya processor")
            self.provider = OCRProvider.SURYA
            self._init_surya()
    
    def _init_surya(self):
        """Initialize Surya processor"""
        try:
            self.surya_service = SuryaDocumentProcessor(preprocess_scanned=True)
            logger.info("Surya processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Surya processor: {e}")
            raise
    
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
            if self.provider == OCRProvider.AWS_TEXTRACT and self.aws_service:
                return self._process_with_aws(file_path, document_id)
            else:
                return self._process_with_surya(file_path, document_id)
                
        except Exception as e:
            logger.error(f"OCR processing failed with {self.provider}: {e}")
            
            # Fallback to alternative provider if available
            if self.provider == OCRProvider.AWS_TEXTRACT and not self.surya_service:
                logger.info("Attempting fallback to Surya processor")
                self._init_surya()
                return self._process_with_surya(file_path, document_id)
            elif self.provider == OCRProvider.SURYA and not self.aws_service:
                logger.info("Attempting fallback to AWS Textract")
                self._init_aws_textract()
                if self.aws_service:
                    return self._process_with_aws(file_path, document_id)
            
            raise
    
    def _process_with_aws(self, file_path: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Process document with AWS Textract"""
        logger.info(f"Processing document with AWS Textract: {file_path}")
        
        # Process with layout analysis for better results
        all_pages_elements = self.aws_service.process_document(
            file_path, 
            document_id, 
            use_layout_analysis=True
        )
        
        # Extract full text
        extracted_text = ""
        total_elements = 0
        
        for page_elements in all_pages_elements:
            page_text = []
            for element in page_elements:
                if element.get('extracted_text'):
                    page_text.append(element['extracted_text'])
            extracted_text += "\n".join(page_text) + "\n\n"
            total_elements += len(page_elements)
        
        # Calculate average confidence
        all_confidences = []
        for page_elements in all_pages_elements:
            for element in page_elements:
                if element.get('confidence'):
                    all_confidences.append(element['confidence'])
        
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        # Check for tables and images (basic detection)
        has_tables = any(
            element.get('element_type') == 'table' 
            for page_elements in all_pages_elements 
            for element in page_elements
        )
        
        return {
            'extracted_text': self._clean_text_for_search(extracted_text.strip()),
            'searchable_content': self._clean_text_for_search(extracted_text.strip()),
            'layout_sections': {
                'pages': all_pages_elements,
                'total_pages': len(all_pages_elements),
                'total_elements': total_elements
            },
            'ocr_confidence_score': avg_confidence,
            'has_tables': has_tables,
            'has_images': False,  # AWS Textract doesn't detect embedded images
            'provider': 'aws_textract'
        }
    
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
        
        for page_elements in all_pages_elements:
            page_text = []
            for element in page_elements:
                if element.get('extracted_text'):
                    page_text.append(element['extracted_text'])
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
            'layout_sections': {
                'pages': all_pages_elements,
                'total_pages': len(all_pages_elements),
                'total_elements': total_elements
            },
            'ocr_confidence_score': avg_confidence,
            'has_tables': has_tables,
            'has_images': has_images,
            'provider': 'surya'
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
