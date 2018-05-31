from flask import render_template

from . import news_blue


@news_blue.route('/<int:news_id>')
def get_news(news_id):
	return render_template('news/detail.html')
