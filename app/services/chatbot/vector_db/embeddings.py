from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np


class EmbeddingGenerator:
    """
    A utility class for generating text embeddings using pre-trained transformer models.

    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the EmbeddingGenerator with a specified transformer model.
        
        Args:
            model_name (str): Name of the pre-trained model to use for embeddings.
                             Default is 'all-MiniLM-L6-v2' which offers good performance
                             with reasonable speed and memory usage.
        """
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Generate embeddings for one or more text inputs.
        
        This method can handle both single text strings and lists of texts,
        automatically converting single strings to lists for processing.
        
        Args:
            texts (Union[str, List[str]]): Single text string or list of text strings
                                          to generate embeddings for
                                          
        Returns:
            List[List[float]]: List of embedding vectors, where each vector is a list of floats
                               representing the semantic content of the corresponding input text
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate a single embedding for a query text.
        
        This method is optimized for generating embeddings for search queries,
        returning a single vector instead of a list of vectors.
        
        Args:
            query (str): The query text to generate an embedding for
            
        Returns:
            List[float]: Single embedding vector as a list of floats
        """
        embedding = self.model.encode([query])
        
        # Return the first (and only) embedding as a list
        return embedding[0].tolist()