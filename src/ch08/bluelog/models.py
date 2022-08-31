# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from bluelog.extensions import db


# 管理员模型
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # 用户姓名
    username = db.Column(db.String(20))
    # 密码散列值
    password_hash = db.Column(db.String(128))
    # 博客标题
    blog_title = db.Column(db.String(60))
    # 博客副标题
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    # 关于信息
    about = db.Column(db.Text)

    def set_password(self, password):
        # 生成密码散列值
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


# 分类模型
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 分类名称不允许重复
    name = db.Column(db.String(30), unique=True)

    posts = db.relationship('Post', back_populates='category')

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        # 将该分类下的所有文章移动到默认分类中
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


# 文章模型
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 文章标题
    title = db.Column(db.String(60))
    # 文章内容
    body = db.Column(db.Text)
    # 文章发布时间
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    # 是否可以评论
    can_comment = db.Column(db.Boolean, default=True)
    # 分类id
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    # 关联分类表
    category = db.relationship('Category', back_populates='posts')
    # 关联评论表
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')


# 评论模型
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 作者
    author = db.Column(db.String(30))
    # 电子邮件
    email = db.Column(db.String(254))
    # 站点
    site = db.Column(db.String(255))
    # 正文
    body = db.Column(db.Text)
    # 评论是否为管理员评论
    from_admin = db.Column(db.Boolean, default=False)
    # 评论是否通过审核
    reviewed = db.Column(db.Boolean, default=False)
    # 发布时间
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 邻接列表关系，回复模型
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    post = db.relationship('Post', back_populates='comments')
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    # 设置remote_side为id字段，就类似于本地侧
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
    # Same with:
    # replies = db.relationship('Comment', backref=db.backref('replied', remote_side=[id]),
    # cascade='all,delete-orphan')


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))
