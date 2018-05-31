from flask import render_template, current_app, jsonify

from info import constants
from info.models import News
from info.utils.response_code import RET
from . import news_blue


@news_blue.route('/<int:news_id>')
def get_news(news_id):
	try:
		news = News.query.get(news_id)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR, errmsg='数据库查询失败')

	# 点击排行数据

	news_list = []
	try:
		news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR, errmsg='数据库查询失败')

	news_dict_li = []
	for news in news_list:
		news_dict_li.append(news.to_basic_dict())

	data = {
		'news': news,
		'news_dict_li': news_dict_li
	}

	return render_template('news/detail.html', data=data)
