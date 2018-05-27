import redis

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from config import Config

db = SQLAlchemy()
redis_store = None  # type: SQLAlchemy


def create_app(config_name):
	app = Flask(__name__)

	app.config.from_object(Config)

	# 数据库
	db.init_app(app)

	# redis
	global redis_store
	redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

	# 开启CSRF
	CSRFProtect(app)

	# 指定session保存位置
	Session(app)

	return app
