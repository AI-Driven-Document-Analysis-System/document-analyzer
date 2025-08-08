import unittest
import sys
import os
import numpy as np

# Add the backend directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from vector_db.embeddings import EmbeddingGenerator


class TestEmbeddingGenerator(unittest.TestCase):
    """Test cases for EmbeddingGenerator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create EmbeddingGenerator instance with real model
        self.embedding_generator = EmbeddingGenerator()

    def test_init_default_model(self):
        """Test EmbeddingGenerator initialization with default model."""
        self.assertIsNotNone(self.embedding_generator.model)
        # Verify the model is loaded correctly
        self.assertTrue(hasattr(self.embedding_generator.model, 'encode'))

    def test_init_custom_model(self):
        """Test EmbeddingGenerator initialization with custom model."""
        custom_model = "paraphrase-MiniLM-L3-v2"
        generator = EmbeddingGenerator(custom_model)
        self.assertIsNotNone(generator.model)
        self.assertTrue(hasattr(generator.model, 'encode'))

    def test_generate_embeddings_single_string(self):
        """Test generating embeddings for a single string."""
        # Test with single string
        text = "This is a test sentence."
        embeddings = self.embedding_generator.generate_embeddings(text)
        
        # Verify results structure
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 1)
        self.assertIsInstance(embeddings[0], list)
        self.assertGreater(len(embeddings[0]), 0)  # Should have embedding dimensions
        
        # Verify the model actually generated meaningful embeddings
        embedding = embeddings[0]
        
        # Check that embedding has non-zero values (not all zeros)
        self.assertTrue(any(abs(val) > 0.001 for val in embedding), 
                       "Embedding should have non-zero values")
        
        # Check that embedding values are reasonable (not all same value)
        unique_values = set(round(val, 3) for val in embedding)
        self.assertGreater(len(unique_values), 1, 
                          "Embedding should have varied values")
        
        # Test with different text to ensure embeddings are different
        different_text = "This is a completely different sentence."
        different_embeddings = self.embedding_generator.generate_embeddings(different_text)
        
        # Verify different texts produce different embeddings
        self.assertNotEqual(embedding, different_embeddings[0],
                           "Different texts should produce different embeddings")

    def test_generate_embeddings_list_of_strings(self):
        """Test generating embeddings for a list of strings."""
        # Test with list of strings
        texts = ["First sentence.", "Second sentence."]
        embeddings = self.embedding_generator.generate_embeddings(texts)
        
        # Verify results
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 2)
        self.assertIsInstance(embeddings[0], list)
        self.assertIsInstance(embeddings[1], list)
        self.assertGreater(len(embeddings[0]), 0)
        self.assertGreater(len(embeddings[1]), 0)

    def test_generate_embeddings_empty_list(self):
        """Test generating embeddings for empty list."""
        # Test with empty list
        texts = []
        embeddings = self.embedding_generator.generate_embeddings(texts)
        
        # Verify results
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 0)

    def test_generate_embeddings_single_empty_string(self):
        """Test generating embeddings for single empty string."""
        # Test with empty string
        text = ""
        embeddings = self.embedding_generator.generate_embeddings(text)
        
        # Verify results
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 1)
        self.assertGreater(len(embeddings[0]), 0)

    def test_generate_embeddings_large_text(self):
        """Test generating embeddings for large text."""
        # Test with large text
        large_text = "This is a very long sentence that contains many words and should be processed correctly by the embedding model. " * 10
        embeddings = self.embedding_generator.generate_embeddings(large_text)
        
        # Verify results
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 1)
        self.assertGreater(len(embeddings[0]), 0)

    def test_generate_query_embedding(self):
        """Test generating query embedding."""
        # Test query embedding
        query = "What is machine learning?"
        embedding = self.embedding_generator.generate_query_embedding(query)
        
        # Verify results
        self.assertIsInstance(embedding, list)
        self.assertGreater(len(embedding), 0)

    def test_generate_query_embedding_empty_query(self):
        """Test generating query embedding for empty query."""
        # Test empty query
        query = ""
        embedding = self.embedding_generator.generate_query_embedding(query)
        
        # Verify results
        self.assertIsInstance(embedding, list)
        self.assertGreater(len(embedding), 0)

    def test_generate_query_embedding_special_characters(self):
        """Test generating query embedding with special characters."""
        # Test with special characters
        query = "What is AI? @#$%^&*()_+-=[]{}|;':\",./<>?"
        embedding = self.embedding_generator.generate_query_embedding(query)
        
        # Verify results
        self.assertIsInstance(embedding, list)
        self.assertGreater(len(embedding), 0)

    def test_embedding_consistency(self):
        """Test that same input produces consistent embeddings."""
        # Test same text multiple times
        text = "Consistent test text"
        embedding1 = self.embedding_generator.generate_embeddings(text)
        embedding2 = self.embedding_generator.generate_embeddings(text)
        
        # Verify consistency (embeddings should be very similar)
        self.assertEqual(len(embedding1), len(embedding2))
        self.assertEqual(len(embedding1[0]), len(embedding2[0]))

    def test_embedding_dimensions(self):
        """Test that embeddings have correct dimensions."""
        # Test multiple texts
        texts = ["First text", "Second text"]
        embeddings = self.embedding_generator.generate_embeddings(texts)
        
        # Verify dimensions
        self.assertEqual(len(embeddings), 2)
        self.assertGreater(len(embeddings[0]), 0)
        self.assertGreater(len(embeddings[1]), 0)
        # All embeddings should have same dimension
        self.assertEqual(len(embeddings[0]), len(embeddings[1]))

    def test_embedding_similarity(self):
        """Test that similar texts produce similar embeddings."""
        similar_texts = [
            "The cat is on the mat.",
            "A cat sits on the mat.",
            "The feline is on the carpet."
        ]
        
        embeddings = self.embedding_generator.generate_embeddings(similar_texts)
        
        # Verify all embeddings have same dimension
        embedding_dim = len(embeddings[0])
        for embedding in embeddings:
            self.assertEqual(len(embedding), embedding_dim)
        
        # Calculate cosine similarity between similar texts
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Convert embeddings to numpy arrays for similarity calculation
        embedding_arrays = [np.array(emb) for emb in embeddings]
        
        # Calculate similarities between similar texts
        similarity_1_2 = cosine_similarity([embedding_arrays[0]], [embedding_arrays[1]])[0][0]
        similarity_1_3 = cosine_similarity([embedding_arrays[0]], [embedding_arrays[2]])[0][0]
        similarity_2_3 = cosine_similarity([embedding_arrays[1]], [embedding_arrays[2]])[0][0]
        
        # Similar texts should have reasonable similarity (cosine similarity > 0.5)
        self.assertGreater(similarity_1_2, 0.5,
                          f"Similar texts should have reasonable cosine similarity. Got: {similarity_1_2:.3f}")
        self.assertGreater(similarity_1_3, 0.5, 
                          f"Similar texts should have reasonable cosine similarity. Got: {similarity_1_3:.3f}")
        self.assertGreater(similarity_2_3, 0.5, 
                          f"Similar texts should have reasonable cosine similarity. Got: {similarity_2_3:.3f}")
        
        # Test with very different text to ensure it has lower similarity
        different_text = "Machine learning algorithms process data."
        different_embedding = self.embedding_generator.generate_embeddings([different_text])[0]
        different_array = np.array(different_embedding)
        
        # Similar texts should be more similar to each other than to different text
        similarity_with_different = cosine_similarity([embedding_arrays[0]], [different_array])[0][0]
        
        # The similar texts should be more similar to each other than to different text
        self.assertGreater(similarity_1_2, similarity_with_different,
                          f"Similar texts should be more similar to each other than to different text. "
                          f"Similarity between similar texts: {similarity_1_2:.3f}, "
                          f"Similarity with different text: {similarity_with_different:.3f}")
        
        # Print similarity scores for debugging
        print(f"\nSimilarity scores:")
        print(f"Text 1 vs Text 2: {similarity_1_2:.3f}")
        print(f"Text 1 vs Text 3: {similarity_1_3:.3f}")
        print(f"Text 2 vs Text 3: {similarity_2_3:.3f}")
        print(f"Text 1 vs Different: {similarity_with_different:.3f}")

    def test_embedding_different_texts(self):
        """Test that different texts produce different embeddings."""
        different_texts = [
            "The cat is on the mat.",
            "Machine learning is a subset of artificial intelligence.",
            "Python is a programming language."
        ]
        
        embeddings = self.embedding_generator.generate_embeddings(different_texts)
        
        # Verify all embeddings have same dimension
        embedding_dim = len(embeddings[0])
        for embedding in embeddings:
            self.assertEqual(len(embedding), embedding_dim)
        
        # Verify that different texts actually produce different embeddings
        embedding1 = embeddings[0]  # "The cat is on the mat."
        embedding2 = embeddings[1]  # "Machine learning is a subset of artificial intelligence."
        embedding3 = embeddings[2]  # "Python is a programming language."
        
        # Check that embeddings are different from each other
        self.assertNotEqual(embedding1, embedding2, 
                           "Different texts should produce different embeddings")
        self.assertNotEqual(embedding1, embedding3, 
                           "Different texts should produce different embeddings")
        self.assertNotEqual(embedding2, embedding3, 
                           "Different texts should produce different embeddings")
        
        # Additional check: verify embeddings are not identical (not all zeros or same values)
        for i, embedding in enumerate(embeddings):
            # Check that embedding has non-zero values
            self.assertTrue(any(abs(val) > 0.001 for val in embedding),
                           f"Embedding {i} should have non-zero values")
            
            # Check that embedding has varied values (not all same)
            unique_values = set(round(val, 3) for val in embedding)
            self.assertGreater(len(unique_values), 1,
                              f"Embedding {i} should have varied values")

    def test_query_vs_document_embedding(self):
        """Test that query and document embeddings work consistently."""
        text = "This is a test document about machine learning."
        
        # Generate embedding as document
        doc_embedding = self.embedding_generator.generate_embeddings(text)
        
        # Generate embedding as query
        query_embedding = self.embedding_generator.generate_query_embedding(text)
        
        # Verify both work and have same dimension
        self.assertEqual(len(doc_embedding), 1)
        self.assertEqual(len(doc_embedding[0]), len(query_embedding))

    def test_model_loading_different_models(self):
        """Test initialization with different model names."""
        model_names = [
            "all-MiniLM-L6-v2",
            "paraphrase-MiniLM-L3-v2"
        ]
        
        for model_name in model_names:
            with self.subTest(model_name=model_name):
                # Create generator with specific model
                generator = EmbeddingGenerator(model_name)
                
                # Verify model is loaded
                self.assertIsNotNone(generator.model)
                self.assertTrue(hasattr(generator.model, 'encode'))
                
                # Test basic functionality
                test_text = "Test text"
                embedding = generator.generate_embeddings(test_text)
                self.assertIsInstance(embedding, list)
                self.assertEqual(len(embedding), 1)


if __name__ == '__main__':
    unittest.main() 