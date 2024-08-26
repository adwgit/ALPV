# app/utils/redis_cache.py
import redis
import os

class RedisCache:
    def __init__(self):
        self.redis = redis.StrictRedis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0
        )

    def get(self, key):
        return self.redis.get(key)

    def set(self, key, value, ex=None):
        self.redis.set(key, value, ex=ex)
