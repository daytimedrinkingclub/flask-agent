import redis
from rq import Queue
from .config import Config

redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)

def get_redis():
    return redis_client

def get_redis_queue():
    return Queue(connection=get_redis())