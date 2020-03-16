from . import db
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import hashlib, os
import markdown


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.Boolean, default=False)
    role = db.Column(db.Boolean, default=False)
    articles = db.relationship('Article', backref='author', lazy='dynamic')

    @property
    def password(self):
        raise ArithmeticError('非明文密码，不可读。')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    def is_admin(self):
        return self.role

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def is_author(self):
        return Article.query.filter_by(author_id=self.id).first()

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def is_admin(self):
        return False


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64),unique=True,index=True)
    name = db.Column(db.String(64), unique=True, index=True)
    desp = db.Column(db.String(300))
    articles = db.relationship('Article', backref='category', lazy='dynamic')

    def __repr__(self):
        return '<Name %r>' % self.name


article_tag = db.Table('article_tag',
                       db.Column('article_id',db.Integer,db.ForeignKey('article.id'),primary_key=True),
                       db.Column('tag_id',db.Integer,db.ForeignKey('tag.id'),primary_key=True))



class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64),nullable=False, unique=True, index=True)

    def __repr__(self):
        return '<Name %r>' % self.name


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), index=True)
    name = db.Column(db.String(64),index=True,unique=True)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    summary = db.Column(db.String(300))
    thumbnail = db.Column(db.String(200))
    state = db.Column(db.Integer,default=0)
    vc = db.Column(db.Integer,default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    tags = db.relationship('Tag',secondary=article_tag,backref=db.backref('articles',lazy='dynamic'),lazy='dynamic')

    def content_to_html(self):
        return markdown.markdown(self.content, extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            ])

    @property
    def author(self):
        """返回作者对象"""
        return User.query.get(self.author_id)

    @property
    def category(self):
        """返回文章分类对象"""
        return Category.query.get(self.category_id)

    @property
    def category_name(self):
        """返回文章分类名称，主要是为了使用 flask-wtf 的 obj 返回对象的功能"""
        return Category.query.get(self.category_id).name

    @property
    def previous(self):
        """用于分页显示的上一页"""
        a = self.query.filter(Article.state==1,Article.id < self.id). \
            order_by(Article.timestamp.desc()).first()
        return a

    @property
    def next(self):
        """用于分页显示的下一页"""
        a = self.query.filter(Article.state==1,Article.id > self.id). \
            order_by(Article.timestamp.asc()).first()
        return a

    @property
    def tag_names(self):
        """返回文章的标签的字符串，用英文‘, ’分隔，主要用于修改文章功能"""
        tags = []
        for tag in self.tags:
            tags.append(tag.name)
        return ', '.join(tags)

    @property
    def thread_key(self): # 用于评论插件
        return hashlib.new(name='md5', string=str(self.id)).hexdigest()

    def __repr__(self):
        return '<Title %r>' % self.title


class Recommend(db.Model):
    '''
    推荐
    '''
    __tablename__ = 'recommend'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    img = db.Column(db.String(200))
    url = db.Column(db.String(200))
    sn = db.Column(db.Integer,default=0)
    state = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.now)

class AccessLog(db.Model):
    '''
    请求日志
    '''
    __tablename__ = 'access_log'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(20))
    url = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    remark = db.Column(db.String(32))

class Picture(db.Model):
    '''
    图片
    '''
    __tablename__ = 'picture'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    url = db.Column(db.String(120))
    remark = db.Column(db.String(32))