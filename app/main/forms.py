# -*- coding:utf-8 -*-
__author__ = '何三'

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('帐号', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField(label='记住我', default=False)
    submit = SubmitField('登 录')


class RegistForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 16, message='用户名长度要在1和16之间')])
    email = StringField('邮箱', validators=[DataRequired(), Length(6, 64, message='邮件长度要在6和64之间'),
                        Email(message='邮件格式不正确！')])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='密码必须一致！')])
    password2 = PasswordField('重输密码', validators=[DataRequired()])
    submit = SubmitField('注 册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被注册！')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册！')


class SearchForm(FlaskForm):
	search = StringField('search', validators=[DataRequired()])

