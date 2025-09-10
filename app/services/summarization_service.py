
# from transformers import pipeline
# import logging
# import re

# logger = logging.getLogger(__name__)

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
#             "model": "t5",
#             "max_length": 200,
#             "min_length": 70
#         }
#     }

# def _get_model_pipeline(model_name: str):
#     """Initialize the appropriate model pipeline."""
#     models = {
#         "bart": "facebook/bart-large-cnn",
#         "pegasus": "google/pegasus-cnn_dailymail", 
#         "t5": "t5-base"
#     }
    
#     if model_name not in models:
#         raise ValueError(f"Unknown model: {model_name}")
    
#     try:
#         return pipeline("summarization", model=models[model_name], framework="pt")
#     except Exception as e:
#         logger.error(f"Error loading model {model_name}: {e}")
#         # Fallback to BART if model loading fails
#         logger.info("Falling back to BART model...")
#         return pipeline("summarization", model="facebook/bart-large-cnn", framework="pt")

# def _preprocess_text_for_model(text: str, model_name: str) -> str:
#     """Preprocess text based on model requirements."""
#     if model_name == "t5":
#         return f"summarize: {text}"
#     return text

# def _handle_long_text(text: str, model_name: str, max_length: int, min_length: int, summarizer):
#     """Handle long text by chunking appropriately for each model."""
#     max_input_lengths = {
#         "bart": 1024,
#         "pegasus": 512,
#         "t5": 512
#     }
    
#     max_input_length = max_input_lengths.get(model_name, 1024)
    
#     if len(text) <= max_input_length:
#         processed_text = _preprocess_text_for_model(text, model_name)
#         try:
#             result = summarizer(processed_text, 
#                               max_length=max_length, 
#                               min_length=min_length, 
#                               do_sample=False)
#             return result[0]["summary_text"]
#         except Exception as e:
#             logger.error(f"Error with single chunk summarization: {e}")
#             # Try with shorter text
#             shorter_text = text[:max_input_length//2]
#             processed_text = _preprocess_text_for_model(shorter_text, model_name)
#             result = summarizer(processed_text, 
#                               max_length=max_length, 
#                               min_length=min_length, 
#                               do_sample=False)
#             return result[0]["summary_text"]
#     else:
#         # Handle long text with chunks
#         chunks = [text[i:i+max_input_length] for i in range(0, len(text), max_input_length//2)]
#         summaries = []
        
#         chunk_max_length = min(max_length//len(chunks) + 30, max_length//2)
#         chunk_min_length = max(min_length//len(chunks), 10)
        
#         for chunk in chunks:
#             try:
#                 processed_chunk = _preprocess_text_for_model(chunk, model_name)
#                 result = summarizer(processed_chunk, 
#                                   max_length=chunk_max_length, 
#                                   min_length=chunk_min_length, 
#                                   do_sample=False)
#                 summaries.append(result[0]["summary_text"])
#             except Exception as e:
#                 logger.error(f"Error processing chunk: {e}")
#                 # Skip problematic chunks
#                 continue
        
#         if not summaries:
#             raise Exception("Failed to process any text chunks")
        
#         combined = " ".join(summaries)
#         if len(combined.split()) > max_length:
#             try:
#                 processed_combined = _preprocess_text_for_model(combined, model_name)
#                 result = summarizer(processed_combined, 
#                                   max_length=max_length, 
#                                   min_length=min_length, 
#                                   do_sample=False)
#                 return result[0]["summary_text"]
#             except Exception as e:
#                 logger.error(f"Error re-summarizing combined text: {e}")
#                 # Return truncated version if re-summarization fails
#                 return " ".join(combined.split()[:max_length])
        
#         return combined

# def summarize_with_options(text: str, options: dict) -> str:
#     """Generate a summary using the appropriate model."""
#     try:
#         model_name = options["model"]
#         max_length = options.get("max_length", 150)
#         min_length = options.get("min_length", 50)
        
#         # Initialize the model
#         summarizer = _get_model_pipeline(model_name)
        
#         # Generate summary
#         summary = _handle_long_text(text, model_name, max_length, min_length, summarizer)
        
#         return summary.strip()
        
#     except Exception as e:
#         logger.error(f"Error generating summary with {options.get('model', 'unknown')} model: {e}")
#         # Fallback to BART
#         try:
#             logger.info("Falling back to BART model...")
#             summarizer = _get_model_pipeline("bart")
#             summary = _handle_long_text(text, "bart", max_length, min_length, summarizer)
#             return summary.strip()
#         except Exception as fallback_error:
#             logger.error(f"Fallback also failed: {fallback_error}")
#             raise Exception(f"Both primary and fallback models failed: {str(e)}")

# def get_model_info():
#     """Return information about each model's strengths."""
#     return {
#         "bart": {
#             "name": "BART (Bidirectional and Auto-Regressive Transformers)",
#             "strengths": ["Detailed summaries", "Comprehensive analysis", "Good for longer content"],
#             "best_for": ["Detailed Summary", "Long documents", "Academic content"]
#         },
#         "pegasus": {
#             "name": "Pegasus (Pre-training with Extracted Gap-sentences)",
#             "strengths": ["Abstractive summarization", "Concise summaries", "News articles"],
#             "best_for": ["Brief Summary", "Abstract Summary", "News content"]
#         },
#         "t5": {
#             "name": "T5 (Text-To-Text Transfer Transformer)", 
#             "strengths": ["Flexible text generation", "Structured output", "Business content"],
#             "best_for": ["Executive Summary", "Technical Summary", "Structured content"]
#         }
#     }


from transformers import pipeline
import logging
import re
import time
import threading
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
import numpy as np

# # Download required NLTK data
# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     nltk.download('punkt')

# try:
#     nltk.data.find('corpora/stopwords')
# except LookupError:
#     nltk.download('stopwords')

logger = logging.getLogger(__name__)

def get_summary_options():
    """Return available summarization options."""
    return {
        "brief": {
            "name": "Brief Summary", 
            "model": "bart",
            "max_length": 150,
            "min_length": 50
        },
        "detailed": {
            "name": "Detailed Summary", 
            "model": "pegasus",
            "max_length": 250,
            "min_length": 80
        },
        "domain_specific": {
            "name": "Domain Specific Summary", 
            "model": "t5",
            "max_length": 200,
            "min_length": 70
        }
    }

class RuleBasedSummarizer:
    """Custom rule-based summarization fallback system."""
    
    def __init__(self, max_words=500):
        self.max_words = max_words
        self.stemmer = PorterStemmer()
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            # Fallback stop words if NLTK data is not available
            self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'}
    
    def _clean_text(self, text):
        """Clean and preprocess text."""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        return text
    
    def _extract_keywords(self, text, top_k=20):
        """Extract top keywords from text using frequency analysis."""
        words = word_tokenize(text.lower())
        words = [self.stemmer.stem(word) for word in words if word.isalnum() and word not in self.stop_words and len(word) > 2]
        
        word_freq = Counter(words)
        return dict(word_freq.most_common(top_k))
    
    def _calculate_sentence_scores(self, sentences, keywords, text):
        """Calculate scores for each sentence based on multiple criteria."""
        scores = []
        total_sentences = len(sentences)
        
        for i, sentence in enumerate(sentences):
            score = 0
            sentence_words = word_tokenize(sentence.lower())
            sentence_words = [self.stemmer.stem(word) for word in sentence_words if word.isalnum()]
            
            # 1. Keyword frequency score (40% weight)
            keyword_score = sum(keywords.get(word, 0) for word in sentence_words)
            if sentence_words:
                keyword_score = keyword_score / len(sentence_words)
            score += keyword_score * 0.4
            
            # 2. Position score (25% weight) - First and last sentences are important
            if i == 0:  # First sentence
                position_score = 1.0
            elif i == total_sentences - 1:  # Last sentence
                position_score = 0.8
            elif i < total_sentences * 0.3:  # First 30%
                position_score = 0.7
            elif i > total_sentences * 0.7:  # Last 30%
                position_score = 0.6
            else:
                position_score = 0.5
            score += position_score * 0.25
            
            # 3. Sentence length score (15% weight) - Prefer medium-length sentences
            sentence_length = len(sentence_words)
            if 10 <= sentence_length <= 25:
                length_score = 1.0
            elif 5 <= sentence_length < 10 or 25 < sentence_length <= 35:
                length_score = 0.8
            else:
                length_score = 0.5
            score += length_score * 0.15
            
            # 4. Numerical data score (10% weight) - Sentences with numbers are often important
            numerical_score = 1.0 if re.search(r'\d+', sentence) else 0.5
            score += numerical_score * 0.1
            
            # 5. Question and exclamation score (10% weight)
            punctuation_score = 1.2 if sentence.endswith(('?', '!')) else 1.0
            score += punctuation_score * 0.1
            
            scores.append(score)
        
        return scores
    
    def _select_top_sentences(self, sentences, scores, max_words):
        """Select top sentences while respecting word limit."""
        # Sort sentences by score
        sentence_score_pairs = list(zip(sentences, scores, range(len(sentences))))
        sentence_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        selected_sentences = []
        current_word_count = 0
        selected_indices = []
        
        for sentence, score, original_index in sentence_score_pairs:
            sentence_word_count = len(sentence.split())
            
            if current_word_count + sentence_word_count <= max_words:
                selected_sentences.append((sentence, original_index))
                selected_indices.append(original_index)
                current_word_count += sentence_word_count
            
            if current_word_count >= max_words * 0.9:  # Stop when we're close to the limit
                break
        
        # Sort selected sentences by original order to maintain flow
        selected_sentences.sort(key=lambda x: x[1])
        return [sentence for sentence, _ in selected_sentences]
    
    def summarize(self, text):
        """Generate rule-based summary."""
        try:
            # Clean the input text
            cleaned_text = self._clean_text(text)
            
            # Split into sentences
            sentences = self._simple_sentence_tokenize(cleaned_text)
            
            if len(sentences) <= 3:
                # If text is very short, return as is (up to max_words)
                words = cleaned_text.split()
                if len(words) <= self.max_words:
                    return cleaned_text
                else:
                    return ' '.join(words[:self.max_words])
            
            # Extract keywords
            keywords = self._extract_keywords(cleaned_text)
            
            # Calculate sentence scores
            scores = self._calculate_sentence_scores(sentences, keywords, cleaned_text)
            
            # Select top sentences
            summary_sentences = self._select_top_sentences(sentences, scores, self.max_words)
            
            # Join sentences to form summary
            summary = ' '.join(summary_sentences)
            
            # Final word count check and truncation if needed
            words = summary.split()
            if len(words) > self.max_words:
                summary = ' '.join(words[:self.max_words])
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error in rule-based summarization: {e}")
            # Ultra fallback - return first few sentences up to word limit
            sentences = text.split('.')[:5]  # Take first 5 sentences
            fallback_summary = '. '.join(sentences)
            words = fallback_summary.split()
            if len(words) > self.max_words:
                fallback_summary = ' '.join(words[:self.max_words])
            return fallback_summary.strip()

def _get_model_pipeline(model_name: str):
    """Initialize the appropriate model pipeline."""
    models = {
        "bart": "facebook/bart-large-cnn",
        "pegasus": "google/pegasus-cnn_dailymail", 
        "t5": "t5-base"
    }
    
    if model_name not in models:
        raise ValueError(f"Unknown model: {model_name}")
    
    try:
        return pipeline("summarization", model=models[model_name], framework="pt")
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {e}")
        # Fallback to BART if model loading fails
        logger.info("Falling back to BART model...")
        return pipeline("summarization", model="facebook/bart-large-cnn", framework="pt")

def _preprocess_text_for_model(text: str, model_name: str) -> str:
    """Preprocess text based on model requirements."""
    if model_name == "t5":
        return f"summarize: {text}"
    return text

def _handle_long_text(text: str, model_name: str, max_length: int, min_length: int, summarizer):
    """Handle long text by chunking appropriately for each model."""
    max_input_lengths = {
        "bart": 1024,
        "pegasus": 512,
        "t5": 512
    }
    
    max_input_length = max_input_lengths.get(model_name, 1024)
    
    if len(text) <= max_input_length:
        processed_text = _preprocess_text_for_model(text, model_name)
        try:
            result = summarizer(processed_text, 
                              max_length=max_length, 
                              min_length=min_length, 
                              do_sample=False)
            return result[0]["summary_text"]
        except Exception as e:
            logger.error(f"Error with single chunk summarization: {e}")
            # Try with shorter text
            shorter_text = text[:max_input_length//2]
            processed_text = _preprocess_text_for_model(shorter_text, model_name)
            result = summarizer(processed_text, 
                              max_length=max_length, 
                              min_length=min_length, 
                              do_sample=False)
            return result[0]["summary_text"]
    else:
        # Handle long text with chunks
        chunks = [text[i:i+max_input_length] for i in range(0, len(text), max_input_length//2)]
        summaries = []
        
        chunk_max_length = min(max_length//len(chunks) + 30, max_length//2)
        chunk_min_length = max(min_length//len(chunks), 10)
        
        for chunk in chunks:
            try:
                processed_chunk = _preprocess_text_for_model(chunk, model_name)
                result = summarizer(processed_chunk, 
                                  max_length=chunk_max_length, 
                                  min_length=chunk_min_length, 
                                  do_sample=False)
                summaries.append(result[0]["summary_text"])
            except Exception as e:
                logger.error(f"Error processing chunk: {e}")
                # Skip problematic chunks
                continue
        
        if not summaries:
            raise Exception("Failed to process any text chunks")
        
        combined = " ".join(summaries)
        if len(combined.split()) > max_length:
            try:
                processed_combined = _preprocess_text_for_model(combined, model_name)
                result = summarizer(processed_combined, 
                                  max_length=max_length, 
                                  min_length=min_length, 
                                  do_sample=False)
                return result[0]["summary_text"]
            except Exception as e:
                logger.error(f"Error re-summarizing combined text: {e}")
                # Return truncated version if re-summarization fails
                return " ".join(combined.split()[:max_length])
        
        return combined

def _summarize_with_timeout(text: str, options: dict, timeout: int = 60):
    """Execute summarization with timeout."""
    result = {"summary": None, "error": None}
    
    def target():
        try:
            model_name = options["model"]
            max_length = options.get("max_length", 150)
            min_length = options.get("min_length", 50)
            
            # Initialize the model
            summarizer = _get_model_pipeline(model_name)
            
            # Generate summary
            summary = _handle_long_text(text, model_name, max_length, min_length, summarizer)
            result["summary"] = summary.strip()
            
        except Exception as e:
            result["error"] = str(e)
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        # Thread is still running, timeout occurred
        logger.warning(f"Neural model timeout after {timeout} seconds")
        return None, "Timeout"
    
    return result["summary"], result["error"]

def summarize_with_options(text: str, options: dict) -> str:
    """Generate a summary using the appropriate model with rule-based fallback."""
    try:
        # First, try the neural model with timeout
        start_time = time.time()
        summary, error = _summarize_with_timeout(text, options, timeout=60)
        neural_time = time.time() - start_time
        
        if summary is not None and error is None:
            logger.info(f"Neural model succeeded in {neural_time:.2f} seconds")
            return summary
        
        # Neural model failed or timed out, use rule-based fallback
        logger.warning(f"Neural model failed/timeout (reason: {error}), using rule-based fallback")
        
        # Initialize rule-based summarizer
        rule_summarizer = RuleBasedSummarizer(max_words=500)
        
        # Generate rule-based summary
        fallback_start = time.time()
        rule_summary = rule_summarizer.summarize(text)
        fallback_time = time.time() - fallback_start
        
        logger.info(f"Rule-based fallback completed in {fallback_time:.2f} seconds")
        return rule_summary
        
    except Exception as e:
        logger.error(f"Error in summarization process: {e}")
        
        # Final fallback - try BART with rule-based backup
        try:
            logger.info("Attempting final BART fallback...")
            summary, error = _summarize_with_timeout(text, {"model": "bart", "max_length": 150, "min_length": 50}, timeout=30)
            
            if summary is not None and error is None:
                return summary
            else:
                # Even BART failed, use rule-based
                logger.info("BART also failed, using rule-based as final fallback")
                rule_summarizer = RuleBasedSummarizer(max_words=500)
                return rule_summarizer.summarize(text)
                
        except Exception as final_error:
            logger.error(f"All summarization methods failed: {final_error}")
            # Ultra final fallback - return first portion of text
            words = text.split()[:500]
            return ' '.join(words) if words else "Unable to generate summary."

def get_model_info():
    """Return information about each model's strengths."""
    return {
        "bart": {
            "name": "BART (Bidirectional and Auto-Regressive Transformers)",
            "strengths": ["Detailed summaries", "Comprehensive analysis", "Good for longer content"],
            "best_for": ["Detailed Summary", "Long documents", "Academic content"]
        },
        "pegasus": {
            "name": "Pegasus (Pre-training with Extracted Gap-sentences)",
            "strengths": ["Abstractive summarization", "Concise summaries", "News articles"],
            "best_for": ["Brief Summary", "Abstract Summary", "News content"]
        },
        "t5": {
            "name": "T5 (Text-To-Text Transfer Transformer)", 
            "strengths": ["Flexible text generation", "Structured output", "Business content"],
            "best_for": ["Executive Summary", "Technical Summary", "Structured content"]
        },
        "rule_based": {
            "name": "Rule-Based Summarizer (Fallback)",
            "strengths": ["Fast processing", "Reliable", "Keyword-focused", "Position-aware"],
            "best_for": ["When neural models fail", "Timeout situations", "Consistent performance"]
        }
    }