# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL

from bluelog.models import Category


# 登录表单
class LoginForm(FlaskForm):
    # 用户名字段
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    # 密码字段
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
    # “记住我”复选框
    remember = BooleanField('Remember me')
    # 提交按钮
    submit = SubmitField('Log in')


#
class SettingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    blog_title = StringField('Blog Title', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('Blog Sub Title', validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField('About Page', validators=[DataRequired()])
    submit = SubmitField()


# 文章表单
class PostForm(FlaskForm):
    # 标题
    title = StringField('Title', validators=[DataRequired(), Length(1, 60)])
    # 分类选择，下拉列表，通过coerce指定为整型，即category.id
    category = SelectField('Category', coerce=int, default=1)
    # 正文
    body = CKEditorField('Body', validators=[DataRequired()])
    # 提交
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # 下拉列表的数据，必须是一个包含两个元素元组的列表
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


# 分类表单
class CategoryForm(FlaskForm):
    # 分类名称
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    # 提交按钮
    submit = SubmitField()

    def validate_name(self, field):
        # 自定义行内验证器
        if Category.query.filter_by(name=field.data).first():
            # 如果查询到已经存在同名记录，那么就抛出异常
            raise ValidationError('Name already in use.')


# 评论表单
class CommentForm(FlaskForm):
    # 姓名
    author = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    # 电子邮箱
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    # 站点
    site = StringField('Site', validators=[Optional(), URL(), Length(0, 255)])
    # 正文
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField()


# 管理员评论表单
class AdminCommentForm(CommentForm):
    # 设置隐藏字段
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()


class LinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    url = StringField('URL', validators=[DataRequired(), URL(), Length(1, 255)])
    submit = SubmitField()
