# -*- coding:utf-8 -*-
__author__ = '何三'

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
	search = StringField('search', validators=[DataRequired()])

