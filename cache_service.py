import time

class SimpleCache:
    def __init__(self, ttl: int = 3600):
        """
        In-memory cache with TTL (Time To Live).
        Default TTL: 1 hour.
        """
        self._cache = {}
        self.ttl = ttl

    def _get_key(self, user_id: int, question: str) -> str:
        # Keying by user_id and normalized question
        return f"{user_id}:{question.strip().lower()}"

    def get(self, user_id: int, question: str):
        key = self._get_key(user_id, question)
        if key in self._cache:
            entry = self._cache[key]
            # Check if expired
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['data']
            else:
                del self._cache[key]
        return None

    def set(self, user_id: int, question: str, data: dict):
        key = self._get_key(user_id, question)
        self._cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

# Singleton instance
query_cache = SimpleCache()
