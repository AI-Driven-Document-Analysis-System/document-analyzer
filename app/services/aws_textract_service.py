import boto3
import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)

class AWSTextractService:
    """
    AWS Textract service for fast cloud-based OCR processing
    """
    
    def __init__(self, aws_access_key_id: str = None, aws_secret_access_key: str = None, region_name: str = 'us-east-1'):
        """
        Initialize AWS Textract client
        
        Args:
            aws_access_key_id: AWS access key (if None, uses environment/IAM)
            aws_secret_access_key: AWS secret key (if None, uses environment/IAM)
            region_name: AWS region for Textract
        """
        try:
            if aws_access_key_id and aws_secret_access_key:
                self.textract_client = boto3.client(
                    'textract',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=region_name
                )
            else:
                # Use environment variables or IAM role
                self.textract_client = boto3.client('textract', region_name=region_name)
            
            logger.info(f"AWS Textract client initialized for region: {region_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS Textract client: {e}")
            raise
    
    def convert_image_to_bytes(self, image_path: str) -> bytes:
        """Convert image file to bytes for Textract"""
        try:
            with open(image_path, 'rb') as image_file:
                return image_file.read()
        except Exception as e:
            logger.error(f"Error reading image file {image_path}: {e}")
            raise
    
    def process_single_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process a single image with AWS Textract
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Textract response with detected text and layout
        """
        try:
            # Use detect_document_text for basic OCR
            response = self.textract_client.detect_document_text(
                Document={'Bytes': image_bytes}
            )
            
            logger.info(f"Textract processed image with {len(response.get('Blocks', []))} blocks")
            return response
            
        except Exception as e:
            logger.error(f"Error processing image with Textract: {e}")
            raise
    
    def process_document_with_layout(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process document with layout analysis using AWS Textract
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Textract response with layout analysis
        """
        try:
            # Use analyze_document for layout analysis
            response = self.textract_client.analyze_document(
                Document={'Bytes': image_bytes},
                FeatureTypes=['LAYOUT', 'TABLES']  # Include layout and table detection
            )
            
            logger.info(f"Textract analyzed document with {len(response.get('Blocks', []))} blocks")
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing document with Textract: {e}")
            raise
    
    def extract_text_from_response(self, textract_response: Dict[str, Any]) -> str:
        """
        Extract plain text from Textract response
        
        Args:
            textract_response: Response from Textract API
            
        Returns:
            Extracted text as string
        """
        try:
            text_blocks = []
            
            for block in textract_response.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    text_blocks.append(block.get('Text', ''))
            
            extracted_text = '\n'.join(text_blocks)
            logger.info(f"Extracted {len(extracted_text)} characters of text")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from Textract response: {e}")
            return ""
    
    def extract_layout_elements(self, textract_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract layout elements from Textract response in Surya-compatible format
        
        Args:
            textract_response: Response from Textract API
            
        Returns:
            List of layout elements compatible with existing database structure
        """
        try:
            elements = []
            
            for block in textract_response.get('Blocks', []):
                if block['BlockType'] in ['LINE', 'WORD']:
                    # Convert Textract bounding box to our format
                    bbox = block.get('Geometry', {}).get('BoundingBox', {})
                    
                    # Textract uses relative coordinates (0-1), convert to absolute if needed
                    element = {
                        "bounding_box": [
                            bbox.get('Left', 0),
                            bbox.get('Top', 0), 
                            bbox.get('Left', 0) + bbox.get('Width', 0),
                            bbox.get('Top', 0) + bbox.get('Height', 0)
                        ],
                        "element_type": block['BlockType'].lower(),
                        "extracted_text": block.get('Text', ''),
                        "confidence": block.get('Confidence', 0) / 100.0  # Convert to 0-1 scale
                    }
                    elements.append(element)
            
            logger.info(f"Extracted {len(elements)} layout elements")
            return elements
            
        except Exception as e:
            logger.error(f"Error extracting layout elements: {e}")
            return []
    
    def process_document(self, file_path: str, document_id: Optional[str] = None, 
                        use_layout_analysis: bool = True) -> List[List[Dict[str, Any]]]:
        """
        Process a complete document using AWS Textract
        
        Args:
            file_path: Path to the document file
            document_id: Unique identifier for the document
            use_layout_analysis: Whether to use layout analysis (slower but more detailed)
            
        Returns:
            List of pages with extracted elements (compatible with Surya format)
        """
        if document_id is None:
            document_id = str(uuid.uuid4())
        
        try:
            file_extension = Path(file_path).suffix.lower()
            
            # Handle different file types
            if file_extension == ".pdf":
                # Convert PDF to images and process with Textract (more reliable)
                logger.info(f"Converting PDF to images for AWS Textract processing")
                
                # Convert PDF to images using pdf2image with poppler path
                try:
                    from pdf2image import convert_from_path
                    import os
                    
                    # Use local poppler installation
                    poppler_path = os.path.join(os.getcwd(), "poppler", "poppler-23.01.0", "Library", "bin")
                    
                    if os.path.exists(poppler_path):
                        images = convert_from_path(file_path, dpi=200, fmt='PNG', poppler_path=poppler_path)
                    else:
                        # Fallback to system poppler
                        images = convert_from_path(file_path, dpi=200, fmt='PNG')
                    
                    logger.info(f"Converted PDF to {len(images)} images")
                except ImportError:
                    raise Exception("pdf2image library required for PDF processing. Install with: pip install pdf2image")
                
                all_pages_elements = []
                
                for i, image in enumerate(images):
                    logger.info(f"Processing page {i+1}/{len(images)} with AWS Textract")
                    
                    # Convert PIL image to bytes
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    image_bytes = img_byte_arr.getvalue()
                    
                    # Check image size (AWS Textract limit is 10MB)
                    if len(image_bytes) > 10 * 1024 * 1024:
                        # Compress image if too large
                        image = image.resize((int(image.width * 0.8), int(image.height * 0.8)), Image.Resampling.LANCZOS)
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG', optimize=True)
                        image_bytes = img_byte_arr.getvalue()
                    
                    # Process with Textract
                    if use_layout_analysis:
                        response = self.process_document_with_layout(image_bytes)
                    else:
                        response = self.process_single_image(image_bytes)
                    
                    # Extract elements in our format
                    page_elements = self.extract_layout_elements(response)
                    all_pages_elements.append(page_elements)
                
                logger.info(f"AWS Textract PDF processing completed. Total pages: {len(all_pages_elements)}")
                return all_pages_elements
                
            elif file_extension in [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]:
                # Process single image
                image_bytes = self.convert_image_to_bytes(file_path)
                
                if use_layout_analysis:
                    response = self.process_document_with_layout(image_bytes)
                else:
                    response = self.process_single_image(image_bytes)
                
                elements = self.extract_layout_elements(response)
                logger.info(f"AWS Textract processing completed. Elements: {len(elements)}")
                
                return [elements]  # Return as single page
                
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error processing document {file_path} with AWS Textract: {e}")
            raise
    
    def get_extracted_text(self, file_path: str) -> str:
        """
        Quick method to get just the extracted text without layout info
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text as string
        """
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension in [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]:
                image_bytes = self.convert_image_to_bytes(file_path)
                response = self.process_single_image(image_bytes)
                return self.extract_text_from_response(response)
            else:
                # For PDFs, process first page only for quick text extraction
                from .surya_processor import SuryaDocumentProcessor
                surya_processor = SuryaDocumentProcessor()
                images = surya_processor.convert_pdf_to_images(file_path, dpi=150)
                
                if images:
                    img_byte_arr = io.BytesIO()
                    images[0].save(img_byte_arr, format='PNG')
                    image_bytes = img_byte_arr.getvalue()
                    
                    response = self.process_single_image(image_bytes)
                    return self.extract_text_from_response(response)
                
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""
