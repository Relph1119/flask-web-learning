#!/usr/bin/env python
# encoding: utf-8
"""
@file: ajax_async_request.py
@time: 2022/8/29 21:42
@project: flask-web-learning
@desc: 使用AJAX技术发送异步请求
"""
from flask import Flask
from jinja2.utils import generate_lorem_ipsum

app = Flask(__name__)


# 加载更多
@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)


# 显示虚拟文章
@app.route('/post')
def show_post():
    # 生成两段随机文本
    post_body = generate_lorem_ipsum(n=2)
    return '''
<h1>A very long post</h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {
    $('#load').click(function() {
        $.ajax({
            url: '/more',
            type: 'get',
            success: function(data){
                $('.body').append(data);
            }
        })
    })
})
</script>''' % post_body


if __name__ == '__main__':
    app.run()
