import time
import numpy as np
from fastembed import TextEmbedding

# Initialize the embedding model globally so it's loaded only once
# BAAI/bge-small-en-v1.5 is extremely fast, lightweight, and very accurate.
try:
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
except Exception as e:
    print(f"Failed to load embedding model: {e}")
    embedding_model = None

def get_embedding(text: str) -> np.ndarray:
    if not embedding_model:
        return None
    # fastembed returns an iterator of arrays
    embeddings = list(embedding_model.embed([text]))
    return embeddings[0]

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

class SemanticCache:
    def __init__(self, ttl: int = 3600, threshold: float = 0.92):
        """
        In-memory Semantic cache with TTL.
        Uses vector embeddings to match similar questions.
        """
        # Store lists of cached entries per user_id
        # Format: { user_id: [ {'question': str, 'vector': np.ndarray, 'data': dict, 'timestamp': float} ] }
        self._cache = {}
        self.ttl = ttl
        self.threshold = threshold

    def get(self, user_id: int, question: str):
        if user_id not in self._cache:
            return None, False

        # Generate the embedding for the incoming question
        question_vector = get_embedding(question)
        if question_vector is None:
            return None, False

        current_time = time.time()
        best_match = None
        highest_similarity = -1.0

        # Filter out expired entries
        valid_entries = []
        for entry in self._cache[user_id]:
            if current_time - entry['timestamp'] < self.ttl:
                valid_entries.append(entry)
                
                # Calculate similarity
                sim = cosine_similarity(question_vector, entry['vector'])
                if sim > highest_similarity:
                    highest_similarity = sim
                    best_match = entry
            
        # Update cache to remove expired ones
        self._cache[user_id] = valid_entries

        # Check if the best match passes our semantic threshold
        if highest_similarity >= self.threshold:
            print(f"Semantic Cache Hit! Similarity: {highest_similarity:.4f}")
            return best_match['data'], True

        return None, False

    def set(self, user_id: int, question: str, data: dict):
        question_vector = get_embedding(question)
        if question_vector is None:
            return

        if user_id not in self._cache:
            self._cache[user_id] = []

        self._cache[user_id].append({
            'question': question,
            'vector': question_vector,
            'data': data,
            'timestamp': time.time()
        })

# Singleton instance
query_cache = SemanticCache()
