# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import Flask
from flask_bootstrap import Bootstrap4
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

# 使用硬编码的形式写出包名称作为程序名称
app = Flask('sayhello')
app.config.from_pyfile('settings.py')
# 删除Jinja2语句后的第一个空行
app.jinja_env.trim_blocks = True
# 删除Jinja2语句所在行之前的空格和制表符(tabs)
app.jinja_env.lstrip_blocks = True
# 创建数据库实例
db = SQLAlchemy(app)
# 使用Bootstrap4简化页面
bootstrap = Bootstrap4(app)
# 使用Flask-Moment本地化日期和时间
moment = Moment(app)

# 将程序实例app注册的视图函数、错误处理函数、自定义命令函数和程序实例关联起来
from sayhello import views, errors, commands
