from contextlib import closing

from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from redis import Redis, RedisError
from psycopg2 import errors
import psycopg2

from config import FlaskConfig, RedisConfig, PostgresConfig
from utils.pub_sub_client import PubSubClient
from forms import InputForm


app = Flask(__name__)
app.config['SECRET_KEY'] = FlaskConfig.SECRET_KEY
Bootstrap(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/redis', methods=['GET', 'POST'])
def redis():
    try:
        r = Redis(host=RedisConfig.HOST,
                  port=RedisConfig.PORT,
                  db=RedisConfig.DB_FOR_DATA)
        keys = r.keys()
        data = {key.decode('utf-8'): (r.get(key).decode('utf-8')) for key in keys}
        return render_template('data.html', data=data)
    except RedisError as err:
        return render_template('errors.html', err=err)


@app.route('/db', methods=['GET', 'POST'])
def db():
    try:
        with closing(psycopg2.connect(user=PostgresConfig.USER,
                                      password=PostgresConfig.PASSWORD,
                                      host=PostgresConfig.HOST,
                                      port=PostgresConfig.PORT,
                                      database=PostgresConfig.DATABASE)) as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute('Select * From postgres.public.key_value')
                    data = {key: value for key, value in cursor}

            except errors.lookup('42P01') as err:
                return render_template('errors.html', err=err)
            except errors.lookup('42601') as err:
                return render_template('errors.html', err=err)
            except errors.lookup('42703') as err:
                return render_template('errors.html', err=err)
    except errors as err:
        return render_template('errors.html', err=err)

    return render_template('data.html', data=data)


@app.route('/publish', methods=['GET', 'POST'])
def publish():
    form = InputForm()
    if form.validate_on_submit():

        key = form.key.data
        value = form.value.data

        client = PubSubClient(host=RedisConfig.HOST,
                              port=RedisConfig.PORT,
                              db=RedisConfig.DB_FOR_CHANNELS)
        pub_sub: PubSubClient

        try:
            with client.connect() as pub_sub:
                pub_sub.publish(RedisConfig.CHANNEL, f'{key}={value}')
        except RedisError as err:
            return render_template('errors.html', err=err)

        flash('Successful!')
        return redirect(url_for('publish'))
    return render_template('publish.html', form=form)


if __name__ == '__main__':
    app.run(host=FlaskConfig.HOST, port=FlaskConfig.PORT)
