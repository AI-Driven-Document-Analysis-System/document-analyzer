from typing import List, Dict, Any
import logging
import os
import json

logger = logging.getLogger(__name__)


class DocumentAwareAugmenter:
    """
    Enhances document chunks with contextual information for improved retrieval.
    
    This module augments each chunk with LLM-generated context that explains
    the chunk's content and its relationship to the overall document, improving
    semantic understanding and retrieval accuracy.
    """
    
    def __init__(self, llm=None):
        """
        Initialize the document-aware augmenter.
        
        Args:
            llm: Language model instance for generating contextual summaries
        """
        self.llm = llm
    
    def augment_chunks_with_context(
        self, 
        chunks: List[Dict[str, Any]], 
        document_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Augment document chunks with contextual information using batch LLM processing.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata' keys
            document_data: Original document data for context generation
            
        Returns:
            List of chunks with augmented text containing contextual information
        """
        if not chunks:
            return chunks
        
        if not self.llm:
            logger.debug("LLM not available for augmentation, using standard chunks")
            return chunks
        
        try:
            logger.info(f"Augmenting {len(chunks)} chunks with document-aware context")
            
            contexts = self._generate_contexts_batch(chunks, document_data)
            
            augmented_chunks = []
            for i, chunk in enumerate(chunks):
                context = contexts.get(i, "")
                if context:
                    augmented_text = f"{context}\n\n{chunk['text']}"
                    augmented_chunks.append({
                        'text': augmented_text,
                        'metadata': chunk['metadata']
                    })
                else:
                    augmented_chunks.append(chunk)
            
            logger.info(f"Successfully augmented {len(augmented_chunks)} chunks")
            return augmented_chunks
            
        except Exception as e:
            logger.error(f"Error during chunk augmentation: {e}")
            return chunks
    
    def _generate_contexts_batch(
        self, 
        chunks: List[Dict[str, Any]], 
        document_data: Dict[str, Any]
    ) -> Dict[int, str]:
        """
        Generate context for multiple chunks in a single LLM call.
        
        Args:
            chunks: List of chunks to generate context for
            document_data: Document metadata for context
            
        Returns:
            Dictionary mapping chunk index to generated context
        """
        try:
            document_title = document_data.get('filename', 'document')
            document_type = document_data.get('type', 'unknown')
            
            batch_size = 50
            all_contexts = {}
            
            for batch_start in range(0, len(chunks), batch_size):
                batch_end = min(batch_start + batch_size, len(chunks))
                batch_chunks = chunks[batch_start:batch_end]
                
                prompt = self._build_batch_prompt(batch_chunks, document_title, document_type, batch_start)
                
                response = self.llm.invoke(prompt)
                
                if hasattr(response, 'content'):
                    response_text = response.content
                else:
                    response_text = str(response)
                
                batch_contexts = self._parse_batch_response(response_text, batch_start)
                all_contexts.update(batch_contexts)
            
            return all_contexts
            
        except Exception as e:
            logger.error(f"Error in batch context generation: {e}")
            return {}
    
    def _build_batch_prompt(
        self, 
        chunks: List[Dict[str, Any]], 
        document_title: str,
        document_type: str,
        start_index: int
    ) -> str:
        """
        Build a prompt for batch context generation.
        
        Args:
            chunks: Batch of chunks to process
            document_title: Title of the document
            document_type: Type of document
            start_index: Starting index for this batch
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are analyzing a {document_type} document titled "{document_title}".

For each chunk below, provide a brief 1-2 sentence context that explains what the chunk discusses and how it relates to the overall document. This context will be prepended to the chunk to improve search retrieval.

Return your response as a JSON array with this exact format:
[
  {{"index": 0, "context": "brief context here"}},
  {{"index": 1, "context": "brief context here"}}
]

Chunks to analyze:

"""
        
        for i, chunk in enumerate(chunks):
            chunk_text = chunk['text'][:500]
            prompt += f"\n--- Chunk {i} ---\n{chunk_text}\n"
        
        prompt += "\n\nProvide the JSON array of contexts now:"
        
        return prompt
    
    def _parse_batch_response(self, response: str, offset: int) -> Dict[int, str]:
        """
        Parse the LLM response containing batch contexts.
        
        Args:
            response: LLM response text
            offset: Index offset for this batch
            
        Returns:
            Dictionary mapping absolute chunk index to context
        """
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON array found in response")
                return {}
            
            json_str = response[json_start:json_end]
            contexts_list = json.loads(json_str)
            
            contexts = {}
            for item in contexts_list:
                if isinstance(item, dict) and 'index' in item and 'context' in item:
                    absolute_index = offset + item['index']
                    contexts[absolute_index] = item['context'].strip()
            
            return contexts
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return self._fallback_parse(response, offset)
        except Exception as e:
            logger.error(f"Error parsing batch response: {e}")
            return {}
    
    def _fallback_parse(self, response: str, offset: int) -> Dict[int, str]:
        """
        Fallback parser for non-JSON responses.
        
        Args:
            response: Response text
            offset: Index offset
            
        Returns:
            Dictionary of parsed contexts
        """
        contexts = {}
        lines = response.split('\n')
        
        current_index = None
        current_context = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Chunk') and ':' in line:
                if current_index is not None and current_context:
                    contexts[offset + current_index] = ' '.join(current_context)
                
                try:
                    index_str = line.split()[1].rstrip(':')
                    current_index = int(index_str)
                    current_context = []
                    
                    context_part = line.split(':', 1)[1].strip()
                    if context_part:
                        current_context.append(context_part)
                except (ValueError, IndexError):
                    continue
            elif current_index is not None and line:
                current_context.append(line)
        
        if current_index is not None and current_context:
            contexts[offset + current_index] = ' '.join(current_context)
        
        return contexts
