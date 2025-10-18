



# import requests
# import logging
# import json
# import time
# import re
# from typing import Dict, List, Optional, Union
# import os
# from dotenv import load_dotenv

# logger = logging.getLogger(__name__)

# # Hard-coded API key - YOU NEED TO UPDATE THIS WITH A VALID KEY
# HF_API_KEY = os.getenv("HF_API_KEY")

# # NER endpoints for different domains
# NER_ENDPOINTS = {
#     "medical_biomedical": "https://api-inference.huggingface.co/models/d4data/biomedical-ner-all",
#     "medical_clinical": "https://api-inference.huggingface.co/models/Clinical-AI-Apollo/Medical-NER",
#     "legal": "https://api-inference.huggingface.co/models/nlpaueb/legal-bert-base-uncased",
#     "general": "https://api-inference.huggingface.co/models/dbmdz/bert-large-cased-finetuned-conll03-english"
# }

# def get_summary_options():
#     """Return available summarization options."""
#     return {
#         "brief": {
#             "name": "Brief Summary", 
#             "model": "bart",
#             "max_length": 150,
#             "min_length": 50
#         },
#         "detailed": {
#             "name": "Detailed Summary", 
#             "model": "pegasus",
#             "max_length": 250,
#             "min_length": 80
#         },
#         "domain_specific": {
#             "name": "Domain Specific Summary", 
#             "model": "bart",
#             "max_length": 200,
#             "min_length": 70
#         }
#     }

# def _get_model_endpoint(model_name: str) -> str:
#     """Get the Hugging Face API endpoint for the model."""
#     models = {
#         "bart": "facebook/bart-large-cnn",
#         "pegasus": "google/pegasus-cnn_dailymail", 
#         "t5": "t5-base"
#     }
    
#     if model_name not in models:
#         raise ValueError(f"Unknown model: {model_name}")
    
#     model_id = models[model_name]
#     return f"https://api-inference.huggingface.co/models/{model_id}"

# def _make_api_request(endpoint: str, payload: dict, max_retries: int = 3) -> dict:
#     """Make a request to the Hugging Face API with retry logic."""
#     headers = {
#         "Authorization": f"Bearer {HF_API_KEY}",
#         "Content-Type": "application/json"
#     }
    
#     for attempt in range(max_retries):
#         try:
#             response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            
#             if response.status_code == 401:
#                 raise Exception(f"Invalid API key. Please check your Hugging Face API key: {response.text}")
#             elif response.status_code == 503:
#                 logger.info(f"Model loading, waiting 20 seconds... (attempt {attempt + 1})")
#                 time.sleep(20)
#                 continue
#             elif response.status_code == 429:
#                 logger.info(f"Rate limit hit, waiting 10 seconds... (attempt {attempt + 1})")
#                 time.sleep(10)
#                 continue
#             elif response.status_code != 200:
#                 logger.error(f"API request failed with status {response.status_code}: {response.text}")
#                 if attempt == max_retries - 1:
#                     raise Exception(f"API request failed: {response.status_code} - {response.text}")
#                 time.sleep(5)
#                 continue
            
#             return response.json()
            
#         except requests.exceptions.Timeout:
#             logger.error(f"Request timeout (attempt {attempt + 1})")
#             if attempt == max_retries - 1:
#                 raise Exception("Request timed out after multiple attempts")
#             time.sleep(5)
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Request error: {e} (attempt {attempt + 1})")
#             if attempt == max_retries - 1:
#                 raise Exception(f"Request failed: {str(e)}")
#             time.sleep(5)
    
#     raise Exception("Max retries exceeded")

# def detect_document_domain(text: str) -> str:
#     """Detect if the document is medical, legal, or general"""
#     text_lower = text.lower()
    
#     # Medical indicators
#     medical_patterns = [
#         r"patient", r"diagnosis", r"treatment", r"medication", r"doctor", r"hospital",
#         r"medical", r"clinical", r"symptom", r"prescription", r"therapy", r"disease",
#         r"blood pressure", r"heart rate", r"lab results", r"discharge", r"admission",
#         r"anaemia", r"thalassaemia"
#     ]
    
#     # Legal indicators
#     legal_patterns = [
#         r"contract", r"agreement", r"plaintiff", r"defendant", r"court", r"lawsuit",
#         r"attorney", r"lawyer", r"legal", r"jurisdiction", r"clause", r"whereas",
#         r"party", r"parties", r"breach", r"damages", r"settlement", r"litigation"
#     ]
    
#     medical_score = sum(len(re.findall(pattern, text_lower)) for pattern in medical_patterns)
#     legal_score = sum(len(re.findall(pattern, text_lower)) for pattern in legal_patterns)
    
#     if medical_score > legal_score and medical_score > 3:
#         return "medical"
#     elif legal_score > medical_score and legal_score > 3:
#         return "legal"
#     else:
#         return "general"

# def _reconstruct_entity_text(entities: List[Dict]) -> List[Dict]:
#     """Reconstruct fragmented BERT tokens into complete entities"""
#     if not entities:
#         return []
    
#     reconstructed = []
#     current_entity = None
    
#     for entity in sorted(entities, key=lambda x: x.get('start', 0)):
#         word = entity.get('word', entity.get('text', ''))
#         entity_type = entity.get('entity_group', entity.get('label', entity.get('entity', '')))
#         confidence = entity.get('score', entity.get('confidence', 0.0))
#         start_pos = entity.get('start', 0)
        
#         # Handle BERT subword tokens (starting with ##)
#         if word.startswith('##'):
#             if (current_entity and 
#                 current_entity.get('entity_type') == entity_type and 
#                 abs(start_pos - current_entity.get('end_pos', 0)) <= 2):
#                 # Merge with previous entity
#                 current_entity['word'] += word[2:]  # Remove ##
#                 current_entity['confidence'] = max(current_entity['confidence'], confidence)
#                 current_entity['end_pos'] = entity.get('end', start_pos + len(word))
#             else:
#                 # Start new entity if types don't match or gap is too large
#                 if current_entity:
#                     reconstructed.append(current_entity)
#                 current_entity = {
#                     'word': word[2:],
#                     'entity_type': entity_type,
#                     'confidence': confidence,
#                     'start_pos': start_pos,
#                     'end_pos': entity.get('end', start_pos + len(word))
#                 }
#         else:
#             # Regular word - finish previous entity if exists
#             if current_entity:
#                 reconstructed.append(current_entity)
            
#             current_entity = {
#                 'word': word,
#                 'entity_type': entity_type,
#                 'confidence': confidence,
#                 'start_pos': start_pos,
#                 'end_pos': entity.get('end', start_pos + len(word))
#             }
    
#     # Don't forget the last entity
#     if current_entity:
#         reconstructed.append(current_entity)
    
#     return reconstructed

# def _filter_meaningful_entities(entities: List[Dict], domain: str) -> List[Dict]:
#     """Filter out meaningless or low-quality entities"""
#     if not entities:
#         return []
    
#     filtered = []
    
#     # Domain-specific meaningful patterns
#     medical_meaningful = {
#         'condition_patterns': [
#             r'\b\w*(?:anaemia|anemia|thalassaemia|thalassemia|diabetes|hypertension|cancer|infection)\w*\b',
#             r'\biron\s+deficiency\s+anaemia\b',
#             r'\bbeta\s+thalassaemia\s+trait\b'
#         ],
#         'medication_patterns': [
#             r'\b\w*(?:cillin|mycin|statin|pril|formin)\w*\b',
#             r'\b(?:metformin|lisinopril|aspirin|ferrous)\b'
#         ],
#         'procedure_patterns': [
#             r'\b\w*(?:surgery|therapy|examination|test)\w*\b',
#             r'\b(?:echocardiogram|mri|ct\s+scan|mentzer\s+index)\b'
#         ],
#         'anatomy_patterns': [
#             r'\b(?:heart|liver|kidney|brain|lung|blood)\b'
#         ],
#         'person_patterns': [
#             r'\b(?:Dr|Doctor|Mr|Mrs|Ms)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
#             r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
#         ],
#         'organization_patterns': [
#             r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Hospital|Clinic|Diagnostics|Institute|Laboratories|Lab|Health)\b',
#             r'\bAgilus\s+Diagnostics\s+Ltd\b',
#             r'\bNational\s+Institutes\s+of\s+Health\b'
#         ]
#     }
    
#     legal_meaningful = {
#         'party_patterns': [
#             r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',
#             r'\b\w+\s+(?:Inc|LLC|Corp|Ltd)\.?\b'
#         ],
#         'legal_terms': [
#             r'\b(?:contract|agreement|liability|damages|breach)\b'
#         ],
#         'court_terms': [
#             r'\b(?:court|judge|jury|trial|appeal)\b'
#         ],
#         'person_patterns': [
#             r'\b(?:Judge|Attorney|Mr|Mrs|Ms)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
#             r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
#         ]
#     }
    
#     for entity in entities:
#         word = entity.get('word', '').strip()
#         confidence = entity.get('confidence', 0.0)
#         entity_type = entity.get('entity_type', '')
        
#         # Basic quality filters
#         if (len(word) < 3 or                    # Too short
#             confidence < 0.7 or                 # Higher confidence threshold
#             word.isdigit() or                   # Just numbers
#             len(word) > 50 or                   # Too long (likely error)
#             word.lower() in ['fax', 'ci', 'ted', 'no', 'caunter', 'based'] or  # Specific noise from example
#             word in ['–', '-', ':', '(', ')', ',', '.', 'the', 'a', 'an', 'and', 'or', 'of', 'in', 'to', 'for']):  # Stop words/punctuation
#             continue
        
#         # Domain-specific meaningful checks
#         is_meaningful = False
        
#         if domain == "medical":
#             # Check if matches meaningful medical patterns
#             for pattern_list in medical_meaningful.values():
#                 if any(re.search(pattern, word, re.IGNORECASE) for pattern in pattern_list):
#                     is_meaningful = True
#                     break
            
#             # Additional medical entity type checks
#             if entity_type.lower() in ['disease', 'medication', 'treatment', 'anatomy', 'procedure', 'person', 'organization']:
#                 is_meaningful = True
        
#         elif domain == "legal":
#             # Check if matches meaningful legal patterns
#             for pattern_list in legal_meaningful.values():
#                 if any(re.search(pattern, word, re.IGNORECASE) for pattern in pattern_list):
#                     is_meaningful = True
#                     break
            
#             # Additional legal entity type checks
#             if entity_type.lower() in ['person', 'organization', 'legal_term', 'court']:
#                 is_meaningful = True
        
#         else:  # general domain
#             # For general domain, be more lenient but still filter obvious junk
#             if (len(word) >= 4 and 
#                 not word.isdigit() and 
#                 confidence > 0.75 and
#                 entity_type.lower() in ['person', 'organization', 'location']):
#                 is_meaningful = True
        
#         if is_meaningful:
#             filtered.append(entity)
    
#     return filtered

# def _group_and_deduplicate_entities(entities: List[Dict]) -> Dict[str, List[str]]:
#     """Group entities by type and remove duplicates with smart matching"""
#     grouped = {}
    
#     for entity in entities:
#         entity_type = entity.get('entity_type', 'UNKNOWN')
#         word = entity.get('word', '').strip()
        
#         # Normalize entity type names for better readability
#         entity_type = entity_type.replace('_', ' ').title()
        
#         # Map common entity types to more readable names
#         type_mapping = {
#             'Per': 'Person',
#             'Org': 'Organization', 
#             'Loc': 'Location',
#             'Misc': 'Miscellaneous',
#             'Disease': 'Medical Condition',
#             'Chemical': 'Medication/Chemical',
#             'Anatomy': 'Body Part/Anatomy',
#             'Sign_Symptom': 'Sign/Symptom',
#             'Diagnostic_Procedure': 'Diagnostic Procedure',
#             'Disease_Disorder': 'Medical Condition'
#         }
        
#         entity_type = type_mapping.get(entity_type, entity_type)
        
#         if entity_type not in grouped:
#             grouped[entity_type] = []
        
#         # Smart deduplication - avoid very similar entities
#         word_lower = word.lower()
#         is_duplicate = False
        
#         for existing in grouped[entity_type]:
#             existing_lower = existing.lower()
#             # Check if it's a substring or very similar
#             if (word_lower in existing_lower or 
#                 existing_lower in word_lower or 
#                 (len(word_lower) >= 5 and len(existing_lower) >= 5 and 
#                  abs(len(word_lower) - len(existing_lower)) <= 3)):
#                 # Keep the longer/more complete version
#                 if len(word) > len(existing):
#                     grouped[entity_type].remove(existing)
#                     grouped[entity_type].append(word)
#                 is_duplicate = True
#                 break
        
#         if not is_duplicate:
#             grouped[entity_type].append(word)
    
#     return grouped

# def query_ner_api(text: str, domain: str) -> List[Dict]:
#     """Query the appropriate NER API based on domain with improved error handling"""
#     try:
#         print(f"Starting NER query for domain '{domain}'")
        
#         if domain == "medical":
#             endpoint = NER_ENDPOINTS["medical_biomedical"]
#             endpoint_type = "medical_biomedical"
#         elif domain == "legal":
#             endpoint = NER_ENDPOINTS["legal"]
#             endpoint_type = "legal"
#         else:
#             endpoint = NER_ENDPOINTS["general"]
#             endpoint_type = "general"
        
#         headers = {"Authorization": f"Bearer {HF_API_KEY}"}
#         # Limit text length for better API performance
#         text_chunk = text[:2000] if len(text) > 2000 else text
#         payload = {"inputs": text_chunk}
        
#         print(f"Sending request to {endpoint_type} endpoint")
#         print(f"Text length: {len(text_chunk)} characters")
        
#         response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        
#         print(f"Response status: {response.status_code}")
        
#         if response.status_code == 401:
#             print("Invalid API key error")
#             return []
#         elif response.status_code == 200:
#             result = response.json()
#             print(f"Raw API response type: {type(result)}")
            
#             # Handle different response formats
#             if isinstance(result, list):
#                 print(f"Found {len(result)} raw entities")
#                 return result
#             elif isinstance(result, dict) and 'entities' in result:
#                 print(f"Found {len(result['entities'])} entities in dict format")
#                 return result['entities']
#             else:
#                 print(f"Unexpected response format, attempting to extract entities")
#                 return []
                
#         elif response.status_code == 503:
#             print("Model is loading, trying fallback...")
#             if domain == "medical" and endpoint_type == "medical_biomedical":
#                 time.sleep(10)
#                 return query_ner_fallback(text_chunk, "medical_clinical")
#             else:
#                 print(f"Model loading error for {endpoint_type}")
#                 return []
#         else:
#             print(f"API Error: {response.status_code} - {response.text}")
#             logger.error(f"NER API Error ({endpoint_type}): {response.status_code} - {response.text}")
            
#             if domain == "medical" and endpoint_type == "medical_biomedical":
#                 return query_ner_fallback(text_chunk, "medical_clinical")
#             return []
            
#     except Exception as e:
#         print(f"Exception occurred: {str(e)}")
#         logger.error(f"NER API Request failed: {e}")
        
#         if domain == "medical":
#             try:
#                 return query_ner_fallback(text[:2000], "medical_clinical")
#             except:
#                 pass
        
#         return []

# def query_ner_fallback(text: str, fallback_type: str) -> List[Dict]:
#     """Fallback NER query with improved error handling"""
#     try:
#         print(f"Using fallback: {fallback_type}")
#         endpoint = NER_ENDPOINTS[fallback_type]
#         headers = {"Authorization": f"Bearer {HF_API_KEY}"}
#         payload = {"inputs": text}
        
#         response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        
#         print(f"Fallback response status: {response.status_code}")
        
#         if response.status_code == 401:
#             print("Invalid API key error in fallback")
#             return []
#         elif response.status_code == 200:
#             result = response.json()
#             print(f"Fallback response received")
            
#             if isinstance(result, list):
#                 return result
#             elif isinstance(result, dict) and 'entities' in result:
#                 return result['entities']
#             else:
#                 return []
#         else:
#             print(f"Fallback error: {response.status_code} - {response.text}")
#             logger.error(f"Fallback NER API Error ({fallback_type}): {response.status_code}")
#             return []
            
#     except Exception as e:
#         print(f"Fallback exception: {str(e)}")
#         logger.error(f"Fallback NER API Request failed: {e}")
#         return []

# def format_ner_entities(entities: List[Dict], domain: str) -> str:
#     """Format NER entities in a professional, readable way with improved processing"""
#     print(f"Formatting {len(entities)} entities for domain '{domain}'")
    
#     if not entities:
#         return "NAMED ENTITY RECOGNITION RESULTS\n" + "=" * 40 + "\n\nNo significant entities identified in the document.\n"
    
#     # Step 1: Reconstruct fragmented tokens
#     reconstructed_entities = _reconstruct_entity_text(entities)
#     print(f"After reconstruction: {len(reconstructed_entities)} entities")
    
#     # Step 2: Filter meaningful entities
#     meaningful_entities = _filter_meaningful_entities(reconstructed_entities, domain)
#     print(f"After filtering: {len(meaningful_entities)} meaningful entities")
    
#     # Step 3: Group and deduplicate
#     grouped_entities = _group_and_deduplicate_entities(meaningful_entities)
#     print(f"Grouped entities: {grouped_entities}")
    
#     # Step 4: Format output professionally
#     formatted_output = "NAMED ENTITY RECOGNITION RESULTS\n"
#     formatted_output += "=" * 40 + "\n\n"
    
#     if not any(grouped_entities.values()):
#         formatted_output += "No significant entities identified with sufficient confidence.\n"
#     else:
#         # Sort entity types for consistent output
#         sorted_types = sorted(grouped_entities.keys())
        
#         for entity_type in sorted_types:
#             entity_list = grouped_entities[entity_type]
#             if entity_list:
#                 formatted_output += f"{entity_type.upper()}:\n"
                
#                 # Sort entities alphabetically and limit to most relevant
#                 sorted_entities = sorted(set(entity_list))[:8]  # Limit to top 8 per category
                
#                 for entity in sorted_entities:
#                     formatted_output += f"  • {entity}\n"
                
#                 formatted_output += "\n"
    
#     print(f"Final formatted output length: {len(formatted_output)}")
#     return formatted_output.strip()

# def extract_medical_key_fields(text: str) -> str:
#     """Extract key medical fields using regex patterns"""
#     key_fields = "KEY MEDICAL INFORMATION EXTRACTED\n"
#     key_fields += "=" * 38 + "\n\n"
    
#     # Patient demographics - improved name extraction
#     name_patterns = [
#         r"patient\s+name:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",  # Full name pattern
#         r"patient:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
#         r"name:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
#         r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:was\s+admitted|presented)\b"  # Name from context
#     ]
    
#     for pattern in name_patterns:
#         name_match = re.search(pattern, text, re.IGNORECASE)
#         if name_match:
#             full_name = name_match.group(1).strip()
#             # Ensure we have at least first and last name
#             if len(full_name.split()) >= 2:
#                 key_fields += f"Patient Name: {full_name}\n"
#                 break
    
#     age_match = re.search(r"age:\s*(\d+)", text, re.IGNORECASE)
#     if age_match:
#         key_fields += f"Age: {age_match.group(1)} years\n"
    
#     # Diagnoses - improved to capture specific conditions
#     diagnosis_patterns = [
#         r"diagnosis\s*:?\s*([^\n]+)",
#         r"primary\s+diagnosis\s*:?\s*([^\n]+)",
#         r"impression\s*:?\s*([^\n]+)",
#         r"\b(?:iron\s+deficiency\s+anaemia|beta\s+thalassaemia\s+trait|thalassaemia\s+trait|diabetes|hypertension)\b([^\n]*)"
#     ]
    
#     diagnoses = []
#     for pattern in diagnosis_patterns:
#         match = re.search(pattern, text, re.IGNORECASE)
#         if match:
#             diagnosis = match.group(1).strip() if match.lastindex else match.group(0).strip()
#             if diagnosis and diagnosis not in diagnoses:
#                 diagnoses.append(diagnosis)
    
#     if diagnoses:
#         key_fields += "Diagnoses:\n"
#         for diag in diagnoses[:3]:  # Limit to top 3
#             key_fields += f"  • {diag}\n"
    
#     # Medications
#     med_matches = re.finditer(r"([A-Za-z]+(?:cillin|mycin|statin|pril|formin|ferrous))\s+(\d+\s*mg)", text, re.IGNORECASE)
#     medications = []
#     for match in med_matches:
#         medications.append(f"{match.group(1)} {match.group(2)}")
    
#     if medications:
#         key_fields += "Medications:\n"
#         for med in medications[:5]:  # Show first 5
#             key_fields += f"  • {med}\n"
    
#     # Vital signs
#     bp_match = re.search(r"blood\s+pressure[:\s]*(\d+/\d+)", text, re.IGNORECASE)
#     if bp_match:
#         key_fields += f"Blood Pressure: {bp_match.group(1)} mmHg\n"
    
#     glucose_match = re.search(r"glucose[:\s]*(\d+\s*mg/dL)", text, re.IGNORECASE)
#     if glucose_match:
#         key_fields += f"Blood Glucose: {glucose_match.group(1)}\n"
    
#     key_fields += "\n"
#     return key_fields

# def extract_legal_key_fields(text: str) -> str:
#     """Extract key legal fields using regex patterns"""
#     key_fields = "KEY LEGAL INFORMATION EXTRACTED\n"
#     key_fields += "=" * 35 + "\n\n"
    
#     # Parties - improved name extraction
#     plaintiff_patterns = [
#         r"plaintiff[s]?:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|LLC|Corp|Ltd)\.?)?)",
#         r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.?\s+"
#     ]
    
#     for pattern in plaintiff_patterns:
#         plaintiff_match = re.search(pattern, text, re.IGNORECASE)
#         if plaintiff_match:
#             plaintiff_name = plaintiff_match.group(1).strip()
#             if len(plaintiff_name.split()) >= 1:
#                 key_fields += f"Plaintiff: {plaintiff_name}\n"
#                 break
    
#     defendant_patterns = [
#         r"defendant[s]?:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|LLC|Corp|Ltd)\.?)?)",
#         r"v\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
#     ]
    
#     for pattern in defendant_patterns:
#         defendant_match = re.search(pattern, text, re.IGNORECASE)
#         if defendant_match:
#             defendant_name = defendant_match.group(1).strip()
#             if len(defendant_name.split()) >= 1:
#                 key_fields += f"Defendant: {defendant_name}\n"
#                 break
    
#     # Case information
#     case_match = re.search(r"case\s+(?:no\.?|number):?\s*([A-Z0-9\-]+)", text, re.IGNORECASE)
#     if case_match:
#         key_fields += f"Case Number: {case_match.group(1)}\n"
    
#     # Monetary amounts
#     amount_match = re.search(r"(?:\$|usd\s*)([0-9,]+(?:\.\d{2})?)", text, re.IGNORECASE)
#     if amount_match:
#         key_fields += f"Amount: ${amount_match.group(1)}\n"
    
#     # Dates
#     date_match = re.search(r"(?:filed|signed|dated)\s+on:?\s*(\d{1,2}[\/\-\s]\w+[\/\-\s]\d{2,4})", text, re.IGNORECASE)
#     if date_match:
#         key_fields += f"Important Date: {date_match.group(1)}\n"
    
#     key_fields += "\n"
#     return key_fields

# def generate_rule_based_summary(text: str, max_length: int, summary_type: str) -> str:
#     """Generate a rule-based summary as fallback when APIs fail"""
#     sentences = re.split(r'[.!?]+', text)
#     sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
#     # Simple scoring based on keyword frequency and position
#     scored_sentences = []
#     for i, sentence in enumerate(sentences):
#         score = 0
        
#         # Position bonus (earlier sentences get higher scores)
#         score += max(0, 10 - i)
        
#         # Keyword bonus
#         important_words = ['diagnosis', 'treatment', 'patient', 'conclusion', 'summary', 
#                           'plaintiff', 'defendant', 'contract', 'agreement', 'court',
#                           'anaemia', 'thalassaemia', 'mentzer']
        
#         for word in important_words:
#             if word in sentence.lower():
#                 score += 5
        
#         # Length penalty for very long sentences
#         if len(sentence) > 200:
#             score -= 2
        
#         scored_sentences.append((score, sentence))
    
#     # Sort by score and select top sentences
#     scored_sentences.sort(reverse=True, key=lambda x: x[0])
#     selected_sentences = [s[1] for s in scored_sentences[:3]]
    
#     rule_summary = " ".join(selected_sentences)
    
#     # Truncate if too long
#     words = rule_summary.split()
#     if len(words) > max_length:
#         rule_summary = " ".join(words[:max_length]) + "..."
    
#     return rule_summary

# def _preprocess_text_for_model(text: str, model_name: str) -> str:
#     """Preprocess text based on model requirements."""
#     if model_name == "t5":
#         return f"summarize: {text}"
#     return text

# def _handle_long_text(text: str, model_name: str, max_length: int, min_length: int, endpoint: str):
#     """Handle long text by chunking appropriately for each model."""
#     max_input_lengths = {
#         "bart": 1024,
#         "pegasus": 512,
#         "t5": 512
#     }
    
#     max_input_length = max_input_lengths.get(model_name, 1024)
    
#     if len(text) <= max_input_length:
#         processed_text = _preprocess_text_for_model(text, model_name)
#         payload = {
#             "inputs": processed_text,
#             "parameters": {
#                 "max_length": max_length,
#                 "min_length": min_length,
#                 "do_sample": False
#             }
#         }
        
#         try:
#             result = _make_api_request(endpoint, payload)
#             if isinstance(result, list) and len(result) > 0:
#                 return result[0].get("summary_text", "")
#             else:
#                 raise Exception(f"Unexpected API response format: {result}")
#         except Exception as e:
#             logger.error(f"Error with single chunk summarization: {e}")
#             # Try with shorter text
#             shorter_text = text[:max_input_length//2]
#             processed_text = _preprocess_text_for_model(shorter_text, model_name)
#             payload["inputs"] = processed_text
#             result = _make_api_request(endpoint, payload)
#             if isinstance(result, list) and len(result) > 0:
#                 return result[0].get("summary_text", "")
#             else:
#                 raise Exception(f"Unexpected API response format: {result}")
#     else:
#         # Handle long text with chunks
#         chunks = [text[i:i+max_input_length] for i in range(0, len(text), max_input_length//2)]
#         summaries = []
        
#         chunk_max_length = min(max_length//len(chunks) + 30, max_length//2)
#         chunk_min_length = max(min_length//len(chunks), 10)
        
#         for chunk in chunks:
#             try:
#                 processed_chunk = _preprocess_text_for_model(chunk, model_name)
#                 payload = {
#                     "inputs": processed_chunk,
#                     "parameters": {
#                         "max_length": chunk_max_length,
#                         "min_length": chunk_min_length,
#                         "do_sample": False
#                     }
#                 }
                
#                 result = _make_api_request(endpoint, payload)
#                 if isinstance(result, list) and len(result) > 0:
#                     summaries.append(result[0].get("summary_text", ""))
                
#                 # Add small delay between requests to avoid rate limiting
#                 time.sleep(1)
                
#             except Exception as e:
#                 logger.error(f"Error processing chunk: {e}")
#                 continue
        
#         if not summaries:
#             raise Exception("Failed to process any text chunks")
        
#         combined = " ".join(summaries)
#         if len(combined.split()) > max_length:
#             try:
#                 processed_combined = _preprocess_text_for_model(combined, model_name)
#                 payload = {
#                     "inputs": processed_combined,
#                     "parameters": {
#                         "max_length": max_length,
#                         "min_length": min_length,
#                         "do_sample": False
#                     }
#                 }
#                 result = _make_api_request(endpoint, payload)
#                 if isinstance(result, list) and len(result) > 0:
#                     return result[0].get("summary_text", "")
#             except Exception as e:
#                 logger.error(f"Error re-summarizing combined text: {e}")
#                 return " ".join(combined.split()[:max_length])
        
#         return combined

# def format_summary_as_points(summary_text: str, entities: List[Dict], domain: str) -> str:
#     """Format the summary text as pointwise bullet points, prioritizing key entities."""
#     sentences = re.split(r'[.!?]+', summary_text)
#     sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
#     if not sentences:
#         return "No meaningful summary points available."
    
#     # Extract key entities for filtering
#     entity_words = {e.get('word', '').lower() for e in entities}
#     key_terms = {'diagnosis', 'patient', 'treatment', 'medication', 'anaemia', 
#                  'thalassaemia', 'mentzer', 'doctor', 'hospital', 'index'}
    
#     # Score sentences based on relevance
#     scored_sentences = []
#     for sentence in sentences:
#         score = 0
#         sentence_lower = sentence.lower()
        
#         # Boost score for sentences containing entities or key terms
#         for entity in entity_words:
#             if entity in sentence_lower:
#                 score += 5
#         for term in key_terms:
#             if term in sentence_lower:
#                 score += 3
        
#         # Penalize short or irrelevant sentences
#         if len(sentence) < 20 or any(noise in sentence_lower for noise in ['ted', 'fax', 'ci', 'no']):
#             score -= 5
        
#         scored_sentences.append((score, sentence))
    
#     # Sort and select top sentences
#     scored_sentences.sort(reverse=True, key=lambda x: x[0])
#     selected_sentences = [s[1] for s in scored_sentences[:5]]  # Limit to 5 points
    
#     if not selected_sentences:
#         return "No meaningful summary points available."
    
#     # Format as bullet points
#     formatted = ""
#     for sentence in selected_sentences:
#         # Clean up sentence
#         sentence = sentence.strip().capitalize()
#         if not sentence.endswith('.'):
#             sentence += '.'
#         formatted += f"• {sentence}\n"
    
#     return formatted.strip()

# def perform_domain_analysis_with_ner(text: str, domain: str) -> str:
#     """Perform domain analysis with NER - only called for domain-specific summaries"""
#     result = ""
    
#     # Add domain detection info
#     result += f"DOCUMENT ANALYSIS\n"
#     result += "=" * 18 + "\n\n"
#     result += f"Document Type: {domain.title()}\n\n"
    
#     if domain in ["medical", "legal"]:
#         # Extract key fields using regex patterns
#         if domain == "medical":
#             key_fields = extract_medical_key_fields(text)
#         else:
#             key_fields = extract_legal_key_fields(text)
        
#         print(f"Key fields extracted: {len(key_fields)} characters")
#         result += key_fields
        
#         # Get NER entities
#         print(f"Starting NER API query for {domain} domain...")
#         logger.info(f"Querying NER API for {domain} domain...")
        
#         try:
#             ner_entities = query_ner_api(text, domain)
#             print(f"NER entities received: {len(ner_entities) if ner_entities else 0} entities")
            
#             # Always format and add NER results, even if empty
#             formatted_ner = format_ner_entities(ner_entities, domain)
#             print(f"Formatted NER length: {len(formatted_ner)} characters")
#             result += formatted_ner + "\n\n"
            
#         except Exception as ner_error:
#             print(f"NER failed with error: {ner_error}")
#             result += "NAMED ENTITY RECOGNITION RESULTS\n"
#             result += "=" * 40 + "\n\n"
#             result += f"NER analysis failed: {str(ner_error)}\n\n"
#     else:
#         print(f"Domain '{domain}' not medical or legal, skipping NER")
#         result += f"No domain-specific NER analysis available for {domain} documents.\n\n"
    
#     return result

# def summarize_with_options(text: str, options: dict) -> str:
#     """Generate a summary using the appropriate model, with NER only for domain-specific summaries."""
#     try:
#         model_name = options["model"]
#         max_length = options.get("max_length", 150)
#         min_length = options.get("min_length", 50)
#         summary_type = options.get("name", "")
        
#         # Check if this is a domain-specific summary request
#         is_domain_specific = summary_type == "Domain Specific Summary"
        
#         print(f"Summary type: {summary_type}")
#         print(f"Is domain-specific request: {is_domain_specific}")
#         print(f"Using model: {model_name}")
        
#         result = ""
        
#         # Detect domain for all types
#         domain = detect_document_domain(text)
#         print(f"Detected domain: {domain}")
#         logger.info(f"Detected domain: {domain}")
        
#         # For domain-specific summaries, perform full analysis with NER
#         ner_entities = []
#         if is_domain_specific:
#             result += perform_domain_analysis_with_ner(text, domain)
#             try:
#                 ner_entities = query_ner_api(text, domain)
#             except:
#                 ner_entities = []
        
#         # Generate summary with improved reliability
#         summary_generated = False
#         summary_text = ""
        
#         try:
#             # Use BART for all summary types for better reliability
#             endpoint = _get_model_endpoint("bart")
#             print(f"Attempting summary with BART model...")
            
#             summary_text = _handle_long_text(text, "bart", max_length, min_length, endpoint)
#             print(f"Summary generated successfully: {len(summary_text)} characters")
#             summary_generated = True
            
#         except Exception as summary_error:
#             print(f"BART model failed: {summary_error}")
#             logger.error(f"Error with BART model: {summary_error}")
            
#             # Fallback to rule-based summary
#             try:
#                 print("Attempting rule-based summary fallback...")
#                 summary_text = generate_rule_based_summary(text, max_length, summary_type)
#                 print(f"Rule-based summary generated: {len(summary_text)} characters")
#                 summary_generated = True
#             except Exception as fallback_error:
#                 print(f"Rule-based fallback failed: {fallback_error}")
#                 logger.error(f"Rule-based fallback failed: {fallback_error}")
        
#         # Add summary section
#         if summary_generated and summary_text.strip():
#             if is_domain_specific:
#                 result += "DOMAIN-SPECIFIC SUMMARY\n"
#                 result += "=" * 25 + "\n\n"
#                 result += format_summary_as_points(summary_text, ner_entities, domain)
#             else:
#                 result += "SUMMARY\n"
#                 result += "=" * 7 + "\n\n"
#                 result += summary_text.strip()
#         else:
#             # Summary generation completely failed
#             if is_domain_specific:
#                 result += "DOMAIN-SPECIFIC SUMMARY\n"
#                 result += "=" * 25 + "\n\n"
#             else:
#                 result += "SUMMARY\n"
#                 result += "=" * 7 + "\n\n"
            
#             result += "Summary generation failed. Please try again or check your API configuration.\n"
        
#         print(f"Final result length: {len(result)} characters")
#         return result
        
#     except Exception as e:
#         print(f"Exception in summarize_with_options: {e}")
#         logger.error(f"Error in summarize_with_options: {e}")
        
#         # Provide a fallback response with error info
#         error_result = "PROCESSING ERROR\n"
#         error_result += "=" * 16 + "\n\n"
#         error_result += f"An error occurred during processing: {str(e)}\n\n"
        
#         # For domain-specific summaries, still try to provide NER analysis
#         if options.get("name") == "Domain Specific Summary":
#             try:
#                 domain = detect_document_domain(text)
#                 error_result += perform_domain_analysis_with_ner(text, domain)
#             except Exception as analysis_error:
#                 error_result += f"Domain analysis also failed: {str(analysis_error)}\n"
        
#         return error_result

# def get_model_info():
#     """Return information about each model's strengths."""
#     return {
#         "bart": {
#             "name": "BART (Bidirectional and Auto-Regressive Transformers)",
#             "strengths": ["Detailed summaries", "Comprehensive analysis", "Good for longer content"],
#             "best_for": ["All summary types", "Long documents", "Academic content"]
#         },
#         "pegasus": {
#             "name": "Pegasus (Pre-training with Extracted Gap-sentences)",
#             "strengths": ["Abstractive summarization", "Concise summaries", "News articles"],
#             "best_for": ["Brief summaries", "News content", "Abstract summaries"]
#         },
#         "t5": {
#             "name": "T5 (Text-To-Text Transfer Transformer)", 
#             "strengths": ["Flexible text generation", "Structured output", "Domain-specific analysis"],
#             "best_for": ["Structured output", "Technical documents", "Complex analysis"]
#         }
#     }

# def check_api_key():
#     """Check if the API key is configured."""
#     if HF_API_KEY == "hf_YOUR_VALID_API_KEY_HERE":
#         raise ValueError("Please replace 'hf_YOUR_VALID_API_KEY_HERE' with your actual Hugging Face API key")
#     return True

# # Example usage and testing
# if __name__ == "__main__":
#     # Configure logging for better debugging
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
#     # Test with a medical document
#     medical_text = """
#     Patient Name: K B Chunchaiah
#     Age: 45
#     Date: September 14, 2025
    
#     Diagnosis: Iron Deficiency Anaemia, Beta Thalassaemia Trait
    
#     The patient was admitted to hospital with iron deficiency anaemia (>13) from beta thalassaemia trait. 
#     Blood tests showed microcytic anaemia with elevated Mentzer index. The patient has a history
#     of fatigue and pallor. The Mentzer index (MCV/RBC) is an automated cell-counter based calculated service tool 
#     to differentiate cases of iron deficiency anaemia (>13) from beta thalassaemia trait. 
#     Estimation of HbA2 remains the gold standard for diagnosing a case of beta thalassaemia trait.
    
#     Current medications:
#     - Ferrous Sulfate 200mg daily
    
#     Treatment plan includes:
#     - Continue iron supplementation
#     - Follow-up in 2 months
#     - Monitor hemoglobin levels
    
#     Dr. Somashekar
#     Agilus Diagnostics Ltd
#     23, 80 Feet Road, Gurukrupa Layout, Bangalore, 560072
#     """
    
#     print("=" * 60)
#     print("TESTING DOMAIN-SPECIFIC SUMMARY WITH NER")
#     print("=" * 60)
    
#     # Test domain-specific summary (with NER)
#     try:
#         domain_options = get_summary_options()["domain_specific"]
#         result = summarize_with_options(medical_text, domain_options)
#         print(result)
        
#         print("\n" + "=" * 60)
#         print("TESTING BRIEF SUMMARY (NO NER - JUST SUMMARY)")
#         print("=" * 60)
        
#         # Test brief summary (without NER)
#         brief_options = get_summary_options()["brief"]
#         result_brief = summarize_with_options(medical_text, brief_options)
#         print(result_brief)
        
#         print("\n" + "=" * 60)
#         print("TESTING DETAILED SUMMARY (NO NER - JUST SUMMARY)")
#         print("=" * 60)
        
#         # Test detailed summary (without NER)
#         detailed_options = get_summary_options()["detailed"]
#         result_detailed = summarize_with_options(medical_text, detailed_options)
#         print(result_detailed)
        
#         print("\n" + "=" * 60)
#         print("TESTING RULE-BASED SUMMARY FALLBACK")
#         print("=" * 60)
        
#         # Test rule-based summary directly
#         rule_summary = generate_rule_based_summary(medical_text, 150, "Domain Specific Summary")
#         print("Rule-based summary (fallback when APIs fail):")
#         print(rule_summary)
        
#     except Exception as e:
#         print(f"Test failed with error: {e}")
#         import traceback
#         traceback.print_exc()


import requests
import logging
import json
import time
import re
from typing import Dict, List, Optional, Union
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Hard-coded API key - YOU NEED TO UPDATE THIS WITH A VALID KEY
HF_API_KEY = os.getenv("HF_API_KEY")

# NER endpoints for different domains
NER_ENDPOINTS = {
    "medical_biomedical": "https://api-inference.huggingface.co/models/d4data/biomedical-ner-all",
    "medical_clinical": "https://api-inference.huggingface.co/models/Clinical-AI-Apollo/Medical-NER",
    "legal": "https://api-inference.huggingface.co/models/nlpaueb/legal-bert-base-uncased",
    "general": "https://api-inference.huggingface.co/models/dbmdz/bert-large-cased-finetuned-conll03-english"
}

def get_summary_options():
    """Return available summarization options with different models for each type."""
    return {
        "brief": {
            "name": "Brief Summary", 
            "model": "pegasus",
            "max_length": 100,
            "min_length": 30
        },
        "detailed": {
            "name": "Detailed Summary", 
            "model": "bart",
            "max_length": 300,
            "min_length": 100
        },
        "domain_specific": {
            "name": "Domain Specific Summary", 
            "model": "t5",
            "max_length": 250,
            "min_length": 80
        }
    }

def _get_model_endpoint(model_name: str) -> str:
    """Get the Hugging Face API endpoint for the model with reliable alternatives."""
    models = {
        "bart": "facebook/bart-large-cnn",
        "pegasus": "sshleifer/distilbart-cnn-12-6",  # More reliable alternative
        "t5": "google/flan-t5-base"
    }
    
    if model_name not in models:
        raise ValueError(f"Unknown model: {model_name}")
    
    model_id = models[model_name]
    return f"https://api-inference.huggingface.co/models/{model_id}"

def _make_api_request(endpoint: str, payload: dict, max_retries: int = 3) -> dict:
    """Make a request to the Hugging Face API with retry logic."""
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 401:
                raise Exception(f"Invalid API key. Please check your Hugging Face API key: {response.text}")
            elif response.status_code == 503:
                logger.info(f"Model loading, waiting 20 seconds... (attempt {attempt + 1})")
                time.sleep(20)
                continue
            elif response.status_code == 429:
                logger.info(f"Rate limit hit, waiting 10 seconds... (attempt {attempt + 1})")
                time.sleep(10)
                continue
            elif response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                if attempt == max_retries - 1:
                    raise Exception(f"API request failed: {response.status_code} - {response.text}")
                time.sleep(5)
                continue
            
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                raise Exception("Request timed out after multiple attempts")
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e} (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                raise Exception(f"Request failed: {str(e)}")
            time.sleep(5)
    
    raise Exception("Max retries exceeded")

def detect_document_domain(text: str) -> str:
    """Detect if the document is medical, legal, or general"""
    text_lower = text.lower()
    
    # Medical indicators
    medical_patterns = [
        r"patient", r"diagnosis", r"treatment", r"medication", r"doctor", r"hospital",
        r"medical", r"clinical", r"symptom", r"prescription", r"therapy", r"disease",
        r"blood pressure", r"heart rate", r"lab results", r"discharge", r"admission",
        r"anaemia", r"thalassaemia"
    ]
    
    # Legal indicators
    legal_patterns = [
        r"contract", r"agreement", r"plaintiff", r"defendant", r"court", r"lawsuit",
        r"attorney", r"lawyer", r"legal", r"jurisdiction", r"clause", r"whereas",
        r"party", r"parties", r"breach", r"damages", r"settlement", r"litigation"
    ]
    
    medical_score = sum(len(re.findall(pattern, text_lower)) for pattern in medical_patterns)
    legal_score = sum(len(re.findall(pattern, text_lower)) for pattern in legal_patterns)
    
    if medical_score > legal_score and medical_score > 3:
        return "medical"
    elif legal_score > medical_score and legal_score > 3:
        return "legal"
    else:
        return "general"

def _reconstruct_entity_text(entities: List[Dict]) -> List[Dict]:
    """Reconstruct fragmented BERT tokens into complete entities"""
    if not entities:
        return []
    
    reconstructed = []
    current_entity = None
    
    for entity in sorted(entities, key=lambda x: x.get('start', 0)):
        word = entity.get('word', entity.get('text', ''))
        entity_type = entity.get('entity_group', entity.get('label', entity.get('entity', '')))
        confidence = entity.get('score', entity.get('confidence', 0.0))
        start_pos = entity.get('start', 0)
        
        # Handle BERT subword tokens (starting with ##)
        if word.startswith('##'):
            if (current_entity and 
                current_entity.get('entity_type') == entity_type and 
                abs(start_pos - current_entity.get('end_pos', 0)) <= 2):
                current_entity['word'] += word[2:]
                current_entity['confidence'] = max(current_entity['confidence'], confidence)
                current_entity['end_pos'] = entity.get('end', start_pos + len(word))
            else:
                if current_entity:
                    reconstructed.append(current_entity)
                current_entity = {
                    'word': word[2:],
                    'entity_type': entity_type,
                    'confidence': confidence,
                    'start_pos': start_pos,
                    'end_pos': entity.get('end', start_pos + len(word))
                }
        else:
            if current_entity:
                reconstructed.append(current_entity)
            
            current_entity = {
                'word': word,
                'entity_type': entity_type,
                'confidence': confidence,
                'start_pos': start_pos,
                'end_pos': entity.get('end', start_pos + len(word))
            }
    
    if current_entity:
        reconstructed.append(current_entity)
    
    return reconstructed

def _filter_meaningful_entities(entities: List[Dict], domain: str) -> List[Dict]:
    """Filter out meaningless or low-quality entities"""
    if not entities:
        return []
    
    filtered = []
    
    medical_meaningful = {
        'condition_patterns': [
            r'\b\w*(?:anaemia|anemia|thalassaemia|thalassemia|diabetes|hypertension|cancer|infection)\w*\b',
            r'\biron\s+deficiency\s+anaemia\b',
            r'\bbeta\s+thalassaemia\s+trait\b'
        ],
        'medication_patterns': [
            r'\b\w*(?:cillin|mycin|statin|pril|formin)\w*\b',
            r'\b(?:metformin|lisinopril|aspirin|ferrous)\b'
        ],
        'procedure_patterns': [
            r'\b\w*(?:surgery|therapy|examination|test)\w*\b',
            r'\b(?:echocardiogram|mri|ct\s+scan|mentzer\s+index)\b'
        ],
        'anatomy_patterns': [
            r'\b(?:heart|liver|kidney|brain|lung|blood)\b'
        ],
        'person_patterns': [
            r'\b(?:Dr|Doctor|Mr|Mrs|Ms)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        ],
        'organization_patterns': [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Hospital|Clinic|Diagnostics|Institute|Laboratories|Lab|Health)\b',
            r'\bAgilus\s+Diagnostics\s+Ltd\b',
            r'\bNational\s+Institutes\s+of\s+Health\b'
        ]
    }
    
    legal_meaningful = {
        'party_patterns': [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',
            r'\b\w+\s+(?:Inc|LLC|Corp|Ltd)\.?\b'
        ],
        'legal_terms': [
            r'\b(?:contract|agreement|liability|damages|breach)\b'
        ],
        'court_terms': [
            r'\b(?:court|judge|jury|trial|appeal)\b'
        ],
        'person_patterns': [
            r'\b(?:Judge|Attorney|Mr|Mrs|Ms)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        ]
    }
    
    for entity in entities:
        word = entity.get('word', '').strip()
        confidence = entity.get('confidence', 0.0)
        entity_type = entity.get('entity_type', '')
        
        if (len(word) < 3 or confidence < 0.7 or word.isdigit() or len(word) > 50 or
            word.lower() in ['fax', 'ci', 'ted', 'no', 'caunter', 'based'] or
            word in ['–', '-', ':', '(', ')', ',', '.', 'the', 'a', 'an', 'and', 'or', 'of', 'in', 'to', 'for']):
            continue
        
        is_meaningful = False
        
        if domain == "medical":
            for pattern_list in medical_meaningful.values():
                if any(re.search(pattern, word, re.IGNORECASE) for pattern in pattern_list):
                    is_meaningful = True
                    break
            
            if entity_type.lower() in ['disease', 'medication', 'treatment', 'anatomy', 'procedure', 'person', 'organization']:
                is_meaningful = True
        
        elif domain == "legal":
            for pattern_list in legal_meaningful.values():
                if any(re.search(pattern, word, re.IGNORECASE) for pattern in pattern_list):
                    is_meaningful = True
                    break
            
            if entity_type.lower() in ['person', 'organization', 'legal_term', 'court']:
                is_meaningful = True
        
        else:
            if (len(word) >= 4 and not word.isdigit() and confidence > 0.75 and
                entity_type.lower() in ['person', 'organization', 'location']):
                is_meaningful = True
        
        if is_meaningful:
            filtered.append(entity)
    
    return filtered

def _group_and_deduplicate_entities(entities: List[Dict]) -> Dict[str, List[str]]:
    """Group entities by type and remove duplicates with smart matching"""
    grouped = {}
    
    for entity in entities:
        entity_type = entity.get('entity_type', 'UNKNOWN')
        word = entity.get('word', '').strip()
        
        entity_type = entity_type.replace('_', ' ').title()
        
        type_mapping = {
            'Per': 'Person',
            'Org': 'Organization', 
            'Loc': 'Location',
            'Misc': 'Miscellaneous',
            'Disease': 'Medical Condition',
            'Chemical': 'Medication/Chemical',
            'Anatomy': 'Body Part/Anatomy',
            'Sign_Symptom': 'Sign/Symptom',
            'Diagnostic_Procedure': 'Diagnostic Procedure',
            'Disease_Disorder': 'Medical Condition'
        }
        
        entity_type = type_mapping.get(entity_type, entity_type)
        
        if entity_type not in grouped:
            grouped[entity_type] = []
        
        word_lower = word.lower()
        is_duplicate = False
        
        for existing in grouped[entity_type]:
            existing_lower = existing.lower()
            if (word_lower in existing_lower or existing_lower in word_lower or 
                (len(word_lower) >= 5 and len(existing_lower) >= 5 and 
                 abs(len(word_lower) - len(existing_lower)) <= 3)):
                if len(word) > len(existing):
                    grouped[entity_type].remove(existing)
                    grouped[entity_type].append(word)
                is_duplicate = True
                break
        
        if not is_duplicate:
            grouped[entity_type].append(word)
    
    return grouped

def query_ner_api(text: str, domain: str) -> List[Dict]:
    """Query the appropriate NER API based on domain with improved error handling"""
    try:
        print(f"Starting NER query for domain '{domain}'")
        
        if domain == "medical":
            endpoint = NER_ENDPOINTS["medical_biomedical"]
            endpoint_type = "medical_biomedical"
        elif domain == "legal":
            endpoint = NER_ENDPOINTS["legal"]
            endpoint_type = "legal"
        else:
            endpoint = NER_ENDPOINTS["general"]
            endpoint_type = "general"
        
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        text_chunk = text[:2000] if len(text) > 2000 else text
        payload = {"inputs": text_chunk}
        
        print(f"Sending request to {endpoint_type} endpoint")
        print(f"Text length: {len(text_chunk)} characters")
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 401:
            print("Invalid API key error")
            return []
        elif response.status_code == 200:
            result = response.json()
            print(f"Raw API response type: {type(result)}")
            
            if isinstance(result, list):
                print(f"Found {len(result)} raw entities")
                return result
            elif isinstance(result, dict) and 'entities' in result:
                print(f"Found {len(result['entities'])} entities in dict format")
                return result['entities']
            else:
                print(f"Unexpected response format, attempting to extract entities")
                return []
                
        elif response.status_code == 503:
            print("Model is loading, trying fallback...")
            if domain == "medical" and endpoint_type == "medical_biomedical":
                time.sleep(10)
                return query_ner_fallback(text_chunk, "medical_clinical")
            else:
                print(f"Model loading error for {endpoint_type}")
                return []
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            logger.error(f"NER API Error ({endpoint_type}): {response.status_code} - {response.text}")
            
            if domain == "medical" and endpoint_type == "medical_biomedical":
                return query_ner_fallback(text_chunk, "medical_clinical")
            return []
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        logger.error(f"NER API Request failed: {e}")
        
        if domain == "medical":
            try:
                return query_ner_fallback(text[:2000], "medical_clinical")
            except:
                pass
        
        return []

def query_ner_fallback(text: str, fallback_type: str) -> List[Dict]:
    """Fallback NER query with improved error handling"""
    try:
        print(f"Using fallback: {fallback_type}")
        endpoint = NER_ENDPOINTS[fallback_type]
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": text}
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        
        print(f"Fallback response status: {response.status_code}")
        
        if response.status_code == 401:
            print("Invalid API key error in fallback")
            return []
        elif response.status_code == 200:
            result = response.json()
            print(f"Fallback response received")
            
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'entities' in result:
                return result['entities']
            else:
                return []
        else:
            print(f"Fallback error: {response.status_code} - {response.text}")
            logger.error(f"Fallback NER API Error ({fallback_type}): {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Fallback exception: {str(e)}")
        logger.error(f"Fallback NER API Request failed: {e}")
        return []

def format_ner_entities_professional(entities: List[Dict], domain: str) -> str:
    """Format NER entities in a compact table format for domain-specific summaries"""
    print(f"Formatting {len(entities)} entities for domain '{domain}'")
    
    if not entities:
        return "ENTITIES EXTRACTED\n" + "No significant entities identified in the document."
    
    reconstructed_entities = _reconstruct_entity_text(entities)
    print(f"After reconstruction: {len(reconstructed_entities)} entities")
    
    meaningful_entities = _filter_meaningful_entities(reconstructed_entities, domain)
    print(f"After filtering: {len(meaningful_entities)} meaningful entities")
    
    grouped_entities = _group_and_deduplicate_entities(meaningful_entities)
    print(f"Grouped entities: {grouped_entities}")
    
    if not any(grouped_entities.values()):
        return "ENTITIES EXTRACTED\n" + "No significant entities identified with sufficient confidence."
    
    formatted_output = "ENTITIES EXTRACTED\n"
    
    sorted_types = sorted(grouped_entities.keys())
    
    for entity_type in sorted_types:
        entity_list = grouped_entities[entity_type]
        if entity_list:
            sorted_entities = sorted(set(entity_list))[:8]
            for i, entity in enumerate(sorted_entities):
                if i == 0:
                    formatted_output += f"{entity_type}: {entity}\n"
                else:
                    formatted_output += f"{entity}, "
            formatted_output = formatted_output.rstrip(", ") + "\n"
    
    print(f"Final formatted output length: {len(formatted_output)}")
    return formatted_output.strip()

def extract_medical_key_fields(text: str) -> str:
    """Extract key medical fields using regex patterns"""
    key_fields = "MEDICAL INFORMATION SUMMARY\n"
    key_fields += "=" * 50 + "\n\n"
    
    name_patterns = [
        r"patient\s+name:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        r"patient:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        r"name:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:was\s+admitted|presented)\b"
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, text, re.IGNORECASE)
        if name_match:
            full_name = name_match.group(1).strip()
            if len(full_name.split()) >= 2:
                key_fields += f"Patient: {full_name}\n"
                break
    
    age_match = re.search(r"age:\s*(\d+)", text, re.IGNORECASE)
    if age_match:
        key_fields += f"Age: {age_match.group(1)} years\n"
    
    diagnosis_patterns = [
        r"diagnosis\s*:?\s*([^\n]+)",
        r"primary\s+diagnosis\s*:?\s*([^\n]+)",
        r"impression\s*:?\s*([^\n]+)"
    ]
    
    diagnoses = []
    for pattern in diagnosis_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            diagnosis = match.group(1).strip() if match.lastindex else match.group(0).strip()
            if diagnosis and diagnosis not in diagnoses:
                diagnoses.append(diagnosis)
    
    if diagnoses:
        key_fields += f"Primary Diagnosis: {diagnoses[0]}\n"
    
    med_matches = re.finditer(r"([A-Za-z]+(?:cillin|mycin|statin|pril|formin|ferrous))\s+(\d+\s*mg)", text, re.IGNORECASE)
    medications = []
    for match in med_matches:
        medications.append(f"{match.group(1)} {match.group(2)}")
    
    if medications:
        key_fields += f"Current Medications: {', '.join(medications[:3])}\n"
    
    bp_match = re.search(r"blood\s+pressure[:\s]*(\d+/\d+)", text, re.IGNORECASE)
    if bp_match:
        key_fields += f"Blood Pressure: {bp_match.group(1)} mmHg\n"
    
    key_fields += "\n"
    return key_fields

def extract_legal_key_fields(text: str) -> str:
    """Extract key legal fields using regex patterns"""
    key_fields = "LEGAL INFORMATION SUMMARY\n"
    key_fields += "=" * 50 + "\n\n"
    
    plaintiff_patterns = [
        r"plaintiff[s]?:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|LLC|Corp|Ltd)\.?)?)",
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.?\s+"
    ]
    
    for pattern in plaintiff_patterns:
        plaintiff_match = re.search(pattern, text, re.IGNORECASE)
        if plaintiff_match:
            plaintiff_name = plaintiff_match.group(1).strip()
            if len(plaintiff_name.split()) >= 1:
                key_fields += f"Plaintiff: {plaintiff_name}\n"
                break
    
    defendant_patterns = [
        r"defendant[s]?:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|LLC|Corp|Ltd)\.?)?)",
        r"v\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
    ]
    
    for pattern in defendant_patterns:
        defendant_match = re.search(pattern, text, re.IGNORECASE)
        if defendant_match:
            defendant_name = defendant_match.group(1).strip()
            if len(defendant_name.split()) >= 1:
                key_fields += f"Defendant: {defendant_name}\n"
                break
    
    case_match = re.search(r"case\s+(?:no\.?|number):?\s*([A-Z0-9\-]+)", text, re.IGNORECASE)
    if case_match:
        key_fields += f"Case Number: {case_match.group(1)}\n"
    
    amount_match = re.search(r"(?:\$|usd\s*)([0-9,]+(?:\.\d{2})?)", text, re.IGNORECASE)
    if amount_match:
        key_fields += f"Amount: ${amount_match.group(1)}\n"
    
    date_match = re.search(r"(?:filed|signed|dated)\s+on:?\s*(\d{1,2}[\/\-\s]\w+[\/\-\s]\d{2,4})", text, re.IGNORECASE)
    if date_match:
        key_fields += f"Date: {date_match.group(1)}\n"
    
    key_fields += "\n"
    return key_fields

def generate_rule_based_summary(text: str, max_length: int, summary_type: str) -> str:
    """Generate a rule-based summary as fallback when APIs fail"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = 0
        score += max(0, 10 - i)
        
        important_words = ['diagnosis', 'treatment', 'patient', 'conclusion', 'summary', 
                          'plaintiff', 'defendant', 'contract', 'agreement', 'court',
                          'anaemia', 'thalassaemia', 'mentzer']
        
        for word in important_words:
            if word in sentence.lower():
                score += 5
        
        if len(sentence) > 200:
            score -= 2
        
        scored_sentences.append((score, sentence))
    
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    selected_sentences = [s[1] for s in scored_sentences[:3]]
    
    rule_summary = " ".join(selected_sentences)
    
    words = rule_summary.split()
    if len(words) > max_length:
        rule_summary = " ".join(words[:max_length]) + "..."
    
    return rule_summary

def _handle_long_text(text: str, model_name: str, max_length: int, min_length: int, endpoint: str):
    """Handle long text by chunking appropriately for each model."""
    max_input_lengths = {
        "bart": 1024,
        "pegasus": 512,
        "t5": 512
    }
    
    max_input_length = max_input_lengths.get(model_name, 1024)
    
    if len(text) <= max_input_length:
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": max_length,
                "min_length": min_length,
                "do_sample": False
            }
        }
        
        try:
            result = _make_api_request(endpoint, payload)
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("summary_text", "")
            else:
                raise Exception(f"Unexpected API response format: {result}")
        except Exception as e:
            logger.error(f"Error with {model_name} summarization: {e}")
            shorter_text = text[:max_input_length//2]
            payload["inputs"] = shorter_text
            result = _make_api_request(endpoint, payload)
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("summary_text", "")
            else:
                raise Exception(f"Unexpected API response format: {result}")
    else:
        chunks = [text[i:i+max_input_length] for i in range(0, len(text), max_input_length//2)]
        summaries = []
        
        chunk_max_length = min(max_length//len(chunks) + 30, max_length//2)
        chunk_min_length = max(min_length//len(chunks), 10)
        
        for chunk in chunks:
            try:
                payload = {
                    "inputs": chunk,
                    "parameters": {
                        "max_length": chunk_max_length,
                        "min_length": chunk_min_length,
                        "do_sample": False
                    }
                }
                
                result = _make_api_request(endpoint, payload)
                if isinstance(result, list) and len(result) > 0:
                    summaries.append(result[0].get("summary_text", ""))
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing chunk: {e}")
                continue
        
        if not summaries:
            raise Exception("Failed to process any text chunks")
        
        combined = " ".join(summaries)
        if len(combined.split()) > max_length:
            try:
                payload = {
                    "inputs": combined,
                    "parameters": {
                        "max_length": max_length,
                        "min_length": min_length,
                        "do_sample": False
                    }
                }
                result = _make_api_request(endpoint, payload)
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("summary_text", "")
            except Exception as e:
                logger.error(f"Error re-summarizing combined text: {e}")
                return " ".join(combined.split()[:max_length])
        
        return combined

def perform_domain_analysis_with_ner(text: str, domain: str) -> str:
    """Perform domain analysis with NER for domain-specific summaries in compact format"""
    result = ""
    
    if domain in ["medical", "legal"]:
        if domain == "medical":
            key_fields = extract_medical_key_fields(text)
        else:
            key_fields = extract_legal_key_fields(text)
        
        print(f"Key fields extracted: {len(key_fields)} characters")
        result += key_fields
        
        print(f"Starting NER API query for {domain} domain...")
        logger.info(f"Querying NER API for {domain} domain...")
        
        try:
            ner_entities = query_ner_api(text, domain)
            print(f"NER entities received: {len(ner_entities) if ner_entities else 0} entities")
            
            formatted_ner = format_ner_entities_professional(ner_entities, domain)
            print(f"Formatted NER length: {len(formatted_ner)} characters")
            result += formatted_ner + "\n"
            
        except Exception as ner_error:
            print(f"NER failed with error: {ner_error}")
            result += "ENTITIES EXTRACTED\n"
            result += f"Entity extraction failed: {str(ner_error)}"
    else:
        print(f"Domain '{domain}' not medical or legal, skipping detailed NER")
        result += f"Entity analysis not available for {domain} documents.  \n"
    
    return result

def summarize_with_options(text: str, options: dict) -> str:
    """Generate a summary using the appropriate model based on summary type."""
    try:
        model_name = options["model"]
        max_length = options.get("max_length", 150)
        min_length = options.get("min_length", 50)
        summary_type = options.get("name", "")
        
        is_domain_specific = summary_type == "Domain Specific Summary"
        
        print(f"\n{'='*60}")
        print(f"Summary type: {summary_type}")
        print(f"Using model: {model_name.upper()}")
        print(f"Is domain-specific request: {is_domain_specific}")
        print(f"{'='*60}\n")
        
        result = ""
        
        domain = detect_document_domain(text)
        print(f"Detected domain: {domain}")
        logger.info(f"Detected domain: {domain}")
        
        ner_entities = []
        if is_domain_specific:
            result += perform_domain_analysis_with_ner(text, domain)
            try:
                ner_entities = query_ner_api(text, domain)
            except:
                ner_entities = []
        
        summary_generated = False
        summary_text = ""
        
        try:
            endpoint = _get_model_endpoint(model_name)
            print(f"Attempting summary with {model_name.upper()} model...")
            
            summary_text = _handle_long_text(text, model_name, max_length, min_length, endpoint)
            print(f"Summary generated successfully with {model_name.upper()}: {len(summary_text)} characters")
            summary_generated = True
            
        except Exception as summary_error:
            print(f"{model_name.upper()} model failed: {summary_error}")
            logger.error(f"Error with {model_name} model: {summary_error}")
            
            try:
                print("Attempting rule-based summary fallback...")
                summary_text = generate_rule_based_summary(text, max_length, summary_type)
                print(f"Rule-based summary generated: {len(summary_text)} characters")
                summary_generated = True
            except Exception as fallback_error:
                print(f"Rule-based fallback failed: {fallback_error}")
                logger.error(f"Rule-based fallback failed: {fallback_error}")
        
        # if summary_generated and summary_text.strip():
        #     if is_domain_specific:
                
        #         result += "\nSUMMARY\n"
                
        #         # Format summary more compactly - break into logical sentences
        #         summary_sentences = re.split(r'(?<=[.!?])\s+', summary_text.strip())
        #         for sentence in summary_sentences:
        #             result += sentence.strip() + " "
        #         result = result.strip() + "\n"
        #     else:
        #         result += "\nSUMMARY\n"
        #         result += "=" * 50 + "\n\n"
        #         result += summary_text.strip() + "\n"
        # else:
        #     if is_domain_specific:
        #         result += "\nSUMMARY\n"
        #     else:
        #         result += "SUMMARY\n"
        #         result += "=" * 50 + "\n\n"
            
        #     result += "Summary generation failed. Please try again or check your API configuration.\n"

        if summary_generated and summary_text.strip():
            if is_domain_specific:
                # Format with clear separation between entities and summary
                result += "-" * 50 + "\n"
                result += "SUMMARY\n"
                result += "-" * 50 + "\n\n"
                
                # Format summary more compactly - break into logical sentences
                summary_sentences = re.split(r'(?<=[.!?])\s+', summary_text.strip())
                for sentence in summary_sentences:
                    result += sentence.strip() + " "
                result = result.strip() + "\n"
            else:
                result += "SUMMARY\n"
                result += "=" * 50 + "\n\n"
                result += summary_text.strip() + "\n"
        else:
            if is_domain_specific:
                result += "-" * 50 + "\n"
                result += "SUMMARY\n"
                result += "-" * 50 + "\n\n"
            else:
                result += "SUMMARY\n"
                result += "=" * 50 + "\n\n"
            
            result += "Summary generation failed. Please try again or check your API configuration.\n"

        
        print(f"Final result length: {len(result)} characters")
        return result
        
    except Exception as e:
        print(f"Exception in summarize_with_options: {e}")
        logger.error(f"Error in summarize_with_options: {e}")
        
        error_result = "PROCESSING ERROR\n"
        error_result += "=" * 50 + "\n\n"
        error_result += f"An error occurred during processing: {str(e)}\n\n"
        
        if options.get("name") == "Domain Specific Summary":
            try:
                domain = detect_document_domain(text)
                error_result += perform_domain_analysis_with_ner(text, domain)
            except Exception as analysis_error:
                error_result += f"Domain analysis also failed: {str(analysis_error)}\n"
        
        return error_result

def get_model_info():
    """Return information about each model's strengths."""
    return {
        "pegasus": {
            "name": "Pegasus (Google - CNN/DailyMail)",
            "strengths": ["Concise, abstractive summaries", "Excellent for news content", "Fast processing", "Best for brief summaries"],
            "best_for": ["Brief summaries", "Quick overviews", "News articles"]
        },
        "bart": {
            "name": "BART (Facebook - Large CNN)",
            "strengths": ["Comprehensive summaries", "Excellent detail retention", "Balanced abstraction", "Large vocabulary"],
            "best_for": ["Detailed summaries", "Complex documents", "Academic content"]
        },
        "t5": {
            "name": "T5 (Google - FLAN-T5-Base)",
            "strengths": ["Instruction-following", "Flexible output", "Domain-aware analysis", "Structured formatting"],
            "best_for": ["Domain-specific analysis", "Structured extraction", "Technical documents"]
        }
    }

def check_api_key():
    """Check if the API key is configured."""
    if not HF_API_KEY or HF_API_KEY == "hf_YOUR_VALID_API_KEY_HERE":
        raise ValueError("Please set HF_API_KEY environment variable with your actual Hugging Face API key")
    return True

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    medical_text = """
    Patient Name: K B Chunchaiah
    Age: 45
    Date: September 14, 2025
    
    Diagnosis: Iron Deficiency Anaemia, Beta Thalassaemia Trait
    
    The patient was admitted to hospital with iron deficiency anaemia (>13) from beta thalassaemia trait. 
    Blood tests showed microcytic anaemia with elevated Mentzer index. The patient has a history
    of fatigue and pallor. The Mentzer index (MCV/RBC) is an automated cell-counter based calculated service tool 
    to differentiate cases of iron deficiency anaemia (>13) from beta thalassaemia trait. 
    Estimation of HbA2 remains the gold standard for diagnosing a case of beta thalassaemia trait.
    
    Current medications:
    - Ferrous Sulfate 200mg daily
    
    Treatment plan includes:
    - Continue iron supplementation
    - Follow-up in 2 months
    - Monitor hemoglobin levels
    
    Dr. Somashekar
    Agilus Diagnostics Ltd
    23, 80 Feet Road, Gurukrupa Layout, Bangalore, 560072
    """
    
    print("\n" + "=" * 70)
    print("TEST 1: BRIEF SUMMARY (PEGASUS MODEL)")
    print("=" * 70)
    
    try:
        brief_options = get_summary_options()["brief"]
        result_brief = summarize_with_options(medical_text, brief_options)
        print(result_brief)
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("TEST 2: DETAILED SUMMARY (BART MODEL)")
    print("=" * 70)
    
    try:
        detailed_options = get_summary_options()["detailed"]
        result_detailed = summarize_with_options(medical_text, detailed_options)
        print(result_detailed)
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("TEST 3: DOMAIN-SPECIFIC SUMMARY (T5 MODEL + NER)")
    print("=" * 70)
    
    try:
        domain_options = get_summary_options()["domain_specific"]
        result_domain = summarize_with_options(medical_text, domain_options)
        print(result_domain)
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("MODEL INFORMATION")
    print("=" * 70)
    
    model_info = get_model_info()
    for model_key, model_details in model_info.items():
        print(f"\n{model_details['name']}")
        print(f"Strengths: {', '.join(model_details['strengths'])}")
        print(f"Best for: {', '.join(model_details['best_for'])}")