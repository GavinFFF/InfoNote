import redis

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)


class Config(object):
	"""工程配置信息"""

	DEBUG = True
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


app.config.from_object(Config)

# 数据库
db = SQLAlchemy(app)

# redis
redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 开启CSRF
CSRFProtect(app)

# 指定session保存位置
Session(app)

# manager启动程序
manager = Manager(app)

# 数据库迁移
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
	return 'aaaaa'


if __name__ == '__main__':
	manager.run()
