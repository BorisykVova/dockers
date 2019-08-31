class RedisConfig:
    CHANNEL = 'main'
    HOST = '172.22.0.4'
    PORT = 6379
    DB_FOR_CHANNELS = 0
    DB_FOR_DATA = 1


class FlaskConfig:
    SECRET_KEY = 'Very Secret key'
    HOST = '0.0.0.0'
    PORT = 80


class PostgresConfig:
    HOST = '172.22.0.2'
    PORT = 5432
    USER = 'postgres'
    PASSWORD = 'postgres'
    DATABASE = 'postgres'
