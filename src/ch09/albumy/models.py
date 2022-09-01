# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import os
from datetime import datetime

from flask import current_app
from flask_avatars import Identicon
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from albumy.extensions import db, whooshee

# relationship table
roles_permissions = db.Table('roles_permissions',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
                             )


# 权限
class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 权限名称
    name = db.Column(db.String(30), unique=True)
    # 建立与角色的关联关系，多对多关系
    roles = db.relationship('Role', secondary=roles_permissions, back_populates='permissions')


# 角色
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 角色名称
    name = db.Column(db.String(30), unique=True)
    users = db.relationship('User', back_populates='role')
    # 建立与权限的关联关系，多对多关系
    permissions = db.relationship('Permission', secondary=roles_permissions, back_populates='roles')

    @staticmethod
    def init_role():
        # 定义角色的权限（key=角色 : value=权限）
        # Follow：关注用户
        # COLLECT：收藏图片
        # COMMENT：发表评论
        # UPLOAD：上传图片
        # MODERATE：协管员权限
        # ADMINISTER：管理员权限
        roles_permissions_map = {
            'Locked': ['FOLLOW', 'COLLECT'],
            'User': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD'],
            'Moderator': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD', 'MODERATE'],
            'Administrator': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD', 'MODERATE', 'ADMINISTER']
        }

        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                # 添加角色与权限的关联数据
                role.permissions.append(permission)
        db.session.commit()


# relationship object
# 用户关注：用户与用户之间的多对多关系
class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship('User', foreign_keys=[follower_id], back_populates='following', lazy='joined')
    followed = db.relationship('User', foreign_keys=[followed_id], back_populates='followers', lazy='joined')


# relationship object
# 收藏图片：使用模型表示多对多关系
class Collect(db.Model):
    collector_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                             primary_key=True)
    collected_id = db.Column(db.Integer, db.ForeignKey('photo.id'),
                             primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # 多对多关系，预加载方式，对关系两侧的表进行联结操作
    collector = db.relationship('User', back_populates='collections', lazy='joined')
    collected = db.relationship('Photo', back_populates='collectors', lazy='joined')


# 用户模型，注册name、username字段索引
@whooshee.register_model('name', 'username')
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # 用户资料
    username = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(30))
    website = db.Column(db.String(255))
    bio = db.Column(db.String(120))
    location = db.Column(db.String(50))
    # 用户加入时间
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    # 三种尺寸头像的文件名
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    # 用户上传的头像文件原图的文件名
    avatar_raw = db.Column(db.String(64))
    # 用户状态
    confirmed = db.Column(db.Boolean, default=False)
    locked = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    # 用户收藏开关选项
    public_collections = db.Column(db.Boolean, default=True)
    # 三类提醒的接收开关选项
    receive_comment_notification = db.Column(db.Boolean, default=True)
    receive_follow_notification = db.Column(db.Boolean, default=True)
    receive_collect_notification = db.Column(db.Boolean, default=True)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    role = db.relationship('Role', back_populates='users')
    photos = db.relationship('Photo', back_populates='author', cascade='all')
    comments = db.relationship('Comment', back_populates='author', cascade='all')
    notifications = db.relationship('Notification', back_populates='receiver', cascade='all')
    # 用户的收藏图片
    collections = db.relationship('Collect', back_populates='collector', cascade='all')
    # 正在关注的Follow记录
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id], back_populates='follower',
                                lazy='dynamic', cascade='all')
    # 关注者的Follow记录
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], back_populates='followed',
                                lazy='dynamic', cascade='all')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_avatar()
        # 关注自己
        self.follow(self)  # follow self
        self.set_role()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_role(self):
        # 初始化用户角色
        if self.role is None:
            if self.email == current_app.config['ALBUMY_ADMIN_EMAIL']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(name='User').first()
            db.session.commit()

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 关注
    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()

    # 取消关注
    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    # 是否已关注了该用户
    def is_following(self, user):
        if user.id is None:  # when follow self, user.id will be None
            return False
        return self.following.filter_by(followed_id=user.id).first() is not None

    # 是否被关注
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_photos(self):
        return Photo.query.join(Follow, Follow.followed_id == Photo.author_id).filter(Follow.follower_id == self.id)

    # 收藏图片
    def collect(self, photo):
        if not self.is_collecting(photo):
            # 添加一条收藏记录
            collect = Collect(collector=self, collected=photo)
            db.session.add(collect)
            db.session.commit()

    # 取消收藏图片
    def uncollect(self, photo):
        collect = Collect.query.with_parent(self).filter_by(collected_id=photo.id).first()
        if collect:
            # 删除收藏记录
            db.session.delete(collect)
            db.session.commit()

    def is_collecting(self, photo):
        return Collect.query.with_parent(self).filter_by(collected_id=photo.id).first() is not None

    # 用户锁定
    def lock(self):
        # 设置锁定
        self.locked = True
        self.role = Role.query.filter_by(name='Locked').first()
        db.session.commit()

    # 用户解除锁定
    def unlock(self):
        # 设置解除锁定
        self.locked = False
        self.role = Role.query.filter_by(name='User').first()
        db.session.commit()

    def block(self):
        self.active = False
        db.session.commit()

    def unblock(self):
        self.active = True
        db.session.commit()

    def generate_avatar(self):
        # 生成Identicon头像
        avatar = Identicon()
        # 生成三种尺寸的文件名
        filenames = avatar.generate(text=self.username)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()

    @property
    def is_admin(self):
        # 判断用户对象的角色名是否为Administrator实现
        return self.role.name == 'Administrator'

    @property
    def is_active(self):
        return self.active

    def can(self, permission_name):
        # 添加权限验证
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and self.role is not None and permission in self.role.permissions


# 创建关联表
tagging = db.Table('tagging',
                   db.Column('photo_id', db.Integer, db.ForeignKey('photo.id')),
                   db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                   )


# 图片模型，注册description字段索引
@whooshee.register_model('description')
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 图片描述
    description = db.Column(db.String(500))
    # 文件名
    filename = db.Column(db.String(64))
    # 小尺寸图片文件名
    filename_s = db.Column(db.String(64))
    # 中型尺寸图片文件名
    filename_m = db.Column(db.String(64))
    # 图片上传时间
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    can_comment = db.Column(db.Boolean, default=True)
    # 被举报次数
    flag = db.Column(db.Integer, default=0)
    # 关联user.id的外键
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # User模型和Photo模型的一对多关系
    author = db.relationship('User', back_populates='photos')
    comments = db.relationship('Comment', back_populates='photo', cascade='all')
    collectors = db.relationship('Collect', back_populates='collected', cascade='all')
    tags = db.relationship('Tag', secondary=tagging, back_populates='photos')


# 图片标签，注册name字段索引
@whooshee.register_model('name')
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    photos = db.relationship('Photo', secondary=tagging, back_populates='tags')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    flag = db.Column(db.Integer, default=0)

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))

    photo = db.relationship('Photo', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    replies = db.relationship('Comment', back_populates='replied', cascade='all')
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])


# 提醒消息模型
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 提醒的消息正文
    message = db.Column(db.Text, nullable=False)
    # 消息的状态，是否已读
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 和User的一对多关系
    receiver = db.relationship('User', back_populates='notifications')


# 头像图片删除事件监听，当删除用户账户，自动删除用户相关的头像图片
@db.event.listens_for(User, 'after_delete', named=True)
def delete_avatars(**kwargs):
    target = kwargs['target']
    for filename in [target.avatar_s, target.avatar_m, target.avatar_l, target.avatar_raw]:
        if filename is not None:  # avatar_raw may be None
            path = os.path.join(current_app.config['AVATARS_SAVE_PATH'], filename)
            if os.path.exists(path):  # not every filename map a unique file
                os.remove(path)


# 图片删除事件监听，当Photo记录被删除时，自动删除对应的文件
@db.event.listens_for(Photo, 'after_delete', named=True)
def delete_photos(**kwargs):
    target = kwargs['target']
    for filename in [target.filename, target.filename_s, target.filename_m]:
        path = os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], filename)
        if os.path.exists(path):  # not every filename map a unique file
            # 删除图片文件
            os.remove(path)
