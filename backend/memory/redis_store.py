import json
import logging
import threading
from typing import Dict, Any, List, Optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    
from backend.config import settings

logger = logging.getLogger(__name__)

class MemoryStoreFallback:
    """A thread-safe local in-memory backup for Redis session state and memory."""
    def __init__(self):
        self._states: Dict[str, str] = {}
        self._user_queries: Dict[str, List[str]] = {}
        self._user_reports: Dict[str, List[str]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            return self._states.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        # Expiry is simulated or ignored locally since it is simple
        with self._lock:
            self._states[key] = value

    def delete(self, key: str) -> None:
        with self._lock:
            self._states.pop(key, None)

    def rpush(self, key: str, value: str) -> None:
        with self._lock:
            if key.startswith("user:") and key.endswith(":past_queries"):
                user_id = key.split(":")[1]
                if user_id not in self._user_queries:
                    self._user_queries[user_id] = []
                if value not in self._user_queries[user_id]:
                    self._user_queries[user_id].append(value)
            elif key.startswith("user:") and key.endswith(":saved_reports"):
                user_id = key.split(":")[1]
                if user_id not in self._user_reports:
                    self._user_reports[user_id] = []
                if value not in self._user_reports[user_id]:
                    self._user_reports[user_id].append(value)

    def lrange(self, key: str, start: int, end: int) -> List[str]:
        with self._lock:
            if key.startswith("user:") and key.endswith(":past_queries"):
                user_id = key.split(":")[1]
                return self._user_queries.get(user_id, [])
            elif key.startswith("user:") and key.endswith(":saved_reports"):
                user_id = key.split(":")[1]
                return self._user_reports.get(user_id, [])
            return []

class RedisStore:
    def __init__(self):
        self.use_fallback = False
        self.redis_client = None
        self.fallback_store = MemoryStoreFallback()
        
        if not REDIS_AVAILABLE:
            self.use_fallback = True
            logger.info("Redis package is not installed. Using in-memory memory fallback.")
            print("[INFO] Redis package is not installed. Using in-memory memory fallback.")
            return

        try:
            # Attempt to connect to Redis
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD or None,
                decode_responses=True,
                socket_connect_timeout=2.0
            )
            # Ping test
            self.redis_client.ping()
            logger.info("Connected to Redis successfully.")
            print("[OK] Connected to Redis successfully.")
        except Exception as e:
            self.use_fallback = True
            logger.warning(f"Failed to connect to Redis: {e}. Using thread-safe in-memory memory fallback.")
            print("[WARN] Failed to connect to Redis. Using in-memory memory fallback instead.")

    def get_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        key = f"research:{session_id}:state"
        try:
            if self.use_fallback:
                data = self.fallback_store.get(key)
            else:
                data = self.redis_client.get(key)
            
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Error reading session state: {e}")
        return None

    def save_state(self, session_id: str, state: Dict[str, Any], expiry: int = 3600) -> None:
        key = f"research:{session_id}:state"
        try:
            serialized = json.dumps(state)
            if self.use_fallback:
                self.fallback_store.set(key, serialized, ex=expiry)
            else:
                self.redis_client.set(key, serialized, ex=expiry)
        except Exception as e:
            logger.error(f"Error saving session state: {e}")

    def clear_state(self, session_id: str) -> None:
        key = f"research:{session_id}:state"
        try:
            if self.use_fallback:
                self.fallback_store.delete(key)
            else:
                self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error clearing session state: {e}")

    def add_user_query(self, user_id: str, query: str) -> None:
        key = f"user:{user_id}:past_queries"
        try:
            if self.use_fallback:
                self.fallback_store.rpush(key, query)
            else:
                # Deduplicate queries in Redis if possible, or just push
                queries = self.redis_client.lrange(key, 0, -1)
                if query not in queries:
                    self.redis_client.rpush(key, query)
        except Exception as e:
            logger.error(f"Error saving user query: {e}")

    def get_user_queries(self, user_id: str) -> List[str]:
        key = f"user:{user_id}:past_queries"
        try:
            if self.use_fallback:
                return self.fallback_store.lrange(key, 0, -1)
            else:
                return self.redis_client.lrange(key, 0, -1)
        except Exception as e:
            logger.error(f"Error fetching user queries: {e}")
            return []

    def add_user_report(self, user_id: str, report_id: str) -> None:
        key = f"user:{user_id}:saved_reports"
        try:
            if self.use_fallback:
                self.fallback_store.rpush(key, report_id)
            else:
                reports = self.redis_client.lrange(key, 0, -1)
                if report_id not in reports:
                    self.redis_client.rpush(key, report_id)
        except Exception as e:
            logger.error(f"Error saving user report ID: {e}")

    def get_user_reports(self, user_id: str) -> List[str]:
        key = f"user:{user_id}:saved_reports"
        try:
            if self.use_fallback:
                return self.fallback_store.lrange(key, 0, -1)
            else:
                return self.redis_client.lrange(key, 0, -1)
        except Exception as e:
            logger.error(f"Error fetching user report IDs: {e}")
            return []

# Singleton instance
redis_store = RedisStore()
