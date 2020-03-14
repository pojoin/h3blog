from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,IntegerField,HiddenField, BooleanField, SubmitField, SelectField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User, Category, Article
from datetime import datetime


class LoginForm(FlaskForm):
    username = StringField('帐号', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField(label='记住我', default=False)
    submit = SubmitField('登 录')


class AddAdminForm(FlaskForm):
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


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='密码必须一致！')])
    password2 = PasswordField('重输密码', validators=[DataRequired()])
    submit = SubmitField('更新密码')


class AddUserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64, message='姓名长度要在1和64之间'),
                       Regexp('^[\u4E00-\u9FFF]+$', flags=0, message='用户名必须为中文')])
    email = StringField('邮箱', validators=[DataRequired(), Length(6, 64, message='邮件长度要在6和64之间'),
                        Email(message='邮件格式不正确！')])
    role = SelectField('权限', choices=[('True', '管理员'), ('False', '一般用户') ])
    status = SelectField('状态', choices=[('True', '正常'), ('False', '注销') ])
    submit = SubmitField('添加用户')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被注册！')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册！')


class DeleteUserForm(FlaskForm):
    user_id = StringField()


class EditUserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64, message='姓名长度要在1和64之间'),
                       Regexp('^[\u4E00-\u9FFF]+$', flags=0, message='用户名必须为中文')])
    email = StringField('邮箱', validators=[DataRequired(), Length(6, 64, message='邮件长度要在6和64之间'),
                        Email(message='邮件格式不正确！')])
    role = SelectField('权限', choices=[('True', '管理员'), ('False', '一般用户') ])
    status = SelectField('状态', choices=[('True', '正常'), ('False', '注销')])
    submit = SubmitField('修改用户')

class ArticleForm(FlaskForm):
    id = HiddenField('id')
    title = StringField('标题',validators=[DataRequired('请录入标题')])
    name = StringField('标识名称',render_kw={'placeholder':'自定义路径'},validators=[DataRequired()])
    content = TextAreaField('文章内容')
    category_id = SelectField('分类',coerce=int, default=1,validators=[DataRequired('请选择分类')])
    tags = StringField('标签')
    state = HiddenField('状态',default=0)
    thumbnail = HiddenField('缩略图',default='/static/img/thumbnail.jpg')
    summary = TextAreaField('概述',validators=[DataRequired(),Length(1, 300, message='长度必须设置在300个字符内')])
    timestamp = DateTimeField('发布时间',default=datetime.now)
    save = SubmitField('保存')
    
    def __init__(self,*args,**kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(category.id, category.title)
                                 for category in Category.query.order_by(Category.title).all()]

    def validate_name(self,field):
        """
        验证文章名称标识的唯一性
        """
        name = field.data
        articles = Article.query.filter_by(name = name).all()
        if len(articles) >1:
            raise ValidationError('路径已经存在')
        if len(articles) == 1 and self.id.data and  articles[0].id != int(self.id.data):
            raise ValidationError('路径已经存在')

class CategoryForm(FlaskForm):
    id = HiddenField('id')
    title = StringField('名称',validators=[DataRequired()])
    name = StringField('标识',validators=[DataRequired()])
    desp = TextAreaField('描述')
    submit = SubmitField('提交')


class RecommendForm(FlaskForm):
    id = HiddenField('id')
    title = StringField('标题',validators=[DataRequired()])
    url = StringField('链接',validators=[DataRequired()],default='#')
    sn = IntegerField('排序',default=0)
    img = StringField('图片',validators=[DataRequired()])
    state = SelectField('状态', choices=[('1', '正常'), ('0', '停止') ])
    submit = SubmitField('提交')



class BaidutongjiForm(FlaskForm):
    token = StringField('健值')
    status = SelectField('状态', choices=[('True', '启用'), ('False', '停用')])
    submit = SubmitField('提交')


class AddFolderForm(FlaskForm):
    directory = StringField('文件夹')
    submit = SubmitField('确定')
