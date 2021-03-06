import redis
import logging


class Config(object):
	"""工程配置信息"""

	# 秘钥，随便写一个
	SECRET_KEY = 'asdkfjalksdfnknzxcv.akls;df'

	# 数据库配置信息
	SQLALCHEMY_DATABASE_URI = 'mysql://root:guanfei123@127.0.0.1/information'
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# redis配置信息
	REDIS_HOST = '127.0.0.1'
	REDIS_PORT = '6379'

	# session配置信息
	SESSION_TYPE = 'redis'
	SESSION_USE_SIGNER = True
	SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
	PERMANENT_SESSION_LIFETIME = 86400


class DevelopmentConfig(Config):
	"""开发模式下配置"""
	DEBUG = True
	LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
	"""生产模式下配置"""
	DEBUG = False
	LOG_LEVEL = logging.WARNING
