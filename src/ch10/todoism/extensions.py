# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import request, current_app
from flask_babel import Babel, lazy_gettext as _l
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
# 使用Flask-Bable处理国际化
babel = Babel()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = _l('Please login to access this page.')


@login_manager.user_loader
def load_user(user_id):
    from todoism.models import User
    return User.query.get(int(user_id))


# 设置区域选择函数
@babel.localeselector
def get_locale():
    if current_user.is_authenticated and current_user.locale is not None:
        return current_user.locale
    # 从cookies中获取区域代码
    locale = request.cookies.get('locale')
    if locale is not None:
        return locale
    # 返回语言列表
    return request.accept_languages.best_match(current_app.config['TODOISM_LOCALES'])
