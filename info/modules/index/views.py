from . import index_blue

# 蓝图注册路由
@index_blue.route('/')
def index():
	return 'index'
