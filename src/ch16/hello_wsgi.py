#!/usr/bin/env python
# encoding: utf-8
"""
@file: hello_wsgi.py
@time: 2022/9/3 16:07
@project: flask-web-learning
@desc: WSGI程序
"""
from wsgiref.simple_server import make_server


class AppClass:
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

    def __iter__(self):
        status = "200 OK"
        response_headers = [('Content-type', 'text/html')]
        self.start_response(status, response_headers)
        return [b'<h1>Hello, Web</h1>']


def hello(environ, start_response):
    """
    使用Python函数实现WSGI程序
    :param environ: 包含了请求的所有信息的字典
    :param start_response: 需要在可调用对象中调用的函数，用来发起响应，参数是状态码、响应头部等
    :return: 可迭代对象
    """
    status = "200 OK"
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)
    name = environ['PATH_INFO'][1:] or 'web'
    return [b'<h1>Hello, %s</h1>' % name.encode()]


class MyMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            headers.append(('A-CUSTOM-HEADERS', 'Nothing'))
            return start_response(status, headers)

        return self.app(environ, custom_start_response)


if __name__ == '__main__':
    wrapped_app = MyMiddleware(hello)
    server = make_server('localhost', 5000, wrapped_app)
    server.serve_forever()
