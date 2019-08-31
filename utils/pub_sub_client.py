import time
from typing import List
from typing import Generator
from contextlib import contextmanager

from redis import StrictRedis, ConnectionPool


class PubSubClient:

    def __init__(self, host: str = 'localhost', port: int = 6349, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.connection = None
        self.publisher = None
        self.subscriber = None

    @contextmanager
    def connect(self):
        self.connection = ConnectionPool(host=self.host, port=self.port, db=self.db)
        self.publisher = StrictRedis(connection_pool=self.connection)
        self.subscriber = self.publisher.pubsub()
        try:
            yield self
        finally:
            self.publisher.close()
            self.subscriber.close()

    def subscribe(self, channels: List[str]):
        self.subscriber.subscribe(*channels)

    def psubscribe(self, patterns: List[str]):
        self.subscriber.psubscribe(*patterns)

    def unsubscribe(self, channels: List[str]):
        self.subscriber.unsubscribe(*channels)

    def punsubscribe(self, patterns: List[str]):
        self.subscriber.punsubscribe(*patterns)

    def publish(self, channel: str, message):
        self.publisher.publish(channel, message)

    def get_message(self) -> Generator:
        while True:
            message = self.subscriber.get_message()
            if message:
                yield message
            time.sleep(0.001)

