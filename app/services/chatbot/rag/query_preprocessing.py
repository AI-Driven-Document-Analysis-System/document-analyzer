"""
Query Preprocessing Module for RAG Chatbot

This module provides text preprocessing functionality for user queries to improve
retrieval accuracy and search quality in the RAG system.

Features:
- Lowercase conversion for case-insensitive matching
- Extra whitespace removal for clean text
- Spell correction using pyspellchecker library
- Comprehensive query normalization pipeline
"""

import re
import logging
from typing import Optional
from spellchecker import SpellChecker

logger = logging.getLogger(__name__)


class QueryPreprocessor:
    """
    Handles preprocessing of user queries for improved RAG retrieval.

    This class implements various text normalization techniques to enhance
    the quality of user input before it's used for similarity search in
    the vector database.
    """

    def __init__(self, language: str = 'en'):
        """
        Initialize the query preprocessor.

        Args:
            language (str): Language code for spell checker (default: 'en')
        """
        self.spell_checker = SpellChecker(language=language)
        logger.info(f"QueryPreprocessor initialized with language: {language}")

    def convert_to_lowercase(self, text: str) -> str:
        """
        Convert text to lowercase for case-insensitive matching.

        This ensures that queries like "AI" and "ai" are treated identically
        during similarity search, improving retrieval accuracy.

        Args:
            text (str): Input text to convert

        Returns:
            str: Lowercase version of the input text
        """
        return text.lower()

    def remove_extra_whitespace(self, text: str) -> str:
        """
        Remove extra whitespace characters from text.

        This includes:
        - Multiple consecutive spaces
        - Leading and trailing whitespace
        - Tab characters and newlines

        Args:
            text (str): Input text to clean

        Returns:
            str: Text with normalized whitespace
        """
        # Replace multiple whitespace characters with single space
        text = re.sub(r'\s+', ' ', text)

        # Remove leading and trailing whitespace
        text = text.strip()

        return text

    def correct_spelling(self, text: str) -> str:
        """
        Correct spelling errors in the input text using pyspellchecker.

        This improves retrieval by ensuring misspelled words don't cause
        vocabulary mismatches with the stored document content.

        Args:
            text (str): Input text with potential spelling errors

        Returns:
            str: Text with corrected spelling
        """
        words = text.split()
        corrected_words = []

        for word in words:
            # Check if word is in the dictionary
            if word in self.spell_checker:
                corrected_words.append(word)
            else:
                # Get the most likely correction
                correction = self.spell_checker.correction(word)
                if correction:
                    corrected_words.append(correction)
                    logger.debug(f"Spell correction: '{word}' -> '{correction}'")
                else:
                    # Keep original word if no correction found
                    corrected_words.append(word)

        return ' '.join(corrected_words)

    def preprocess_query(self, query: str) -> str:
        """
        Apply complete preprocessing pipeline to user query.

        This method applies all preprocessing steps in the correct order:
        1. Convert to lowercase
        2. Remove extra whitespace
        3. Correct spelling errors

        Args:
            query (str): Raw user query

        Returns:
            str: Preprocessed query ready for similarity search
        """
        if not query or not isinstance(query, str):
            return ""

        try:
            # Step 1: Convert to lowercase
            processed_query = self.convert_to_lowercase(query)

            # Step 2: Remove extra whitespace
            processed_query = self.remove_extra_whitespace(processed_query)

            # Step 3: Correct spelling
            processed_query = self.correct_spelling(processed_query)

            logger.info(f"Query preprocessing: '{query}' -> '{processed_query}'")
            return processed_query

        except Exception as e:
            logger.error(f"Error preprocessing query '{query}': {str(e)}")
            # Return original query if preprocessing fails
            return query

# Global preprocessor instance
query_preprocessor = QueryPreprocessor()


def preprocess_user_query(query: str) -> str:
    """
    Convenience function for preprocessing user queries.

    Args:
        query (str): Raw user query

    Returns:
        str: Preprocessed query
    """
    return query_preprocessor.preprocess_query(query)


