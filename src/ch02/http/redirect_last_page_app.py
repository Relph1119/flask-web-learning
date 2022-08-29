#!/usr/bin/env python
# encoding: utf-8
"""
@file: practice_app.py
@time: 2022/8/29 21:21
@project: flask-web-learning
@desc: HTTP进阶实践：
（1）希望通过操作do-something视图，重定向回上一个页面
（2）如果在Foo页面上单击链接，希望重定向回Foo页面
（3）如果在Bar页面上单击链接，希望返回到Bar页面

"""
from urllib.parse import urlparse, urljoin

from flask import Flask, url_for, request, redirect

app = Flask(__name__)


@app.route('/foo')
def foo():
    # 查询参数一般命名为next，使用当前页面的完整路径
    return '<h1>Foo page</h1><a href="%s">Do something and redirect</a>' \
           % url_for('do_something', next=request.full_path)


@app.route('/bar')
def bar():
    return '<h1>Bar page</h1><a href="%s">Do something and redirect</a>' \
           % url_for('do_something', next=request.full_path)


@app.route('/do-something')
def do_something():
    # do something here
    return redirect_back()


# 验证next变量值是否属于程序内部URL
def is_safe_url(target):
    # 获取程序内的主机地址
    ref_url = urlparse(request.host_url)
    # 目标URL地址
    test_url = urlparse(urljoin(request.host_url, target))
    # 比较两个地址的内部URL地址
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='hello', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        # 对URL进行安全验证
        if is_safe_url(target):
            # 进行跳转
            return redirect(target)
    # next和referer都为空
    return redirect(url_for(default, **kwargs))


if __name__ == '__main__':
    app.run()
