# from transformers import pipeline
# import logging

# logger = logging.getLogger(__name__)

# def get_summary_options():
#     """Return available summarization options."""
#     return {
#         "1": {"name": "Brief Summary", "max_length": 150, "min_length": 30},
#         "2": {"name": "Detailed Summary", "max_length": 300, "min_length": 100},
#         "3": {"name": "Technical Summary", "max_length": 200, "min_length": 50},
#         "4": {"name": "Business Summary", "max_length": 200, "min_length": 50},
#         "5": {"name": "Key Points Only", "max_length": 200, "min_length": 50}
#     }

# def summarize_with_options(text: str, options: dict) -> str:
#     """Generate a summary using the transformers pipeline with PyTorch."""
#     try:
#         # Explicitly specify PyTorch framework
#         summarizer = pipeline("summarization", model="facebook/bart-large-cnn", framework="pt")
#         max_length = options.get("max_length", 150)
#         min_length = options.get("min_length", 30)
        
#         # Split text into chunks if too long
#         max_input_length = 1024  # BART's max input length
#         chunks = [text[i:i+max_input_length] for i in range(0, len(text), max_input_length)]
        
#         summaries = []
#         for chunk in chunks:
#             summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
#             summaries.append(summary[0]["summary_text"])
        
#         # Combine summaries
#         combined_summary = " ".join(summaries)
        
#         # For key points, format as bullet points
#         if options["name"] == "Key Points Only":
#             points = [f"- {point.strip()}" for point in combined_summary.split(". ") if point.strip()]
#             return "\n".join(points)
        
#         return combined_summary
#     except Exception as e:
#         logger.error(f"Error generating summary: {e}")
#         raise




from transformers import pipeline
import logging
import re

logger = logging.getLogger(__name__)

def get_summary_options():
    """Return available summarization options."""
    return {
        "1": {"name": "Brief Summary", "max_length": 100, "min_length": 30},
        "2": {"name": "Detailed Summary", "max_length": 250, "min_length": 80},
        "3": {"name": "Key Points", "max_length": 150, "min_length": 40},
        "4": {"name": "Executive Summary", "max_length": 180, "min_length": 60}
    }

def _extract_key_points(text: str, max_points: int = 6) -> str:
    """Extract key points and format as bullet points."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
    
    # Score sentences for importance
    scored_sentences = []
    important_words = ['important', 'key', 'main', 'significant', 'critical', 'major', 
                      'primary', 'essential', 'crucial', 'shows', 'indicates', 'found',
                      'results', 'concluded', 'demonstrated', 'revealed', 'discovered']
    
    for i, sentence in enumerate(sentences):
        score = 0
        # Early sentences are often more important
        score += max(0, 8 - i * 0.5)
        # Count important keywords
        score += sum(2 for word in important_words if word.lower() in sentence.lower())
        # Prefer medium-length sentences
        if 40 < len(sentence) < 180:
            score += 3
        scored_sentences.append((sentence, score))
    
    # Get top sentences
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    top_sentences = [s[0] for s in scored_sentences[:max_points]]
    
    # Format as clean bullet points
    formatted_points = []
    for point in top_sentences:
        clean_point = point.strip()
        if not clean_point.endswith('.'):
            clean_point += '.'
        formatted_points.append(f"• {clean_point}")
    
    return "\n".join(formatted_points)

def _format_summary(summary: str, summary_type: str) -> str:
    """Format the summary nicely based on type."""
    # Clean up the summary
    summary = summary.strip()
    if not summary.endswith('.'):
        summary += '.'
    
    # Split into sentences for better formatting
    sentences = re.split(r'(?<=[.!?])\s+', summary)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if summary_type == "Brief Summary":
        # Simple, clean format
        header = "📋 BRIEF SUMMARY\n" + "="*50 + "\n\n"
        content = " ".join(sentences)
        return f"{header}{content}\n\n{'='*50}"
    
    elif summary_type == "Detailed Summary":
        # Paragraph format with better spacing
        header = "📖 DETAILED SUMMARY\n" + "="*50 + "\n\n"
        
        # Group sentences into paragraphs (every 2-3 sentences)
        paragraphs = []
        current_paragraph = []
        
        for i, sentence in enumerate(sentences):
            current_paragraph.append(sentence)
            if len(current_paragraph) >= 2 or i == len(sentences) - 1:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
        
        content = "\n\n".join(paragraphs)
        return f"{header}{content}\n\n{'='*50}"
    
    elif summary_type == "Executive Summary":
        # Professional business format
        header = "💼 EXECUTIVE SUMMARY\n" + "="*50 + "\n\n"
        
        # Add overview and key insights sections
        if len(sentences) >= 3:
            overview = sentences[0]
            insights = " ".join(sentences[1:])
            content = f"OVERVIEW:\n{overview}\n\nKEY INSIGHTS:\n{insights}"
        else:
            content = " ".join(sentences)
        
        return f"{header}{content}\n\n{'='*50}"
    
    else:  # Default formatting
        return summary

def summarize_with_options(text: str, options: dict) -> str:
    """Generate a nicely formatted summary using BART model."""
    try:
        summary_type = options["name"]
        
        # Handle Key Points separately with extraction
        if summary_type == "Key Points":
            header = "🔑 KEY POINTS\n" + "="*50 + "\n\n"
            points = _extract_key_points(text)
            return f"{header}{points}\n\n{'='*50}"
        
        # Use BART for other summary types
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn", framework="pt")
        max_length = options.get("max_length", 150)
        min_length = options.get("min_length", 50)
        
        # Handle long text by chunking
        max_input_length = 1024
        if len(text) <= max_input_length:
            # Single chunk
            result = summarizer(text, 
                              max_length=max_length, 
                              min_length=min_length, 
                              do_sample=False)
            summary = result[0]["summary_text"]
        else:
            # Multiple chunks
            chunks = [text[i:i+max_input_length] for i in range(0, len(text), max_input_length)]
            summaries = []
            
            for chunk in chunks:
                result = summarizer(chunk, 
                                  max_length=max_length//len(chunks) + 50, 
                                  min_length=min_length//len(chunks), 
                                  do_sample=False)
                summaries.append(result[0]["summary_text"])
            
            summary = " ".join(summaries)
        
        # Format the summary nicely
        formatted_summary = _format_summary(summary, summary_type)
        return formatted_summary
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise