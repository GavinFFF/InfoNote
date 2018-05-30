import random
import re
from flask import request, current_app, jsonify, make_response, session

from . import passport_blue
from info.utils.captcha.captcha import captcha
from info import redis_store, constants, db
from info.utils.response_code import RET
from info.libs.yuntongxun.sms import CCP
from info.models import User

# 蓝图实现路由
"""
登录接口
URL:passport/logout
"""


@passport_blue.route('/logout', methods=['POST'])
def logout():
	# 清除session中登录后保存的对应信息
	session.pop('user_id', None)
	session.pop('nick_name', None)
	session.pop('mobile', None)

	return jsonify(errno=RET.OK, errmsg='退出成功')


"""
登录接口
URL:/passport/login
参数:mobile(手机号),password(密码)
"""


@passport_blue.route('/login', methods=['POST'])
def login():
	# 1.获取参数
	params_dict = request.json
	mobile = params_dict['mobile']
	password = params_dict['password']

	# 2.校验参数
	# 2.1参数完整性
	if not all([mobile, password]):
		return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

	# 2.2检查手机号是否正确
	if not re.match('^1[3456789][0-9]{9}$', mobile):
		return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

	# 3.校验账号、密码
	# 3.1数据库查询mobile
	try:
		user = User.query.filter_by(mobile=mobile).first()
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR, errmsg='数据库查询mobile失败')

	# 3.2判断user是否存在
	if not user:
		return jsonify(errno=RET.NODATA, errmsg='用户不存在')

	# 3.3对比密码
	if not user.check_password(password):
		return jsonify(errno=RET.PWDERR, errmsg='用户名或密码错误')

	# 4.记录登录状态
	session['user_id'] = user.id
	session['nick_name'] = mobile
	session['mobile'] = mobile

	# 5.返回登录成功信息
	return jsonify(errno=RET.OK, errmsg='登录成功')


"""
注册接口
URL:/passport/register
参数:mobile(手机号码),sms_code(短信验证码),password(密码)
"""


@passport_blue.route('/register', methods=['POST'])
def register():
	# 1.获取参数
	params_dict = request.json
	mobile = params_dict['mobile']
	sms_code = params_dict['sms_code']
	password = params_dict['password']

	# 2.校验参数
	# 2.1参数完整性

	if not all([mobile, sms_code, password]):
		return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

	# 2.2检查手机号是否正确
	if not re.match('^1[3456789][0-9]{9}$', mobile):
		return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

	# 3.校验短信验证码
	# 3.1redis查询短信验证码
	try:
		real_sms_code = redis_store.get('SMS_' + mobile)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR, errmsg='查询短信验证码失败')

	# 3.2判断短信验证码是否失效
	if not real_sms_code:
		return jsonify(errno=RET.NODATA, errmsg='短信验证码已失效')

	# 3.3 对比短信验证码
	if real_sms_code.upper() != sms_code.upper():
		return jsonify(errno=RET.DATAERR, errmsg='短信验证码输入错误')

	# 3.4 短信验证码校验成功，删除
	try:
		redis_store.delete('SMS_' + mobile)
	except Exception as e:
		current_app.logger.error(e)

	# 4.判断账号是否注册过
	# 4.1数据库中查询手机号码
	try:
		user = User.query.filter_by(mobile=mobile).first()
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR, errmsg='数据库查询mobile失败')

	# 4.2判断user是否存在
	if user:
		return jsonify(errno=RET.DATAEXIST, errmsg='用户已注册')

	# 5.保存用户信息到数据库
	user = User()
	user.mobile = mobile
	user.nick_name = mobile

	# user.password_hash = password
	user.password = password

	try:
		db.session.add(user)
		db.session.commit()
	except Exception as e:
		db.session.rollback()
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR, errmsg='数据库添加user失败')

	# 6.保持登录状态
	session['user_id'] = user.id
	session['nick_name'] = user.nick_name
	session['mobile'] = mobile

	# 7.返回成功信息
	return jsonify(errno=RET.OK, errmsg='注册成功')


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
		return jsonify(errno=RET.DATAERR, errmsg='验证码错误')

	# 3.3生成短信验证码----第三方只负责发送短信，验证码需要自己设定
	sms_code_str = '%06d' % random.randint(0, 999999)
	print(sms_code_str)
	current_app.logger.debug('sms_code:%s' % sms_code_str)

	# 3.4调用第三方发送短信
	# result = CCP().send_template_sms(mobile, [sms_code_str, 5], 1)
	# if result != 0:
	# 	# 表示发送失败
	# 	return jsonify(errno=RET.THIRDERR, errmsg='短信验证码发送失败')

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
