# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import os
import sys

from sayhello import app

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

dev_db = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db')
# 设置CSRF令牌的密钥
SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
# 关闭警告信息
SQLALCHEMY_TRACK_MODIFICATIONS = False
# 设置数据库的URI
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', dev_db)
