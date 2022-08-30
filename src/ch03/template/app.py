#!/usr/bin/env python
# encoding: utf-8
"""
@file: app.py
@time: 2022/8/30 10:06
@project: flask-web-learning
@desc:
"""
import os
from flask import Flask, render_template, flash, redirect, url_for, Markup

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')
# 删除Jinja2语句后的第一个空行
app.jinja_env.trim_blocks = True
# 删除Jinja2语句所在行之前的空格和制表符(tabs)
app.jinja_env.lstrip_blocks = True

# 用户信息
user = {
    'username': 'Grey Li',
    'bio': 'A boy who loves movies and music.',
}

# 用户收藏的电影列表
movies = [
    {'name': 'My Neighbor Totoro', 'year': '1988'},
    {'name': 'Three Colours trilogy', 'year': '1993'},
    {'name': 'Forrest Gump', 'year': '1994'},
    {'name': 'Perfect Blue', 'year': '1997'},
    {'name': 'The Matrix', 'year': '1999'},
    {'name': 'Memento', 'year': '2000'},
    {'name': 'The Bucket list', 'year': '2007'},
    {'name': 'Black Swan', 'year': '2010'},
    {'name': 'Gone Girl', 'year': '2014'},
    {'name': 'CoCo', 'year': '2017'},
]


# 渲染watchlist的HTML模板
@app.route('/watchlist')
def watchlist():
    return render_template('watchlist.html', user=user, movies=movies)


# 渲染index的HTML模板
@app.route('/')
def index():
    return render_template('index.html')


# 注册模板上下文处理函数
@app.context_processor
def inject_info():
    foo = 'I am foo.'
    return dict(foo=foo)  # equal to: return {'foo': foo}


# 注册模板全局函数
@app.template_global()
def bar():
    return 'I am bar.'


# 注册模板过滤器
@app.template_filter()
def musical(s):
    # 使用Markup标记为安全字符
    return s + Markup(' &#9835;')


# 注册自定义测试器
@app.template_test()
def baz(n):
    if n == 'baz':
        return True
    return False


@app.route('/watchlist2')
def watchlist_with_static():
    return render_template('watchlist_with_static.html', user=user, movies=movies)


# 消息闪现
@app.route('/flash')
def just_flash():
    flash('I am flash, who is looking for me?')
    return redirect(url_for('index'))


# 404错误处理器
@app.errorhandler(404)
def page_not_found(e):
    # 重定向到404.html页面
    return render_template('errors/404.html'), 404


# 500错误处理器
@app.errorhandler(500)
def internal_server_error(e):
    # 重定向到500.html页面
    return render_template('errors/500.html'), 500
