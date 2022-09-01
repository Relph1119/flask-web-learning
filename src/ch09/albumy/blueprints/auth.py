# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user, login_fresh, confirm_login

from albumy.emails import send_confirm_email, send_reset_password_email
from albumy.extensions import db
from albumy.forms.auth import LoginForm, RegisterForm, ForgetPasswordForm, ResetPasswordForm
from albumy.models import User
from albumy.settings import Operations
from albumy.utils import generate_token, validate_token, redirect_back

auth_bp = Blueprint('auth', __name__)


# 处理登录请求
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # 通过表单数据中的email地址查询对应的用户
        user = User.query.filter_by(email=form.email.data.lower()).first()
        # 如果用户存在就验证密码
        if user is not None and user.validate_password(form.password.data):
            if login_user(user, form.remember_me.data):
                flash('Login success.', 'info')
                return redirect_back()
            else:
                # 给封禁用户显示提示消息
                flash('Your account is blocked.', 'warning')
                return redirect(url_for('main.index'))
        # 提示消息“无效的用户名或密码”
        flash('Invalid email or password.', 'warning')
    return render_template('auth/login.html', form=form)


# 重新认证
@auth_bp.route('/re-authenticate', methods=['GET', 'POST'])
@login_required
def re_authenticate():
    # 判断用户的登录会话是否“新鲜”
    if login_fresh():
        return redirect(url_for('main.index'))

    form = LoginForm()
    # 验证表单和密码
    if form.validate_on_submit() and current_user.validate_password(form.password.data):
        # 将会话重新标记为“新鲜”
        confirm_login()
        # 将用户重定向回上一个页面
        return redirect_back()
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect(url_for('main.index'))


# 处理注册请求
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    # 判断表单提交状态
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data.lower()
        username = form.username.data
        password = form.password.data
        user = User(name=name, email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # 生成一个验证令牌
        token = generate_token(user=user, operation='confirm')
        # 向用户邮箱发送一份验证邮件
        send_confirm_email(user=user, token=token)
        # 显示一条消息
        flash('Confirm email sent, check your inbox.', 'info')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)


# 验证邮箱地址
@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    # 判断当前用户的确认状态
    if current_user.confirmed:
        # 已经确认过的用户单击验证链接，会重定向到首页
        return redirect(url_for('main.index'))

    # 验证并解析令牌
    if validate_token(user=current_user, token=token, operation=Operations.CONFIRM):
        flash('Account confirmed.', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('.resend_confirm_email'))


# 重新发送确认邮件
@auth_bp.route('/resend-confirm-email')
@login_required
def resend_confirm_email():
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    # 重新生成令牌
    token = generate_token(user=current_user, operation=Operations.CONFIRM)
    send_confirm_email(user=current_user, token=token)
    flash('New email sent, check your inbox.', 'info')
    return redirect(url_for('main.index'))


# 忘记密码
@auth_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgetPasswordForm()
    if form.validate_on_submit():
        # 通过email查找用户
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # 创建一个令牌
            token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
            # 向用户的邮箱发送验证邮件
            send_reset_password_email(user=user, token=token)
            flash('Password reset email sent, check your inbox.', 'info')
            return redirect(url_for('.login'))
        flash('Invalid email.', 'warning')
        return redirect(url_for('.forget_password'))
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None:
            return redirect(url_for('main.index'))
        if validate_token(user=user, token=token, operation=Operations.RESET_PASSWORD,
                          new_password=form.password.data):
            flash('Password updated.', 'success')
            return redirect(url_for('.login'))
        else:
            flash('Invalid or expired link.', 'danger')
            return redirect(url_for('.forget_password'))
    return render_template('auth/reset_password.html', form=form)
