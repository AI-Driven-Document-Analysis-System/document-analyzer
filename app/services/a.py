import json
import re
from typing import Dict, List, Tuple

# Mock T5 API for testing without authentication
class MockT5Summarizer:
    """Mock T5 summarizer for testing without API authentication."""
    
    @staticmethod
    def _extract_sentences(text: str, min_length: int = 15) -> List[str]:
        """Extract sentences from text."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > min_length]
    
    @staticmethod
    def _score_sentences(sentences: List[str], domain: str) -> List[Tuple[float, str]]:
        """Score sentences based on domain-relevant keywords."""
        keywords = {
            "medical": ["diagnosis", "treatment", "patient", "medication", "symptom", 
                       "hospital", "clinical", "disease", "condition", "admitted"],
            "legal": ["agreement", "contract", "plaintiff", "defendant", "court", 
                     "breach", "damages", "settlement", "clause", "litigation"],
            "financial": ["revenue", "profit", "investment", "dividend", "earnings", 
                         "stock", "fund", "cash flow", "equity", "debt"],
            "general": ["important", "key", "significant", "result", "concluded"]
        }
        
        domain_keywords = keywords.get(domain, keywords["general"])
        scored = []
        
        for i, sent in enumerate(sentences):
            sent_lower = sent.lower()
            # Position score (earlier sentences valued more)
            score = max(0, 10 - i) * 1.0
            # Keyword matches
            score += sum(3 for kw in domain_keywords if kw in sent_lower)
            # Length bonus (not too short, not too long)
            if 20 < len(sent) < 200:
                score += 2
            scored.append((score, sent))
        
        return sorted(scored, reverse=True)
    
    @staticmethod
    def brief_summary(text: str, domain: str) -> str:
        """Generate brief 2-3 sentence summary."""
        sentences = MockT5Summarizer._extract_sentences(text)
        if len(sentences) <= 2:
            return " ".join(sentences)
        
        scored = MockT5Summarizer._score_sentences(sentences, domain)
        selected = [s[1] for s in scored[:2]]
        return " ".join(selected)
    
    @staticmethod
    def detailed_summary(text: str, domain: str) -> str:
        """Generate detailed comprehensive summary."""
        sentences = MockT5Summarizer._extract_sentences(text)
        if len(sentences) <= 3:
            return " ".join(sentences)
        
        scored = MockT5Summarizer._score_sentences(sentences, domain)
        selected = [s[1] for s in scored[:4]]
        return " ".join(selected)
    
    @staticmethod
    def extract_entities(text: str, domain: str) -> Dict[str, List[str]]:
        """Extract entities using T5-style instruction following."""
        entities = {}
        
        # Extract capitalized name patterns (people)
        people = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', text)
        if people:
            entities["PERSON"] = list(set(people))[:5]
        
        # Extract organizations
        orgs = re.findall(
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Ltd|Inc|Corp|Hospital|Clinic|Bank|University|Institute)\b',
            text
        )
        if orgs:
            entities["ORGANIZATION"] = list(set(orgs))[:5]
        
        # Domain-specific entity extraction
        if domain == "medical":
            # Medical conditions
            conditions = re.findall(
                r'\b(?:anaemia|anemia|thalassaemia|thalassemia|diabetes|hypertension|'
                r'infection|cancer|arthritis|pneumonia|hepatitis|influenza)\b',
                text, re.IGNORECASE
            )
            if conditions:
                entities["MEDICAL_CONDITION"] = list(set(conditions))[:5]
            
            # Medications
            medications = re.findall(
                r'\b(?:[A-Z][a-z]+)?(?:cillin|mycin|statin|pril|formin|sulfate)\b',
                text
            )
            if medications:
                entities["MEDICATION"] = list(set(medications))[:5]
            
            # Body parts/anatomy
            anatomy = re.findall(
                r'\b(?:heart|liver|kidney|brain|lung|blood|hemoglobin|glucose)\b',
                text, re.IGNORECASE
            )
            if anatomy:
                entities["ANATOMY"] = list(set(anatomy))[:3]
        
        elif domain == "legal":
            # Legal parties
            parties = re.findall(
                r'\b(?:Plaintiff|Defendant|Party)\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|LLC|Corp|Ltd))?)\b',
                text
            )
            if parties:
                entities["LEGAL_PARTY"] = list(set(parties))[:5]
            
            # Legal concepts
            legal_terms = re.findall(
                r'\b(?:contract|agreement|breach|damages|settlement|clause|jurisdiction|'
                r'litigation|plaintiff|defendant|court|judge|lawsuit)\b',
                text, re.IGNORECASE
            )
            if legal_terms:
                entities["LEGAL_TERM"] = list(set(legal_terms))[:6]
            
            # Case/document identifiers
            case_nums = re.findall(r'\b(?:Case|Document|Reference)\s*[#:]?\s*([A-Z0-9\-]+)\b', text)
            if case_nums:
                entities["CASE_NUMBER"] = list(set(case_nums))[:3]
        
        elif domain == "financial":
            # Companies and funds
            companies = re.findall(
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Fund|Corp|Inc|Bank|Investment|Capital)\b',
                text
            )
            if companies:
                entities["COMPANY"] = list(set(companies))[:5]
            
            # Financial metrics
            financial_terms = re.findall(
                r'\b(?:revenue|profit|dividend|stock|equity|debt|earnings|cash flow|'
                r'investment|portfolio|fund|trading|market)\b',
                text, re.IGNORECASE
            )
            if financial_terms:
                entities["FINANCIAL_METRIC"] = list(set(financial_terms))[:6]
            
            # Amounts
            amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?|\d+\s*(?:million|billion|thousand)', text)
            if amounts:
                entities["AMOUNT"] = list(set(amounts))[:4]
        
        return entities

def detect_document_domain(text: str) -> str:
    """Detect document domain based on keyword frequency."""
    text_lower = text.lower()
    
    medical_kw = ["patient", "diagnosis", "treatment", "medication", "doctor", 
                  "hospital", "clinical", "disease", "anaemia", "hemoglobin"]
    legal_kw = ["contract", "agreement", "plaintiff", "defendant", "court", 
                "breach", "damages", "litigation", "lawsuit", "attorney"]
    financial_kw = ["investment", "revenue", "profit", "dividend", "stock", 
                    "fund", "earnings", "portfolio", "cash flow", "equity"]
    
    medical_score = sum(text_lower.count(kw) for kw in medical_kw)
    legal_score = sum(text_lower.count(kw) for kw in legal_kw)
    financial_score = sum(text_lower.count(kw) for kw in financial_kw)
    
    scores = {"medical": medical_score, "legal": legal_score, "financial": financial_score}
    domain = max(scores, key=scores.get)
    
    return domain if scores[domain] > 1 else "general"

def format_entities(entities: Dict[str, List[str]]) -> str:
    """Format extracted entities for display."""
    if not entities:
        return "No entities identified.\n"
    
    output = "\nEXTRACTED ENTITIES:\n"
    output += "=" * 50 + "\n"
    
    for entity_type in sorted(entities.keys()):
        entity_list = entities[entity_type]
        if entity_list:
            # Format entity type nicely
            formatted_type = entity_type.replace('_', ' ').title()
            output += f"\n{formatted_type}:\n"
            for entity in entity_list:
                output += f"  • {entity}\n"
    
    return output

def summarize_with_t5_instruction(text: str, summary_type: str = "brief") -> str:
    """
    Single T5 model with different instructions for each use case.
    summary_type: "brief", "detailed", or "domain_specific"
    """
    if not text or len(text.strip()) < 50:
        return "Error: Text too short to summarize (minimum 50 characters)."
    
    # Detect domain
    domain = detect_document_domain(text)
    print(f"✓ Detected domain: {domain}")
    print(f"✓ Summary type: {summary_type}\n")
    
    # T5 instructions for different tasks
    instructions = {
        "brief": "Summarize the following text in 2-3 sentences:\n\n",
        "detailed": "Provide a detailed and comprehensive summary of the following text, including all key points:\n\n",
        "domain_specific": f"You are analyzing a {domain} document. Extract all key entities (people, organizations, conditions, terms, amounts) and provide a structured summary:\n\n"
    }
    
    # Format input with instruction
    instruction = instructions.get(summary_type, instructions["brief"])
    input_text = instruction + text[:1500]  # Limit to 1500 chars for processing
    
    print(f"T5 Instruction: {instruction.strip()}\n")
    print("Processing...\n")
    
    result = ""
    
    # For domain-specific, include entity extraction
    if summary_type == "domain_specific":
        result += f"DOMAIN-SPECIFIC ANALYSIS - {domain.upper()}\n"
        result += "=" * 50 + "\n"
        
        # Extract entities
        entities = MockT5Summarizer.extract_entities(text, domain)
        result += format_entities(entities)
        
        # Generate structured summary
        summary = MockT5Summarizer.detailed_summary(text, domain)
        result += "\nSTRUCTURED SUMMARY:\n"
        result += "=" * 50 + "\n"
        result += summary + "\n"
    
    else:  # brief or detailed
        summary_name = "BRIEF SUMMARY" if summary_type == "brief" else "DETAILED SUMMARY"
        result += f"{summary_name} (T5 Model with Instruction)\n"
        result += "=" * 50 + "\n"
        
        if summary_type == "brief":
            summary = MockT5Summarizer.brief_summary(text, domain)
        else:
            summary = MockT5Summarizer.detailed_summary(text, domain)
        
        result += summary + "\n"
    
    return result

def get_summary_options() -> Dict:
    """Return available summarization options."""
    return {
        "brief": {
            "name": "Brief Summary",
            "instruction": "Summarize in 2-3 sentences",
            "description": "Quick overview using T5 with brief instruction",
            "length_tokens": "80-100 tokens"
        },
        "detailed": {
            "name": "Detailed Summary",
            "instruction": "Provide comprehensive summary with all key points",
            "description": "Full summary using T5 with detailed instruction",
            "length_tokens": "200-250 tokens"
        },
        "domain_specific": {
            "name": "Domain-Specific Analysis",
            "instruction": "Extract entities and provide structured summary",
            "description": "Detailed analysis with entity extraction using T5",
            "length_tokens": "150-200 tokens"
        }
    }

# Testing
if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("SINGLE T5 MODEL WITH DIFFERENT INSTRUCTIONS")
    print("="*70)
    
    # Medical Document
    medical_text = """
    Patient Name: Mr. Ruwan Perera 
Age: 45 
Gender: Male 
Date of Admission: 01 September 2025 
Date of Discharge: 05 September 2025 
Hospital: Colombo General Hospital 
Consultant Physician: Dr. Anjali Fernando 
Chief Complaint 
Patient presented with chest pain, shortness of breath, and fatigue for the past two weeks. 
Medical History 
• Hypertension (diagnosed 2015) 
• Type 2 Diabetes Mellitus (diagnosed 2018) 
• Family history of ischemic heart disease (father). 
Examination Findings 
• Blood Pressure: 150/95 mmHg 
• Heart Rate: 96 bpm 
• ECG: ST-segment depression noted 
• Chest X-ray: Mild cardiomegaly 
• Blood Tests: Elevated cholesterol, HbA1c = 8.2% 
Diagnosis 
• Acute Coronary Syndrome (Unstable Angina) 
Treatment Given 
• Aspirin 75mg daily 
• Clopidogrel 75mg daily 
• Atorvastatin 40mg nightly 
• Insulin therapy for diabetes control 
• Lifestyle advice: diet modification, exercise, smoking cessation 
Outcome & Discharge Plan 
Patient responded well to medication. Chest pain subsided. Referred for follow-up at cardiology clinic in 
two weeks. Advised regular monitoring of blood sugar and blood pressure. 
    """
    
    print("\n--- MEDICAL DOCUMENT ---\n")
    
    print("1. BRIEF SUMMARY (T5 with brief instruction)\n")
    print(summarize_with_t5_instruction(medical_text, "brief"))
    
    print("\n2. DETAILED SUMMARY (T5 with detailed instruction)\n")
    print(summarize_with_t5_instruction(medical_text, "detailed"))
    
    print("\n3. DOMAIN-SPECIFIC ANALYSIS (T5 with entity extraction instruction)\n")
    print(summarize_with_t5_instruction(medical_text, "domain_specific"))
    
    
    # Show options
    print("\n" + "="*70)
    print("AVAILABLE OPTIONS")
    print("="*70 + "\n")
    
    options = get_summary_options()
    for key, opt in options.items():
        print(f"{key.upper()}:")
        print(f"  Instruction: {opt['instruction']}")
        print(f"  Description: {opt['description']}")
        print(f"  Length: {opt['length_tokens']}\n")