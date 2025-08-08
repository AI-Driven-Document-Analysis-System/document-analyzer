from typing import List, Dict, Any
import re

class DocumentChunker:
    """
    This class provides methods to chunk documents based on different strategies:
    - Sentence-based chunking: Splits text at sentence boundaries
    - Layout-based chunking: Respects document structure (sections, headers, paragraphs)
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the DocumentChunker with specified chunk parameters.
        
        Args:
            chunk_size (int): Maximum number of characters per chunk (default: 1000)
            chunk_overlap (int): Number of characters to overlap between consecutive chunks (default: 200)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_by_sentences(self, text: str, document_metadata: Dict) -> List[Dict]:
        """
        Split text into chunks based on sentence boundaries while respecting chunk size limits.
        
        This method ensures that sentences are not split in the middle, maintaining
        semantic coherence while staying within the specified chunk size.
        
        Args:
            text (str): The input text to be chunked
            document_metadata (Dict): Metadata to be attached to each chunk
            
        Returns:
            List[Dict]: List of chunks, each containing 'text' and 'metadata' keys
        """
        # Split text into sentences using regex pattern that looks for sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        current_length = 0

        # Process each sentence and build chunks
        for sentence in sentences:
            sentence_length = len(sentence)

            # Check if adding this sentence would exceed the chunk size limit
            # Only create a new chunk if we already have content in the current chunk
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': {**document_metadata, 'chunk_index': len(chunks)}
                })

                # Create overlap by taking the last chunk_overlap characters from the previous chunk
                # This ensures context continuity between chunks
                overlap_text = current_chunk[-self.chunk_overlap:] if len(
                    current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
                current_length = len(current_chunk)
            else:
                # Add sentence to current chunk (either first sentence or fits within limit)
                current_chunk += " " + sentence if current_chunk else sentence
                current_length += sentence_length

        # Add the final chunk if there's remaining content
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': {**document_metadata, 'chunk_index': len(chunks)}
            })

        return chunks

    def chunk_by_layout(self, layout_data: Dict, document_metadata: Dict) -> List[Dict]:
        """
        Split document into chunks based on its layout structure (sections, paragraphs, headers).
        
        This method processes structured document data and creates chunks that respect
        the original document organization while maintaining chunk size constraints.
        
        Args:
            layout_data (Dict): Structured document data containing sections with text and metadata
            document_metadata (Dict): Base metadata to be attached to each chunk
            
        Returns:
            List[Dict]: List of chunks with enhanced metadata including layout information
        """
        chunks = []

        # Process each section in the layout data
        for section in layout_data.get('sections', []):
            # Only process sections that contain text content (paragraphs and headers)
            if section['type'] in ['paragraph', 'header']:
                text = section['text']
                
                # If the section text is longer than chunk size, split it into sub-chunks
                if len(text) > self.chunk_size:
                    sub_chunks = self.chunk_by_sentences(text, document_metadata)
                    # Enhance each sub-chunk with section-specific metadata
                    for chunk in sub_chunks:
                        chunk['metadata'].update({
                            'section_type': section['type'],
                            'page_number': section.get('page', 1),
                            'bbox': section.get('bbox', [])  # Bounding box coordinates
                        })
                    chunks.extend(sub_chunks)
                else:
                    # If section fits within chunk size, create a single chunk
                    # This preserves the original document structure
                    chunks.append({
                        'text': text,
                        'metadata': {
                            **document_metadata,
                            'section_type': section['type'],
                            'page_number': section.get('page', 1),
                            'bbox': section.get('bbox', []),
                            'chunk_index': len(chunks)
                        }
                    })

        return chunks