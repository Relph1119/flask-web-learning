#!/usr/bin/env python
# encoding: utf-8
"""
@file: app.py
@time: 2022/8/30 16:16
@project: flask-web-learning
@desc: 数据库操作
"""
import os
import sys

import click
from flask import Flask
from flask import redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
# 删除Jinja2语句后的第一个空行
app.jinja_env.trim_blocks = True
# 删除Jinja2语句所在行之前的空格和制表符(tabs)
app.jinja_env.lstrip_blocks = True
# 设置CSRF令牌的密钥
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret string')
# 设置数据库的URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', prefix + os.path.join(app.root_path, 'data.db'))
# 关闭警告信息
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 创建数据库实例
db = SQLAlchemy(app)


# 注册shell上下文处理函数
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Note=Note, Author=Author, Article=Article, Writer=Writer, Book=Book,
                Singer=Singer, Song=Song, Citizen=Citizen, City=City, Capital=Capital,
                Country=Country, Teacher=Teacher, Student=Student, Post=Post, Comment=Comment, Draft=Draft)


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        click.confirm('This operation will delete the database, do you want to continue?', abort=True)
        db.drop_all()
        click.echo('Drop tables.')
    db.create_all()
    click.echo('Initialized database.')


# 创建笔记NewNoteForm的模板
class NewNoteForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Save')


class EditNoteForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Update')


class DeleteNoteForm(FlaskForm):
    submit = SubmitField('Delete')


# 定义Note模型
class Note(db.Model):
    # 包含id（整型）和bodu（Text文本类型）两个字段
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)

    # optional
    def __repr__(self):
        return '<Note %r>' % self.body


@app.route('/')
def index():
    form = DeleteNoteForm()
    # 读取数据库中的所有记录
    notes = Note.query.all()
    return render_template('index.html', notes=notes, form=form)


# 创建新笔记
@app.route('/new', methods=['GET', 'POST'])
def new_note():
    form = NewNoteForm()
    if form.validate_on_submit():
        body = form.body.data
        # 保存到数据库中
        note = Note(body=body)
        db.session.add(note)
        db.session.commit()
        flash('Your note is saved.')
        return redirect(url_for('index'))
    return render_template('new_note.html', form=form)


@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    form = EditNoteForm()
    note = Note.query.get(note_id)
    if form.validate_on_submit():
        # 修改数据
        note.body = form.body.data
        db.session.commit()
        flash('Your note is updated.')
        return redirect(url_for('index'))
    form.body.data = note.body  # preset form input's value
    return render_template('edit_note.html', form=form)


@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    form = DeleteNoteForm()
    if form.validate_on_submit():
        # 删除数据
        note = Note.query.get(note_id)
        db.session.delete(note)
        db.session.commit()
        flash('Your note is deleted.')
    else:
        abort(400)
    return redirect(url_for('index'))


# 一对多的关系，1个author对应多个article
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    phone = db.Column(db.String(20))
    # 定义关系属性
    articles = db.relationship('Article')  # collection

    def __repr__(self):
        return '<Author %r>' % self.name


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True)
    body = db.Column(db.Text)
    # 定义author.id作为外键
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    def __repr__(self):
        return '<Article %r>' % self.title


# 建立多对一关系
class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City')  # scalar

    def __repr__(self):
        return '<Citizen %r>' % self.name


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    def __repr__(self):
        return '<City %r>' % self.name


# 建立一对一关系
class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    # uselist=False，将多对多转换为一对一关系
    capital = db.relationship('Capital', back_populates='country', uselist=False)  # collection -> scalar

    def __repr__(self):
        return '<Country %r>' % self.name


class Capital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country', back_populates='capital')  # scalar

    def __repr__(self):
        return '<Capital %r>' % self.name


# 建立多对多关系
# 建立association关联表
association_table = db.Table('association',
                             db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                             db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'))
                             )


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    grade = db.Column(db.String(20))
    # 建立双向关系
    teachers = db.relationship('Teacher',
                               secondary=association_table,
                               back_populates='students')  # collection

    def __repr__(self):
        return '<Student %r>' % self.name


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    office = db.Column(db.String(20))
    # 建立双向关系
    students = db.relationship('Student',
                               secondary=association_table,
                               back_populates='teachers')  # collection

    def __repr__(self):
        return '<Teacher %r>' % self.name


# 基于一对多关系的双向关系
class Writer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # back_populates反向引用
    books = db.relationship('Book', back_populates='writer')

    def __repr__(self):
        return '<Writer %r>' % self.name


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    writer_id = db.Column(db.Integer, db.ForeignKey('writer.id'))
    writer = db.relationship('Writer', back_populates='books')

    def __repr__(self):
        return '<Book %r>' % self.name


# 一对多，使用backref建立双向关系
class Singer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    songs = db.relationship('Song', backref='singer')

    def __repr__(self):
        return '<Singer %r>' % self.name


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    singer_id = db.Column(db.Integer, db.ForeignKey('singer.id'))

    def __repr__(self):
        return '<Song %r>' % self.name


# 级联操作
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.Text)
    # 级联操作
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')  # collection


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')  # scalar


# 事件监听
class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    edit_time = db.Column(db.Integer, default=0)


@db.event.listens_for(Draft.body, 'set')
def increment_edit_time(target, value, oldvalue, initiator):
    if target.edit_time is not None:
        target.edit_time += 1

# same with:
# @db.event.listens_for(Draft.body, 'set', named=True)
# def increment_edit_time(**kwargs):
#     if kwargs['target'].edit_time is not None:
#         kwargs['target'].edit_time += 1
