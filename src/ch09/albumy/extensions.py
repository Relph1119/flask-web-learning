# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask_avatars import Avatars
from flask_bootstrap import Bootstrap4
from flask_dropzone import Dropzone
from flask_login import LoginManager, AnonymousUserMixin
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_whooshee import Whooshee
from flask_wtf import CSRFProtect

bootstrap = Bootstrap4()
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
# 使用Flask-Dropzone扩展，支持文件上传
dropzone = Dropzone()
moment = Moment()
# 使用Flask-Whooshee扩展，实现全文搜索
whooshee = Whooshee()
# 使用Flask-Avatars扩展，支持处理用户头像
avatars = Avatars()
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id):
    from albumy.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录！'
login_manager.login_message_category = 'warning'

# 配置重新认证的端点
login_manager.refresh_view = 'auth.re_authenticate'
login_manager.needs_refresh_message = '为了保护你的账户安全，请重新登录。'
# 配置重定向到重新认证页面时闪现的消息的分类
login_manager.needs_refresh_message_category = 'warning'


# 匿名用户类
class Guest(AnonymousUserMixin):

    def can(self, permission_name):
        return False

    @property
    def is_admin(self):
        return False


login_manager.anonymous_user = Guest
