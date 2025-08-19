


# from transformers import pipeline
# import logging
# import re

# logger = logging.getLogger(__name__)

# def get_summary_options():
#     """Return available summarization options with model assignments."""
#     return {
#         "1": {
#             "name": "Brief Summary", 
#             "max_length": 100, 
#             "min_length": 30,
#             "model": "pegasus",  # Best for concise, abstractive summaries
#             "description": "Quick, essential points using Pegasus"
#         },
#         "2": {
#             "name": "Detailed Summary", 
#             "max_length": 250, 
#             "min_length": 80,
#             "model": "bart",  # Best for comprehensive, detailed summaries
#             "description": "Comprehensive analysis using BART"
#         },
#         "3": {
#             "name": "Key Points", 
#             "max_length": 150, 
#             "min_length": 40,
#             "model": "extraction",  # Rule-based extraction
#             "description": "Bullet-point extraction using custom algorithm"
#         },
#         "4": {
#             "name": "Executive Summary", 
#             "max_length": 180, 
#             "min_length": 60,
#             "model": "t5",  # Good for structured, business-style summaries
#             "description": "Professional format using T5"
#         },
#         "5": {
#             "name": "Abstract Summary", 
#             "max_length": 120, 
#             "min_length": 50,
#             "model": "pegasus",  # Pegasus excels at abstractive summarization
#             "description": "Abstractive summary using Pegasus"
#         },
#         "6": {
#             "name": "Domain Specific Summary", 
#             "max_length": 200, 
#             "min_length": 70,
#             "model": "t5",
#             "description": "Adaptive summary based on document domain using T5"
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
    
#     return pipeline("summarization", model=models[model_name], framework="pt")

# def _extract_key_points(text: str, max_points: int = 6) -> str:
#     """Extract key points and format as bullet points."""
#     sentences = re.split(r'[.!?]+', text)
#     sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
    
#     # Score sentences for importance
#     scored_sentences = []
#     important_words = ['important', 'key', 'main', 'significant', 'critical', 'major', 
#                       'primary', 'essential', 'crucial', 'shows', 'indicates', 'found',
#                       'results', 'concluded', 'demonstrated', 'revealed', 'discovered',
#                       'therefore', 'however', 'moreover', 'furthermore', 'consequently']
    
#     for i, sentence in enumerate(sentences):
#         score = 0
#         # Early sentences are often more important
#         score += max(0, 8 - i * 0.5)
#         # Count important keywords
#         score += sum(2 for word in important_words if word.lower() in sentence.lower())
#         # Prefer medium-length sentences
#         if 40 < len(sentence) < 180:
#             score += 3
#         # Boost sentences with numbers/statistics
#         if re.search(r'\d+%|\d+\.\d+|\$\d+', sentence):
#             score += 2
#         scored_sentences.append((sentence, score))
    
#     # Get top sentences
#     scored_sentences.sort(key=lambda x: x[1], reverse=True)
#     top_sentences = [s[0] for s in scored_sentences[:max_points]]
    
#     # Format as clean bullet points
#     formatted_points = []
#     for point in top_sentences:
#         clean_point = point.strip()
#         if not clean_point.endswith('.'):
#             clean_point += '.'
#         formatted_points.append(f"• {clean_point}")
    
#     return "\n".join(formatted_points)

# def _format_summary_bart(summary: str, summary_type: str) -> str:
#     """Format BART summary - best for detailed, comprehensive summaries."""
#     summary = summary.strip()
#     if not summary.endswith('.'):
#         summary += '.'
    
#     sentences = re.split(r'(?<=[.!?])\s+', summary)
#     sentences = [s.strip() for s in sentences if s.strip()]
    
#     if summary_type == "Detailed Summary":
#         header = "📖 DETAILED SUMMARY (BART)\n" + "="*55 + "\n\n"
        
#         # Group sentences into paragraphs for better readability
#         paragraphs = []
#         current_paragraph = []
        
#         for i, sentence in enumerate(sentences):
#             current_paragraph.append(sentence)
#             if len(current_paragraph) >= 2 or i == len(sentences) - 1:
#                 paragraphs.append(" ".join(current_paragraph))
#                 current_paragraph = []
        
#         content = "\n\n".join(paragraphs)
#         footer = f"\n\n{'='*55}\n📊 Model: BART-Large-CNN (Optimized for detailed analysis)"
#         return f"{header}{content}{footer}"
    
#     return summary

# def _format_summary_pegasus(summary: str, summary_type: str) -> str:
#     """Format Pegasus summary - best for abstractive, concise summaries."""
#     summary = summary.strip()
#     if not summary.endswith('.'):
#         summary += '.'
    
#     if summary_type == "Brief Summary":
#         header = "📋 BRIEF SUMMARY (PEGASUS)\n" + "="*55 + "\n\n"
#         content = summary
#         footer = f"\n\n{'='*55}\n🎯 Model: Pegasus (Optimized for concise abstracts)"
#         return f"{header}{content}{footer}"
    
#     elif summary_type == "Abstract Summary":
#         header = "🔬 ABSTRACT SUMMARY (PEGASUS)\n" + "="*55 + "\n\n"
#         content = summary
#         footer = f"\n\n{'='*55}\n🎯 Model: Pegasus (Specialized for abstractive summarization)"
#         return f"{header}{content}{footer}"
    
#     return summary

# def _format_summary_domain_specific(summary: str, domain: str = "general") -> str:
#     """Format domain-specific summary with appropriate headers."""
#     summary = summary.strip()
#     if not summary.endswith('.'):
#         summary += '.'
    
#     domain_headers = {
#         "technical": "🔧 TECHNICAL SUMMARY (T5)",
#         "medical": "🏥 MEDICAL SUMMARY (T5)", 
#         "legal": "⚖️ LEGAL SUMMARY (T5)",
#         "financial": "💰 FINANCIAL SUMMARY (T5)",
#         "academic": "🎓 ACADEMIC SUMMARY (T5)",
#         "business": "💼 BUSINESS SUMMARY (T5)",
#         "general": "🎯 DOMAIN SUMMARY (T5)"
#     }
    
#     header = domain_headers.get(domain, domain_headers["general"]) + "\n" + "="*55 + "\n\n"
    
#     sentences = re.split(r'(?<=[.!?])\s+', summary)
#     sentences = [s.strip() for s in sentences if s.strip()]
    
#     if len(sentences) >= 2:
#         content = f"📋 OVERVIEW:\n{sentences[0]}\n\n🔍 ANALYSIS:\n{' '.join(sentences[1:])}"
#     else:
#         content = f"📋 SUMMARY:\n{summary}"
    
#     footer = f"\n\n{'='*55}\n🎯 Model: T5-Base (Optimized for {domain} content)"
#     return f"{header}{content}{footer}"

# def _format_summary_t5(summary: str, summary_type: str, domain: str = "general") -> str:
#     """Format T5 summary - best for structured, flexible summaries."""
#     summary = summary.strip()
#     if not summary.endswith('.'):
#         summary += '.'
    
#     sentences = re.split(r'(?<=[.!?])\s+', summary)
#     sentences = [s.strip() for s in sentences if s.strip()]
    
#     if summary_type == "Domain Specific Summary":
#         return _format_summary_domain_specific(summary, domain)
#     elif summary_type == "Executive Summary":
#         header = "💼 EXECUTIVE SUMMARY (T5)\n" + "="*55 + "\n\n"
        
#         if len(sentences) >= 3:
#             overview = sentences[0]
#             insights = " ".join(sentences[1:])
#             content = f"📌 OVERVIEW:\n{overview}\n\n🔍 KEY INSIGHTS:\n{insights}"
#         else:
#             content = f"📌 SUMMARY:\n{summary}"
        
#         footer = f"\n\n{'='*55}\n🏢 Model: T5-Base (Optimized for business summaries)"
#         return f"{header}{content}{footer}"
#     elif summary_type == "Technical Summary":
#         header = "🔧 TECHNICAL SUMMARY (T5)\n" + "="*55 + "\n\n"
#         content = f"📋 TECHNICAL OVERVIEW:\n{summary}"
#         footer = f"\n\n{'='*55}\n⚙️ Model: T5-Base (Optimized for technical content)"
#         return f"{header}{content}{footer}"
    
#     return summary

# def _preprocess_text_for_model(text: str, model_name: str) -> str:
#     """Preprocess text based on model requirements."""
#     if model_name == "t5":
#         # T5 expects task prefix
#         return f"summarize: {text}"
#     return text

# def _handle_long_text(text: str, model_name: str, max_length: int, min_length: int, summarizer):
#     """Handle long text by chunking appropriately for each model."""
#     # Different models have different optimal input lengths
#     max_input_lengths = {
#         "bart": 1024,
#         "pegasus": 512,  # Pegasus has shorter input limit
#         "t5": 512
#     }
    
#     max_input_length = max_input_lengths.get(model_name, 1024)
    
#     if len(text) <= max_input_length:
#         # Single chunk
#         processed_text = _preprocess_text_for_model(text, model_name)
#         result = summarizer(processed_text, 
#                           max_length=max_length, 
#                           min_length=min_length, 
#                           do_sample=False)
#         return result[0]["summary_text"]
#     else:
#         # Multiple chunks
#         chunks = [text[i:i+max_input_length] for i in range(0, len(text), max_input_length//2)]  # Overlap chunks
#         summaries = []
        
#         chunk_max_length = min(max_length//len(chunks) + 30, max_length//2)
#         chunk_min_length = max(min_length//len(chunks), 10)
        
#         for chunk in chunks:
#             processed_chunk = _preprocess_text_for_model(chunk, model_name)
#             result = summarizer(processed_chunk, 
#                               max_length=chunk_max_length, 
#                               min_length=chunk_min_length, 
#                               do_sample=False)
#             summaries.append(result[0]["summary_text"])
        
#         # Combine and re-summarize if needed
#         combined = " ".join(summaries)
#         if len(combined.split()) > max_length:
#             # Re-summarize the combined text
#             processed_combined = _preprocess_text_for_model(combined, model_name)
#             result = summarizer(processed_combined, 
#                               max_length=max_length, 
#                               min_length=min_length, 
#                               do_sample=False)
#             return result[0]["summary_text"]
        
#         return combined

# def summarize_with_options(text: str, options: dict, domain: str = "general") -> str:
#     """Generate a summary using the appropriate model based on summary type."""
#     try:
#         summary_type = options["name"]
#         model_name = options["model"]
        
#         # Handle Key Points separately with extraction
#         if model_name == "extraction":
#             header = "🔑 KEY POINTS (EXTRACTION)\n" + "="*55 + "\n\n"
#             points = _extract_key_points(text)
#             footer = f"\n\n{'='*55}\n🧠 Method: Rule-based extraction algorithm"
#             return f"{header}{points}{footer}"
        
#         # Initialize the appropriate model
#         summarizer = _get_model_pipeline(model_name)
#         max_length = options.get("max_length", 150)
#         min_length = options.get("min_length", 50)
        
#         # Generate summary using the selected model
#         summary = _handle_long_text(text, model_name, max_length, min_length, summarizer)
        
#         # Format based on model type
#         if model_name == "bart":
#             formatted_summary = _format_summary_bart(summary, summary_type)
#         elif model_name == "pegasus":
#             formatted_summary = _format_summary_pegasus(summary, summary_type)
#         elif model_name == "t5":
#             formatted_summary = _format_summary_t5(summary, summary_type, domain)
#         else:
#             formatted_summary = summary
        
#         return formatted_summary
        
#     except Exception as e:
#         logger.error(f"Error generating summary with {options.get('model', 'unknown')} model: {e}")
#         # Fallback to BART if the selected model fails
#         try:
#             logger.info("Falling back to BART model...")
#             summarizer = _get_model_pipeline("bart")
#             summary = _handle_long_text(text, "bart", options.get("max_length", 150), 
#                                       options.get("min_length", 50), summarizer)
#             return f"⚠️ FALLBACK SUMMARY (BART)\n{'='*50}\n\n{summary}\n\n{'='*50}\nNote: Primary model failed, used BART as fallback"
#         except Exception as fallback_error:
#             logger.error(f"Fallback also failed: {fallback_error}")
#             raise Exception(f"Both primary ({options.get('model', 'unknown')}) and fallback (BART) models failed")

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
#         },
#         "extraction": {
#             "name": "Rule-based Extraction",
#             "strengths": ["Key point identification", "Fast processing", "Preserves original phrasing"],
#             "best_for": ["Key Points", "Quick overviews", "Bullet-point format"]
#         }
#     }

# # Example usage function
# def display_summary_options():
#     """Display available summary options with model information."""
#     options = get_summary_options()
#     model_info = get_model_info()
    
#     print("📚 AVAILABLE SUMMARY OPTIONS\n" + "="*60)
    
#     for key, option in options.items():
#         model = option["model"]
#         model_name = model_info[model]["name"]
#         print(f"\n{key}. {option['name']}")
#         print(f"   📖 Description: {option['description']}")
#         print(f"   🤖 Model: {model_name}")
#         print(f"   📏 Length: {option['min_length']}-{option['max_length']} words")
#         print(f"   🎯 Best for: {', '.join(model_info[model]['best_for'])}")
    
#     print(f"\n{'='*60}")

# # Example of how to use the system
# if __name__ == "__main__":
#     # Display available options
#     display_summary_options()
    
#     # Example text
#     sample_text = """
#     Artificial intelligence has revolutionized many industries in recent years. 
#     Machine learning algorithms can now process vast amounts of data to identify 
#     patterns and make predictions. This technology is being used in healthcare 
#     to diagnose diseases, in finance to detect fraud, and in transportation 
#     to develop autonomous vehicles. However, there are also concerns about job 
#     displacement and privacy issues that need to be addressed as AI continues to evolve.
#     """
    
#     # Get summary options
#     options = get_summary_options()
    
#     # Try different summary types
#     for key, option in list(options.items())[:3]:  # Try first 3 options
#         print(f"\n\n{'='*70}")
#         print(f"TESTING OPTION {key}: {option['name']}")
#         print('='*70)
        
#         try:
#             result = summarize_with_options(sample_text, option)
#             print(result)
#         except Exception as e:
#             print(f"❌ Error: {e}")




from transformers import pipeline
import logging
import re

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

def _get_model_pipeline(model_name: str):
    """Initialize the appropriate model pipeline."""
    models = {
        "bart": "facebook/bart-large-cnn",
        "pegasus": "google/pegasus-cnn_dailymail", 
        "t5": "t5-base"
    }
    
    if model_name not in models:
        raise ValueError(f"Unknown model: {model_name}")
    
    return pipeline("summarization", model=models[model_name], framework="pt")

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
            processed_chunk = _preprocess_text_for_model(chunk, model_name)
            result = summarizer(processed_chunk, 
                              max_length=chunk_max_length, 
                              min_length=chunk_min_length, 
                              do_sample=False)
            summaries.append(result[0]["summary_text"])
        
        combined = " ".join(summaries)
        if len(combined.split()) > max_length:
            processed_combined = _preprocess_text_for_model(combined, model_name)
            result = summarizer(processed_combined, 
                              max_length=max_length, 
                              min_length=min_length, 
                              do_sample=False)
            return result[0]["summary_text"]
        
        return combined

def summarize_with_options(text: str, options: dict) -> str:
    """Generate a summary using the appropriate model."""
    try:
        model_name = options["model"]
        max_length = options.get("max_length", 150)
        min_length = options.get("min_length", 50)
        
        # Initialize the model
        summarizer = _get_model_pipeline(model_name)
        
        # Generate summary
        summary = _handle_long_text(text, model_name, max_length, min_length, summarizer)
        
        return summary.strip()
        
    except Exception as e:
        logger.error(f"Error generating summary with {options.get('model', 'unknown')} model: {e}")
        # Fallback to BART
        try:
            logger.info("Falling back to BART model...")
            summarizer = _get_model_pipeline("bart")
            summary = _handle_long_text(text, "bart", max_length, min_length, summarizer)
            return summary.strip()
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            raise Exception(f"Both primary and fallback models failed")