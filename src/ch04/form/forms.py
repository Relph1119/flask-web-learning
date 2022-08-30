#!/usr/bin/env python
# encoding: utf-8
"""
@file: forms.py
@time: 2022/8/30 13:48
@project: flask-web-learning
@desc: 表单类
"""
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, IntegerField, \
    TextAreaField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Length, ValidationError, Email


# 4.2.1节 基本表单类
class LoginForm(FlaskForm):
    # 验证数据是否有效
    username = StringField('Username', validators=[DataRequired()])
    # 验证输入值长度
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    # 单项按钮
    remember = BooleanField('Remember me')
    # 提交按钮
    submit = SubmitField('Log in')


# 自定义验证器
class FortyTwoForm(FlaskForm):
    answer = IntegerField('The Number')
    submit = SubmitField()

    # 对answer进行验证
    def validate_answer(form, field):
        if field.data != 42:
            raise ValidationError('Must be 42.')


# 上传表单
class UploadForm(FlaskForm):
    # 验证文件的类型
    photo = FileField('Upload Image', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField()


# 多文件上传
class MultiUploadForm(FlaskForm):
    photo = MultipleFileField('Upload Image', validators=[DataRequired()])
    submit = SubmitField()


# 包含两个提交按钮的表单
class NewPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 50)])
    body = TextAreaField('Body', validators=[DataRequired()])
    # 保存按钮
    save = SubmitField('Save')
    # 发布按钮
    publish = SubmitField('Publish')


# 登录表单
class SigninForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit1 = SubmitField('Sign in')


# 注册表单
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit2 = SubmitField('Register')


class SigninForm2(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 24)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit = SubmitField()


class RegisterForm2(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 24)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit = SubmitField()


# CKEditor Form
# 文章表单
class RichTextForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 50)])
    # 使用CKEditorField字段类型
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Publish')
