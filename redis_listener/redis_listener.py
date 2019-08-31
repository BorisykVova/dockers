import logging

from redis import Redis, RedisError

from config import RedisConfig
from utils.pub_sub_client import PubSubClient


client = PubSubClient(host=RedisConfig.HOST,
                      port=RedisConfig.PORT,
                      db=RedisConfig.DB_FOR_CHANNELS)
pub_sub: PubSubClient
try:
    with client.connect() as pub_sub:
        pub_sub.subscribe([RedisConfig.CHANNEL])
        for message in pub_sub.get_message():
            if message:
                try:
                    data = (message['data']).decode('utf-8')
                    key, value = data.split('=')

                    r = Redis(host=RedisConfig.HOST,
                              port=RedisConfig.PORT,
                              db=RedisConfig.DB_FOR_DATA)
                    r.set(key, value)
                except (ValueError, AttributeError) as err:
                    logging.warning(f'Wrong message: {err}')
except RedisError as err:
    logging.error(f'Redis Connection error: {err}')
