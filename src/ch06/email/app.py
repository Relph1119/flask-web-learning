#!/usr/bin/env python
# encoding: utf-8
"""
@file: app.py
@time: 2022/8/30 20:16
@project: flask-web-learning
@desc: 电子邮件操作
"""
import os
from threading import Thread

import sendgrid
from sendgrid.helpers.mail import Email as SGEmail, Content, Mail as SGMail
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from flask import Flask, flash, redirect, url_for, render_template, request

app = Flask(__name__)
# 删除Jinja2语句后的第一个空行
app.jinja_env.trim_blocks = True
# 删除Jinja2语句所在行之前的空格和制表符(tabs)
app.jinja_env.lstrip_blocks = True

# 配置Flask-Mail
app.config.update(
    # 设置CSRF令牌的密钥
    SECRET_KEY=os.getenv('SECRET_KEY', 'secret string'),
    # 配置发送邮件的SMTP服务器
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    # 配置发信端口
    MAIL_PORT=465,
    # 配置使用SSL
    MAIL_USE_SSL=True,
    # 配置发信服务器的用户名
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    # 配置发信服务器的密码
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    # 配置默认的发信人
    MAIL_DEFAULT_SENDER=('Grey Li', os.getenv('MAIL_USERNAME'))
)

mail = Mail(app)


# send over SMTP
def send_smtp_mail(subject, to, body):
    # 创建Message对象
    message = Message(subject, recipients=[to], body=body)
    # 发送邮件
    mail.send(message)


# 使用SendGrid Web API发送邮件的通用函数
def send_api_mail(subject, to, body):
    sg = sendgrid.SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    from_email = SGEmail('Grey Li <noreply@helloflask.com>')
    to_email = SGEmail(to)
    content = Content("text/plain", body)
    email = SGMail(from_email, subject, to_email, content)
    sg.client.mail.send.post(request_body=email.get())


# send email asynchronously
def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


# 异步发送邮件
def send_async_mail(subject, to, body):
    # app = current_app._get_current_object()  # if use factory (i.e. create_app()), get app like this
    message = Message(subject, recipients=[to], body=body)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


# 使用HTML邮件模板发送邮件
def send_subscribe_mail(subject, to, **kwargs):
    message = Message(subject, recipients=[to], sender='Flask Weekly <%s>' % os.getenv('MAIL_USERNAME'))
    message.body = render_template('emails/subscribe.txt', **kwargs)
    message.html = render_template('emails/subscribe.html', **kwargs)
    mail.send(message)


class EmailForm(FlaskForm):
    to = StringField('To', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])
    submit_smtp = SubmitField('Send with SMTP')
    submit_api = SubmitField('Send with SendGrid API')
    submit_async = SubmitField('Send with SMTP asynchronously')


class SubscribeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    if form.validate_on_submit():
        to = form.to.data
        subject = form.subject.data
        body = form.body.data
        if form.submit_smtp.data:
            send_smtp_mail(subject, to, body)
            method = request.form.get('submit_smtp')
        elif form.submit_api.data:
            send_api_mail(subject, to, body)
            method = request.form.get('submit_api')
        else:
            send_async_mail(subject, to, body)
            method = request.form.get('submit_async')

        flash('Email sent %s! Check your inbox.' % ' '.join(method.split()[1:]))
        return redirect(url_for('index'))
    form.subject.data = 'Hello, World!'
    form.body.data = 'Across the Great Wall we can reach every corner in the world.'
    return render_template('index.html', form=form)


# 发送一封邮件来通知用户订阅成功
@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SubscribeForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        send_subscribe_mail('Subscribe Success!', email, name=name)
        flash('Confirmation email have been sent! Check your inbox.')
        return redirect(url_for('subscribe'))
    return render_template('subscribe.html', form=form)


@app.route('/unsubscribe')
def unsubscribe():
    flash('Want to unsubscribe? No way...')
    return redirect(url_for('subscribe'))
