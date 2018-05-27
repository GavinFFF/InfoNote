from flask import request, current_app, jsonify, make_response

from . import passport_blue
from info.utils.captcha.captcha import captcha
from info import redis_store, constants
from info.utils.response_code import RET

# 蓝图实现路由


"""
图像验证码
URL:/passport/image_code?code_id= XXXXXXX
参数: image_code_id
"""


@passport_blue.route('/image_code')
def get_image_code():
	# 1.获取参数
	image_code_id = request.args.get('code_id')

	# 2.生成验证码内容
	name, text, image = captcha.generate_captcha()

	# 3.保存到redis中
	try:
		redis_store.set('image_code_id' + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)

	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR, errmsg='保存到redis失败')

	# 4.返回验证码图像
	response = make_response(image)
	# 修改成图片类型
	response.headers['Content-Type'] = 'image/jpg'

	return response
