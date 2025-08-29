import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
import cv2
import numpy as np
import pdf2image

from .ocr_engine import OCREngine
from .layout import LayoutAnalyzer
from .table_extractor import TableExtractor
from .document_element import DocumentElement


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main document processing class that orchestrates OCR and layout analysis"""
    
    def __init__(self, db_config: Optional[Dict] = None, use_postgres: bool = False):
        # Initialize components
        self.preprocessor = DocumentPreprocessor()
        self.ocr_engine = OCREngine(['paddleocr', 'tesseract'])
        self.layout_analyzer = LayoutAnalyzer()
        self.table_extractor = TableExtractor()
        
        # Initialize database
        self.db_manager = DatabaseManager(
            db_path="document_analysis.db",
            use_postgres=use_postgres,
            postgres_config=db_config
        )
        
        logger.info("Document processor initialized successfully")
    
    def convert_pdf_to_images(self, pdf_path: str, dpi: int = 200) -> List[np.ndarray]:
        """Convert PDF pages to images"""
        try:
            images = pdf2image.convert_from_path(
                pdf_path,
                dpi=dpi,
                fmt='RGB'
            )
            
            # Convert PIL images to numpy arrays
            numpy_images = []
            for img in images:
                numpy_img = np.array(img)
                numpy_images.append(numpy_img)
            
            logger.info(f"Converted PDF to {len(numpy_images)} images")
            return numpy_images
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return []
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load image file"""
        try:
            image = cv2.imread(image_path)
            if image is not None:
                # Convert BGR to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                return image
            return None
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None
    
    def process_single_page(self, image: np.ndarray, page_number: int) -> List[DocumentElement]:
        """Process a single page/image"""
        try:
            # Step 1: Preprocess image
            enhanced_image = self.preprocessor.enhance_image(image)
            corrected_image = self.preprocessor.correct_skew(enhanced_image)
            
            # Step 2: OCR extraction
            logger.info(f"Extracting text from page {page_number}")
            ocr_results = self.ocr_engine.extract_text(corrected_image, engine='paddleocr')
            
            if not ocr_results:
                logger.warning(f"No text extracted from page {page_number}")
                return []
            
            # Step 3: Layout analysis
            logger.info(f"Analyzing layout for page {page_number}")
            layout_elements = self.layout_analyzer.analyze_layout(corrected_image, ocr_results)
            
            # Step 4: Table extraction
            logger.info(f"Extracting tables from page {page_number}")
            table_elements = self.table_extractor.extract_tables(corrected_image, layout_elements)
            
            # Combine all elements
            all_elements = layout_elements + table_elements
            
            # Convert to DocumentElement objects
            document_elements = []
            for element in all_elements:
                doc_element = DocumentElement(
                    page_number=page_number,
                    bounding_box=element['bounding_box'],
                    extracted_text=element.get('text', element.get('extracted_text', '')),
                    element_type=element['element_type'],
                    confidence=element['confidence'],
                    metadata=element.get('metadata', {})
                )
                document_elements.append(doc_element)
            
            logger.info(f"Processed page {page_number}: {len(document_elements)} elements extracted")
            return document_elements
            
        except Exception as e:
            logger.error(f"Error processing page {page_number}: {e}")
            return []
    
    def process_document(self, file_path: str, document_id: Optional[str] = None) -> str:
        """Process entire document (PDF or image)"""
        if document_id is None:
            document_id = str(uuid.uuid4())
        
        try:
            filename = os.path.basename(file_path)
            file_extension = Path(file_path).suffix.lower()
            
            # Determine if it's a PDF or image
            if file_extension == '.pdf':
                images = self.convert_pdf_to_images(file_path)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                image = self.load_image(file_path)
                images = [image] if image is not None else []
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            if not images:
                raise ValueError("No images to process")
            
            # Create document entry in database
            self.db_manager.create_document(document_id, filename, len(images))
            
            all_elements = []
            
            # Process each page
            for page_num, image in enumerate(images, 1):
                logger.info(f"Processing page {page_num}/{len(images)}")
                
                page_elements = self.process_single_page(image, page_num)
                all_elements.extend(page_elements)
                
                # Store page elements in database
                if page_elements:
                    self.db_manager.store_elements(document_id, page_elements)
            
            # Update document status
            status = "completed" if all_elements else "failed"
            self.db_manager.update_document_status(document_id, status)
            
            logger.info(f"Document processing completed. Total elements: {len(all_elements)}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            if document_id:
                self.db_manager.update_document_status(document_id, "failed")
            raise
    
    def get_document_results(self, document_id: str, page_number: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve processed document results"""
        try:
            elements = self.db_manager.get_document_elements(document_id, page_number)
            
            result = {
                'document_id': document_id,
                'total_elements': len(elements),
                'elements': elements
            }
            
            if page_number:
                result['page_number'] = page_number
            
            # Group elements by type
            element_types = {}
            for element in elements:
                elem_type = element['element_type']
                if elem_type not in element_types:
                    element_types[elem_type] = 0
                element_types[elem_type] += 1
            
            result['element_types_count'] = element_types
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving document results: {e}")
            return {
                'document_id': document_id,
                'error': str(e)
            }
    
    def close(self):
        """Clean up resources"""
        self.db_manager.close()