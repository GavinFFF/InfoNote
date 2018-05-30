from info import constants
from info.models import User, News
from . import index_blue
from flask import render_template, current_app, session


# 蓝图注册路由
# 根路由  首页
@index_blue.route('/')
def index():
	# 登录数据
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

	# 新闻数据
	# 数据库查询新闻数据
	news_list = []
	try:
		# 通过点击量，做降序，获取前10条
		news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
	except Exception as e:
		current_app.logger.error(e)

	news_dict_li = []
	for news in news_list:
		news_dict_li.append(news.to_basic_dict())

	data = {
		'user': user.to_dict() if user else None,
		'news_dict_li': news_dict_li
	}

	return render_template('news/index.html', data=data)


# favicon图片
@index_blue.route('/favicon.ico')
def favicon():
	return current_app.send_static_file('news/favicon.ico')
