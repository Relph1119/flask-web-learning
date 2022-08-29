#!/usr/bin/env python
# encoding: utf-8
"""
@file: app.py
@time: 2022/8/29 15:35
@project: flask-web-learning
@desc: 初识Flask
"""

import click
from flask import Flask

app = Flask(__name__)


# 最小的Flask程序
@app.route('/')
def index():
    return '<h1>Hello, World!</h1>'


# 为视图绑定多个URL
@app.route('/hi')
@app.route('/hello')
def say_hello():
    return '<h1>Hello, Flask!</h1>'


# 动态URL
@app.route('/greet', defaults={'name': 'Programmer'})
@app.route('/greet/<name>')
def greet(name):
    return '<h1>Hello, %s!</h1>' % name


# 创建自定义命令
@app.cli.command()
def hello():
    """Just say hello."""
    click.echo('Hello, Human!')

