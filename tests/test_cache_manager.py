import json
from types import SimpleNamespace

from core.plugins.config.cache_manager import RedisCacheManager

class FakeRedis:
    def __init__(self):
        self.store = {}
    def ping(self):
        return True
    def get(self, key):
        value = self.store.get(key)
        return value.encode('utf-8') if value is not None else None
    def set(self, key, value):
        self.store[key] = value
    def setex(self, key, ttl, value):
        self.store[key] = value
    def delete(self, key):
        return 1 if self.store.pop(key, None) is not None else 0
    def flushdb(self):
        self.store.clear()
    def close(self):
        pass


def test_redis_cache_manager_json_serialization():
    config = SimpleNamespace(host='localhost', port=6379, db=0, ttl=10)
    manager = RedisCacheManager(config)
    fake = FakeRedis()
    manager.redis_client = fake
    manager.start()

    value = {"foo": "bar", "num": 123}
    manager.set('testkey', value)

    # ensure data stored is JSON
    assert fake.store['testkey'] == json.dumps(value)
    assert manager.get('testkey') == value
