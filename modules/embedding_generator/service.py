"""
Embedding Generator Service.

This module generates text embeddings using the BAAI/bge-m3 model.
Supports batch processing and caching for efficiency.
"""

import time
import json
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import torch
from shared.config_loader import config
from shared.logger import get_module_logger

# Initialize logger
logger = get_module_logger("embedding_generator", config.get_log_level())


class EmbeddingGeneratorService:
    """
    Service for generating text embeddings.
    
    Uses BAAI/bge-m3 model for multilingual embeddings.
    Supports Serbian Cyrillic text.
    """
    
    def __init__(self):
        """Initialize the embedding generator service."""
        self.model_name = config.get_embedding_model()
        self.embedding_dim = config.get_embedding_dimensions()
        self.device = self._get_device()
        self.batch_size = config.get_embedding_batch_size()
        
        logger.info(f"Initializing embedding model: {self.model_name}")
        logger.info(f"Device: {self.device}")
        
        # Load model
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            raise
    
    def _get_device(self) -> str:
        """
        Determine the best device to use (CUDA or CPU).
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        configured_device = config.get_embedding_device()
        
        if configured_device == "cuda" and torch.cuda.is_available():
            logger.info("CUDA is available, using GPU")
            return "cuda"
        else:
            if configured_device == "cuda":
                logger.warning("CUDA requested but not available, falling back to CPU")
            else:
                logger.info("Using CPU for embeddings")
            return "cpu"
    
    def generate_embedding(self, text: str) -> Dict[str, Any]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
        
        Returns:
            Dictionary containing:
            - embeddings: List of floats (embedding vector)
            - model_name: Name of the model used
            - embedding_dimension: Dimension of the embedding
            - text_length: Length of input text
            - processing_time_ms: Processing time in milliseconds
        """
        start_time = time.time()
        
        try:
            # Generate embedding
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            
            # Convert to list for JSON serialization
            embedding_list = embedding.tolist()
            
            processing_time = (time.time() - start_time) * 1000
            
            result = {
                "embeddings": embedding_list,
                "model_name": self.model_name,
                "embedding_dimension": len(embedding_list),
                "text_length": len(text),
                "processing_time_ms": round(processing_time, 2)
            }
            
            logger.debug(f"Generated embedding for text of length {len(text)} in {processing_time:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}", exc_info=True)
            raise
    
    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts
            batch_size: Optional batch size (uses config default if not provided)
        
        Returns:
            Dictionary containing:
            - embeddings: List of embedding vectors
            - model_name: Name of the model used
            - embedding_dimension: Dimension of embeddings
            - text_count: Number of texts processed
            - total_processing_time_ms: Total processing time
            - avg_time_per_text_ms: Average time per text
        """
        start_time = time.time()
        
        if batch_size is None:
            batch_size = self.batch_size
        
        try:
            # Generate embeddings in batches
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=len(texts) > 10
            )
            
            # Convert to list of lists
            embeddings_list = [emb.tolist() for emb in embeddings]
            
            processing_time = (time.time() - start_time) * 1000
            avg_time = processing_time / len(texts) if texts else 0
            
            result = {
                "embeddings": embeddings_list,
                "model_name": self.model_name,
                "embedding_dimension": len(embeddings_list[0]) if embeddings_list else 0,
                "text_count": len(texts),
                "total_processing_time_ms": round(processing_time, 2),
                "avg_time_per_text_ms": round(avg_time, 2)
            }
            
            logger.info(
                f"Generated {len(texts)} embeddings in {processing_time:.2f}ms "
                f"(avg: {avg_time:.2f}ms per text)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}", exc_info=True)
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "device": self.device,
            "batch_size": self.batch_size,
            "max_seq_length": self.model.max_seq_length if hasattr(self.model, 'max_seq_length') else None
        }


# Create singleton instance
service = EmbeddingGeneratorService()


# Example usage
if __name__ == "__main__":
    print("Testing Embedding Generator Service...")
    
    # Test single embedding
    test_text = "Zakon o radu regulise prava i obaveze zaposlenih."
    print(f"\nTest text: {test_text}")
    
    result = service.generate_embedding(test_text)
    print(f"Embedding dimension: {result['embedding_dimension']}")
    print(f"Processing time: {result['processing_time_ms']}ms")
    print(f"First 5 values: {result['embeddings'][:5]}")
    
    # Test batch embeddings
    test_texts = [
        "Clan 1: Opste odredbe",
        "Clan 2: Definicije pojmova",
        "Clan 3: Primena zakona"
    ]
    print(f"\nBatch test with {len(test_texts)} texts...")
    
    batch_result = service.generate_embeddings_batch(test_texts)
    print(f"Total time: {batch_result['total_processing_time_ms']}ms")
    print(f"Average per text: {batch_result['avg_time_per_text_ms']}ms")
    
    # Model info
    print("\nModel info:")
    info = service.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

# Made with Bob
