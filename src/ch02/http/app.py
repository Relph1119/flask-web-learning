#!/usr/bin/env python
# encoding: utf-8
"""
@file: app.py
@time: 2022/8/29 19:50
@project: flask-web-learning
@desc: Flask与HTTP的练习代码
"""
import os

from markupsafe import escape

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from jinja2.utils import generate_lorem_ipsum
from flask import Flask, make_response, request, redirect, url_for, abort, session, jsonify

app = Flask(__name__)
# 设置密钥
app.secret_key = os.getenv('SECRET_KEY', 'secret string')


# get name value from query string and cookie
@app.route('/')
@app.route('/hello')
def hello():
    name = request.args.get('name')
    # 如果在查询参数中获取不到name，就从Cookie中寻找
    if name is None:
        name = request.cookies.get('name', 'Human')
    response = '<h1>Hello, %s!</h1>' % escape(name)  # escape name to avoid XSS
    # 根据用户认证状态返回不同的内容
    if 'logged_in' in session:
        # 认证通过后
        response += '[Authenticated]'
    else:
        # 认证未通过
        response += '[Not Authenticated]'
    return response


# 重定向到其他视图
@app.route('/hi')
def hi():
    return redirect(url_for('hello'))


# URL变量转换器
@app.route('/goback/<int:year>')
def go_back(year):
    return 'Welcome to %d!' % (2018 - year)


# any转换器
@app.route('/colors/<any(blue, white, red):color>')
def three_colors(color):
    return '<p>Love is patient and kind. Love is not jealous or boastful or proud or rude.</p>'


# 返回418错误响应
@app.route('/brew/<drink>')
def teapot(drink):
    if drink == 'coffee':
        abort(418)
    else:
        return 'A drop of tea.'


# 返回404错误响应
@app.route('/404')
def not_found():
    abort(404)


# 返回不同格式的响应
@app.route('/note', defaults={'content_type': 'text'})
@app.route('/note/<content_type>')
def note(content_type):
    content_type = content_type.lower()
    if content_type == 'text':
        body = '''Note
to: Peter
from: Jane
heading: Reminder
body: Don't forget the party!
'''
        response = make_response(body)
        response.mimetype = 'text/plain'
    elif content_type == 'html':
        body = '''<!DOCTYPE html>
<html>
<head></head>
<body>
  <h1>Note</h1>
  <p>to: Peter</p>
  <p>from: Jane</p>
  <p>heading: Reminder</p>
  <p>body: <strong>Don't forget the party!</strong></p>
</body>
</html>
'''
        response = make_response(body)
        response.mimetype = 'text/html'
    elif content_type == 'xml':
        body = '''<?xml version="1.0" encoding="UTF-8"?>
<note>
  <to>Peter</to>
  <from>Jane</from>
  <heading>Reminder</heading>
  <body>Don't forget the party!</body>
</note>
'''
        response = make_response(body)
        response.mimetype = 'application/xml'
    elif content_type == 'json':
        body = {"note": {
            "to": "Peter",
            "from": "Jane",
            "heading": "Remider",
            "body": "Don't forget the party!"
        }
        }
        # 使用jsonify函数
        response = jsonify(body)
        # equal to:
        # response = make_response(json.dumps(body))
        # response.mimetype = "application/json"
    else:
        abort(400)
    return response


# 设置cookie
@app.route('/set/<name>')
def set_cookie(name):
    # 手动生成一个重定向的响应
    response = make_response(redirect(url_for('hello')))
    # 添加一个cookie
    response.set_cookie('name', name)
    return response


# 模拟用户认证
@app.route('/login')
def login():
    # 写入session，表示用户已认证
    session['logged_in'] = True
    return redirect(url_for('hello'))


# 模拟管理后台
@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        abort(403)
    return 'Welcome to admin page.'


# 登出用户
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        # 删除session中的记录
        session.pop('logged_in')
    return redirect(url_for('hello'))



