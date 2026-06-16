import os
import json
import redis
from prometheus_client import Counter

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

cache_hits = Counter("cache_hits_total", "Number of cache hits", ["endpoint"])
cache_misses = Counter("cache_misses_total", "Number of cache misses", ["endpoint"])

try:
    _client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    _client.ping()
except Exception:
    _client = None


def get_client():
    return _client


def cache_get(key: str, endpoint: str):
    if _client is None:
        cache_misses.labels(endpoint=endpoint).inc()
        return None
    try:
        value = _client.get(key)
        if value is not None:
            cache_hits.labels(endpoint=endpoint).inc()
            return json.loads(value)
        cache_misses.labels(endpoint=endpoint).inc()
        return None
    except Exception:
        cache_misses.labels(endpoint=endpoint).inc()
        return None


def cache_set(key: str, value, ttl: int = 30):
    if _client is None:
        return
    try:
        _client.setex(key, ttl, json.dumps(value))
    except Exception:
        pass


def cache_delete(key: str):
    if _client is None:
        return
    try:
        _client.delete(key)
    except Exception:
        pass


def cache_delete_pattern(pattern: str):
    if _client is None:
        return
    try:
        keys = _client.keys(pattern)
        if keys:
            _client.delete(*keys)
    except Exception:
        pass
