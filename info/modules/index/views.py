from info import constants
from info.models import User, News, Category
from info.utils.response_code import RET
from . import index_blue
from flask import render_template, current_app, session, request, jsonify

# 蓝图注册路由

"""
获取新闻数据
URL:passport/news_list
请求方式GET
参数: cid(分类ID)  page(页码) per_page(每页数量) 三个都可为空
"""


@index_blue.route('/news_list')
def get_news_list():
	# 1.获取参数
	cid = request.args.get('cid', '1')
	page = request.args.get('page', '1')
	per_page = request.args.get('per_page', '10')

	# 2.校验参数
	try:
		cid = int(cid)
		page = int(page)
		per_page = int(per_page)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.PARAMERR, errmsg='参数传入错误')

	# 3.查询新闻数据
	filter = []
	if cid != 1:
		filter.append(News.category_id == cid)
		print('filter判断了')
	try:
		paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(page, per_page, False)
		print('paginate:::', paginate)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR, errmsg='查询失败')

	# 获取查询后的数据
	news_model_list = paginate.items

	# 获取分页总页码
	total_page = paginate.pages

	# 获取当前页码
	current_page = paginate.page

	news_dict_li = []
	for news in news_model_list:
		news_dict_li.append(news.to_basic_dict())

	print('news_dict_li', news_dict_li)

	data = {
		'news_dict_li': news_dict_li,
		'total_page': total_page,
		'current_page': current_page
	}
	return jsonify(errno=RET.OK, errmsg='成功', data=data)


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
		'news_dict_li': news_dict_li,
	}

	return render_template('news/index.html', data=data)


# favicon图片
@index_blue.route('/favicon.ico')
def favicon():
	return current_app.send_static_file('news/favicon.ico')
