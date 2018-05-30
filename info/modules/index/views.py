from info.models import User
from . import index_blue
from flask import render_template, current_app, session


# 蓝图注册路由
# 根路由  首页
@index_blue.route('/')
def index():
	# 登录时，返回session信息（如果有的话）
	# 1.从session中获取用户ID
	user_id = session.get('user_id', None)
	user = None

	# 2.如果user存在就查询数据库
	try:
		user = User.query.get(user_id)
	except Exception as e:
		current_app.logger.error(e)

	# 3.返回user中的数据
	data = {
		'user': user.to_dict() if user else None
	}

	return render_template('news/index.html', data=data)


# favicon图片
@index_blue.route('/favicon.ico')
def favicon():
	return current_app.send_static_file('news/favicon.ico')
