from logging.handlers import RotatingFileHandler

import redis
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from config import Config

db = SQLAlchemy()
redis_store = None  # type: SQLAlchemy


def set_log(config_name):
	# 设置日志的记录等级
	logging.basicConfig(level=config_name.LOG_LEVEL)  # 调试debug级
	# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
	file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
	# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
	formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
	# 为刚创建的日志记录器设置日志记录格式
	file_log_handler.setFormatter(formatter)
	# 为全局的日志工具对象（flask app使用的）添加日志记录器
	logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
	set_log(config_name)

	app = Flask(__name__)

	app.config.from_object(config_name)

	# 数据库
	db.init_app(app)

	# redis
	global redis_store
	redis_store = redis.StrictRedis(host=config_name.REDIS_HOST, port=config_name.REDIS_PORT)

	# 开启CSRF
	CSRFProtect(app)

	# 指定session保存位置
	Session(app)

	# 注册蓝图
	from info.modules.index import index_blue
	app.register_blueprint(index_blue)

	return app
