from PIL import Image
import pdf2image
from transformers import LayoutLMv3FeatureExtractor, LayoutLMv3TokenizerFast, LayoutLMv3Processor, LayoutLMv3ForSequenceClassification
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentClassifier:
    """Class to classify document types based on layout and text content"""
    def __init__(self):
        self.feature_extractor = LayoutLMv3FeatureExtractor(apply_ocr=True)
        self.tokenizer = LayoutLMv3TokenizerFast.from_pretrained(
            "microsoft/layoutlmv3-base"
        )
        self.processor = LayoutLMv3Processor(self.feature_extractor, self.tokenizer)
        self.model = LayoutLMv3ForSequenceClassification.from_pretrained("RavindiG/layoutlmv3-document-classification")

        self.id2label = { 0: 'Financial Report', 1: 'Handwritten', 2: 'Invoice', 3: 'Medical Record', 4: 'Quesionnaire', 5: 'Research Paper', 6: 'Resume', 7: 'Scientific Report'}

    
    def predict_document_image(self, image):

        # prepare image for the model
        encoded_inputs = self.processor(image, max_length=512, return_tensors="pt")

        # make sure all keys of encoded_inputs are on the same device as the model
        for k,v in encoded_inputs.items():
            encoded_inputs[k] = v.to(self.model.device)

        # forward pass
        outputs = self.model(**encoded_inputs)

        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        print("Predicted index:", predicted_class_idx, "id2label keys:", list(id2label.keys()))
        return self.id2label[predicted_class_idx]

    def classify_document(self, file_path):
        """Classify document type based on layout and extracted text"""
        try:
            # Open the document (PDF or image)
            if file_path.lower().endswith('.pdf'):
                image = pdf2image.convert_from_path(
                    file_path,
                    dpi=120,
                    fmt="RGB",
                    first_page=1,
                    last_page=1
                )[0]
            else:
                image = Image.open(file_path)
            
            # Predict document type
            doc_type = self.predict_document_image(image)
            
            return doc_type
        
        except Exception as e:
            logger.error(f"Error classifying document {file_path}: {e}")
            return "unknown", 0.0

        