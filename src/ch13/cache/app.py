# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import time

from flask import Flask, url_for, redirect, request, flash, render_template
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config['SECRET_KEY'] = 'dev key'

# 使用本地的Python字典
app.config['CACHE_TYPE'] = 'simple'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# 初始化缓存对象
cache = Cache(app)
toolbar = DebugToolbarExtension(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/foo')
def foo():
    time.sleep(1)
    return render_template('foo.html')


# 设置缓存，缓存时间为10分钟
@app.route('/bar')
@cache.cached(timeout=10 * 60)
def bar():
    time.sleep(1)
    return render_template('bar.html')


@app.route('/baz')
@cache.cached(timeout=60 * 60)
def baz():
    time.sleep(1)
    return render_template('baz.html')


# 使用缓存，将排序后的查询参数散列值作为键
@app.route('/qux')
@cache.cached(query_string=True)
def qux():
    time.sleep(1)
    page = request.args.get('page', 1)
    return render_template('qux.html', page=page)


@app.route('/update/bar')
def update_bar():
    # 在对内容进行更改时，清除缓存
    cache.delete('view/%s' % url_for('bar'))
    flash('Cached data for bar have been deleted.')
    return redirect(url_for('index'))


@app.route('/update/baz')
def update_baz():
    cache.delete('view/%s' % url_for('baz'))
    flash('Cached data for baz have been deleted.')
    return redirect(url_for('index'))


@app.route('/update/all')
def update_all():
    # 清除程序中的所有缓存
    cache.clear()
    flash('All cached data deleted.')
    return redirect(url_for('index'))


# cache other function
@cache.cached(key_prefix='add')
def add(a, b):
    time.sleep(2)
    return a + b


# cache memorize (with argument)
@cache.memoize()
def add_pro(a, b):
    time.sleep(2)
    return a + b


def del_add_cache():
    cache.delete('add')


# delete memorized cache
def del_pro_cache():
    # 删除为add_pro()函数设置的缓存
    cache.delete_memoized(add_pro)
