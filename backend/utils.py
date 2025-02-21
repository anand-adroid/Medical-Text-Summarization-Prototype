import backend.config
import hashlib
import json
from backend.config import REDIS_ENABLED

in_memory_cache = {}

def count_tokens(text):
    return len(text.split()) // 1.3

def get_cache_key(notes, role):
    return f"summary:{hashlib.sha256(f'{notes}-{role}'.encode()).hexdigest()}"

def get_cached_summary(notes, role):
    """Retrieve summary from simple in-memory cache."""
    return in_memory_cache.get(get_cache_key(notes, role), None)

def set_cached_summary(notes, role, summary_data):
    """Store summary in simple in-memory cache."""
    in_memory_cache[get_cache_key(notes, role)] = summary_data