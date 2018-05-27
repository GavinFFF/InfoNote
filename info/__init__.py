import redis

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from config import Config

app = Flask(__name__)

app.config.from_object(Config)

# 数据库
db = SQLAlchemy(app)

# redis
redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 开启CSRF
CSRFProtect(app)

# 指定session保存位置
Session(app)
