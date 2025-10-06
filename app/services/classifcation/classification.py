from PIL import Image
import pdf2image
from transformers import LayoutLMv3FeatureExtractor, LayoutLMv3TokenizerFast, LayoutLMv3Processor, LayoutLMv3ForSequenceClassification
import torch
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentClassifier:
    """Class to classify document types based on layout and text content"""
    def __init__(self):
        try:
            self.feature_extractor = LayoutLMv3FeatureExtractor()
            self.tokenizer = LayoutLMv3TokenizerFast.from_pretrained(
                "microsoft/layoutlmv3-base"
            )
            self.processor = LayoutLMv3Processor(self.feature_extractor, self.tokenizer)
            self.model = LayoutLMv3ForSequenceClassification.from_pretrained(
                "RavindiG/layoutlmv3-document-classification"
            )
            self.model.eval()  # Set to evaluation mode

            self.id2label = { 
                0: 'Financial Report', 
                1: 'Handwritten', 
                2: 'Invoice', 
                3: 'Medical Record', 
                4: 'Questionnaire',  
                5: 'Research Paper', 
                6: 'Resume', 
                7: 'Scientific Report'
            }

            logger.info("DocumentClassifier initialized successfully.")
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            logger.error(traceback.format_exc())
            raise

    
    def predict_document_class(self, image):
        try:
            logger.info(f"Image size: {image.size}, mode: {image.mode}")
            
            # Convert image to RGB if needed
            if image.mode != 'RGB':
                logger.info(f"Converting image from {image.mode} to RGB")
                image = image.convert('RGB')
            
            # Prepare image for the model
            logger.info("Processing image...")
            encoded_inputs = self.processor(image, max_length=512, return_tensors="pt")

            # Move inputs to same device as model
            device = next(self.model.parameters()).device
            
            for k, v in encoded_inputs.items():
                encoded_inputs[k] = v.to(device)

            # Forward pass
            logger.info("Running model inference...")
            with torch.no_grad():  # Disable gradient computation for inference
                outputs = self.model(**encoded_inputs)

            logits = outputs.logits
            logger.info(f"Logits shape: {logits.shape}, values: {logits}")
            
            predicted_class_idx = logits.argmax(-1).item()
            logger.info(f"Predicted index: {predicted_class_idx}")
            
            predicted_label = self.id2label[predicted_class_idx]
            logger.info(f"Predicted label: {predicted_label}")
            
            return predicted_label
            
        except Exception as e:
            logger.error(f"Error in predict_document_class: {e}")
            logger.error(traceback.format_exc())
            raise

    def classify_document(self, file_path):
        """Classify document type based on layout and extracted text"""
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Open the document (PDF or image)
            if file_path.lower().endswith('.pdf'):
                logger.info("Converting PDF to image...")
                images = pdf2image.convert_from_path(
                    file_path,
                    dpi=120,
                    fmt="RGB",
                    first_page=1,
                    last_page=1
                )
                if not images:
                    raise ValueError("No images extracted from PDF")
                image = images[0]
                logger.info(f"PDF converted successfully, image size: {image.size}")
            else:
                logger.info("Opening image file...")
                image = Image.open(file_path)
                logger.info(f"Image opened successfully, size: {image.size}")
            
            # Predict document type
            doc_type = self.predict_document_class(image)
            
            logger.info(f"Classification successful: {doc_type}")
            return doc_type
        
        except Exception as e:
            logger.error(f"Error classifying document {file_path}: {e}")
            logger.error(traceback.format_exc())
            return "unknown"


