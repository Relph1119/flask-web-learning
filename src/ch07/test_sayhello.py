# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import unittest

from flask import abort

from sayhello import app, db
from sayhello.models import Message
from sayhello.commands import forge, initdb


class SayHelloTestCase(unittest.TestCase):

    # 配置环境变量，创建内存数据库
    def setUp(self):
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        db.create_all()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

    # 清除会话，清除测试数据库
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_app_exist(self):
        self.assertFalse(app is None)

    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    # 测试404错误页面
    def test_404_page(self):
        # 访问一个未定义的URL
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('404 Error', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)

    # 测试500错误页面
    def test_500_page(self):
        # 临时创建一个视图，用于生成500错误响应
        @app.route('/500')
        def internal_server_error_for_test():
            abort(500)

        response = self.client.get('/500')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn('500 Error', data)
        self.assertIn('Go Back', data)

    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Say Hello', data)

    # 测试创建新消息
    def test_create_message(self):
        response = self.client.post('/', data=dict(
            name='Peter',
            body='Hello, world.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Your message have been sent to the world!', data)
        self.assertIn('Hello, world.', data)

    # 测试表单验证
    def test_form_validation(self):
        response = self.client.post('/', data=dict(
            name=' ',
            body='Hello, world.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('This field is required.', data)

    # 测试forge命令
    def test_forge_command(self):
        # 使用invoke()函数调用forge命令
        result = self.runner.invoke(forge)
        self.assertIn('Created 20 fake messages.', result.output)
        self.assertEqual(Message.query.count(), 20)

    # 测试添加--count选项的forge命令
    def test_forge_command_with_count(self):
        result = self.runner.invoke(forge, ['--count', '50'])
        self.assertIn('Created 50 fake messages.', result.output)
        self.assertEqual(Message.query.count(), 50)

    # 测试initdb命令
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)

    # 测试添加--drop选项的initdb命令
    def test_initdb_command_with_drop(self):
        result = self.runner.invoke(initdb, ['--drop'], input='y\n')
        self.assertIn('This operation will delete the database, do you want to continue?', result.output)
        self.assertIn('Drop tables.', result.output)


if __name__ == '__main__':
    unittest.main()
