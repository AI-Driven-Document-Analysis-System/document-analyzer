from typing import List, Dict, Any, Optional

class DocumentElement:
    """Represents an extracted document element"""
    page_number: int
    bounding_box: List[int]
    extracted_text: str
    element_type: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'page_number': self.page_number,
            'bounding_box': self.bounding_box,
            'extracted_text': self.extracted_text,
            'element_type': self.element_type,
            'confidence': self.confidence,
            'metadata': self.metadata or {}
        }
