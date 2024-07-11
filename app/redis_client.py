import redis
from rq import Queue
from urllib.parse import urlparse
from functools import lru_cache
from .config import Config

@lru_cache(maxsize=None)
def create_redis_client():
    url = urlparse(Config.REDIS_URL)
    return redis.Redis(
        host=url.hostname,
        port=url.port,
        username=url.username,
        password=url.password,
        ssl=True,
        ssl_cert_reqs=None,
        decode_responses=True
    )

def get_redis():
    return create_redis_client()

def get_redis_queue():
    return Queue(connection=get_redis())