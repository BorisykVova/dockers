from contextlib import closing
import logging

import psycopg2
from psycopg2 import errors

from config import RedisConfig, PostgresConfig
from utils.pub_sub_client import PubSubClient


client = PubSubClient(host=RedisConfig.HOST,
                      port=RedisConfig.PORT,
                      db=RedisConfig.DB_FOR_CHANNELS)
pub_sub: PubSubClient
with client.connect() as pub_sub:

    pub_sub.subscribe([RedisConfig.CHANNEL])
    for message in pub_sub.get_message():
        if message:
            try:
                data = (message['data']).decode('utf-8')
                key, value = data.split('=')

                try:
                    with closing(psycopg2.connect(user=PostgresConfig.USER,
                                                  password=PostgresConfig.PASSWORD,
                                                  host=PostgresConfig.HOST,
                                                  port=PostgresConfig.PORT,
                                                  database=PostgresConfig.DATABASE)) as connection:
                        try:
                            with connection.cursor() as cursor:
                                cursor.execute('INSERT INTO postgres.public.key_value VALUES (%s, %s)', (key, value))
                        except errors.lookup('42P01') as err:
                            logging.error(f'Wrong SQL  request: {err}')
                        except errors.lookup('42601') as err:
                            logging.error(f'Wrong SQL  request: {err}')
                        except errors.lookup('42703') as err:
                            logging.error(err)
                        connection.commit()
                except psycopg2.errors as err:
                    logging.error(f'Database(host =  username = ) is unavailable, {err})')

            except (ValueError, AttributeError) as err:
                logging.warning(f'Wrong Message: {err}')
