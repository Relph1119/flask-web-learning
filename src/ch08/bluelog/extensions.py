# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask_bootstrap import Bootstrap4
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate

# 扩展类实例化
bootstrap = Bootstrap4()
# 创建数据库实例
db = SQLAlchemy()
# 创建用户会话管理实例
login_manager = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
# 创建邮件实例
mail = Mail()
moment = Moment()
toolbar = DebugToolbarExtension()
migrate = Migrate()


# 获取当前用户，当调用current_user时，会调用该函数并返回对应的用户对象
# 如果当前用户已经登录，返回Admin类实例
# 如果用户未登录，默认返回内置的AnonymousUserMixin类对象，其中is_authenticated=False，is_active=False，is_anonymous=True
@login_manager.user_loader
def load_user(user_id):
    from bluelog.models import Admin
    user = Admin.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录！'
login_manager.login_message_category = 'warning'
