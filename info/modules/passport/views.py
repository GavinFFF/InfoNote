import random
import re
from flask import request, current_app, jsonify, make_response

from . import passport_blue
from info.utils.captcha.captcha import captcha
from info import redis_store, constants
from info.utils.response_code import RET
from info.libs.yuntongxun.sms import CCP

# 蓝图实现路由

"""
短信验证码
URL:/passport/sms_code?
参数：mobile, image_code, image_code_id
"""


@passport_blue.route('/sms_code', methods=['POST'])
def get_sms_code():
	# 1.获取参数
	params_dict = request.json
	mobile = params_dict.get('mobile')  # 手机号
	image_code = params_dict.get('image_code')  # 验证码图片内容
	image_code_id = params_dict.get('image_code_id')  # 验证码图片编号

	# 2.校验参数是否齐全
	if not all([mobile, image_code, image_code_id]):
		return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

	# 2.1检查手机号是否正确
	if not re.match('^1[3456789][0-9]{9}$', mobile):
		return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

	# 3.逻辑处理
	# 3.1从redis中查询 图像验证码内容
	try:
		real_image_code = redis_store.get('image_code_id_' + image_code_id)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

	# 3.2判断数据是否过期
	if not real_image_code:
		return jsonify(errno=RET.NODATA, errmsg='验证码已经过期')

	# 3.2将数据转化成全大写或者全小写 进行对比
	if real_image_code.upper() != image_code.upper():
		print("*" * 50)
		print(real_image_code, image_code)
		return jsonify(errno=RET.DATAERR, errmsg='验证码错误')

	# 3.3生成短信验证码----第三方只负责发送短信，验证码需要自己设定
	sms_code_str = '%06d' % random.randint(0, 999999)
	current_app.logger.debug('sms_code:%s' % sms_code_str)

	# 3.4调用第三方发送短信
	result = CCP().send_template_sms(mobile, [sms_code_str, 5], 1)
	if result != 0:
		# 表示发送失败
		return jsonify(errno=RET.THIRDERR, errmsg='短信验证码发送失败')

	# 保存到redis中
	try:
		redis_store.set('SMS_' + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR, errmsg='短信验证码数据保存失败')

	# 4.返回数据
	return jsonify(errno=RET.OK, errmsg='短信验证码发送成功')


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
		redis_store.set('image_code_id_' + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)

	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR, errmsg='保存到redis失败')

	# 4.返回验证码图像
	response = make_response(image)
	# 修改成图片类型
	response.headers['Content-Type'] = 'image/jpg'

	return response
