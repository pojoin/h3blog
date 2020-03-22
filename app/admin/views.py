from flask import render_template, request, redirect, url_for, flash, current_app, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from . import admin
from app.extensions import db
from .forms import AddAdminForm, LoginForm, AddUserForm, DeleteUserForm, EditUserForm, ArticleForm, \
        ChangePasswordForm, AddFolderForm, CategoryForm, RecommendForm, InvitcodeForm
from app.models import User, Category, Tag, Article, Recommend, AccessLog, Picture, InvitationCode
import os
from datetime import datetime
from app.util import admin_required, author_required, isAjax, upload_file_qiniu, allowed_file, \
    baidu_push_urls, strip_tags, gen_invit_code


@admin.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    current_user.ping()

    return render_template('admin/index.html')


@admin.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(prefix='login')
    user = User.query.filter_by(status=True).first()
    if not user:
        add_admin_form = AddAdminForm(prefix='add_admin')
        if add_admin_form.validate_on_submit():
            u = User(username=add_admin_form.username.data.strip(),
                     email=add_admin_form.email.data.strip(),
                     password=add_admin_form.password.data.strip(),
                     status=True, role=True
                     )
            db.session.add(u)
            db.session.commit()
            login_user(user=u)
            return redirect(url_for('admin.index'))

        return render_template('admin/add_admin.html', addAdminForm=add_admin_form)
    else:
        if login_form.validate_on_submit():
            u = User.query.filter_by(username=login_form.username.data.strip()).first()
            if u is None:
                flash({'error': '帐号未注册！'})
            elif u is not None and u.verify_password(login_form.password.data.strip()) and u.status:
                login_user(user=u, remember=login_form.remember_me.data)
                return redirect(url_for('admin.index'))
            elif not u.status:
                flash({'error': '用户已被管理员注销！'})
            elif not u.verify_password(login_form.password.data.strip()):
                flash({'error': '密码不正确！'})

    return render_template('admin/login.html', loginForm=login_form)

@admin.route('/logout')
@login_required
def logout():
    """
    退出系统
    """
    logout_user()
    return redirect(url_for('main.index'))

@admin.route('/articles', methods=['GET'])
@login_required
@admin_required
def articles():
    title = request.args.get('title','')
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter(
        Article.title.like("%" + title + "%") if title is not None else ''
        ).order_by(Article.timestamp.desc()).paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)

    return render_template('admin/articles.html', articles=articles,title = title)


@admin.route('/article/edit/<id>', methods=['GET'])
@login_required
@admin_required
def article_edit(id):
    article = Article.query.get(int(id))
    form = ArticleForm(obj=article)
    form.tags.data = ','.join([t.name for t in article.tags.all()])
    return render_template('admin/write.html', form=form)


@admin.route('/article/write', methods=['GET','POST'])
@login_required
@admin_required
def write():
    form = ArticleForm()
    if form.validate_on_submit():
        # --------以下功能是增加文章的分类
        cty = Category.query.get(int(form.category_id.data))
        a = None
        if form.id.data:
            a = Article.query.get(int(form.id.data))
        if a :
            a.title = form.title.data.strip()
            a.content = form.content.data
            a.content_html = a.content_to_html()
            a.summary = form.summary.data
            a.thumbnail = form.thumbnail.data
            a.category = cty
            a.name = form.name.data.strip()
            a.state = form.state.data
            a.timestamp = form.timestamp.data
            if not a.name and len(a.name) == 0 :
                a.name = a.id
            db.session.commit()
        else:
            # --------以下功能是将文章信息插入数据库
            a = Article(title=form.title.data.strip(), content=form.content.data,
                        thumbnail = form.thumbnail.data,name = form.name.data.strip(),
                        state = form.state.data,summary = form.summary.data,
                        category=cty, author=current_user._get_current_object())
            a.content_html = a.content_to_html()
            db.session.add(a)
            db.session.commit()
            if not a.name and len(a.name) == 0 :
                a.name = a.id
                db.session.commit()
        # --------以下功能是将文章标识插入数据库
        a.tags = []
        for tg in form.tags.data.split(','):
            if tg.strip() == '':
                continue
            t = Tag.query.filter_by(name=tg.strip()).first()
            if not t:
                t = Tag(name=tg.strip())
                db.session.add(t)
            if t not in a.tags :
                a.tags.append(t)
        if isAjax() :
            msg = '发布成功' if int(form.state.data) == 1 else '保存成功' 
            return jsonify({'code':1,'msg':msg,'id':a.id})

    return render_template('admin/write.html', form=form)

@admin.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    add_user_form = AddUserForm(prefix='add_user')
    delete_user_form = DeleteUserForm(prefix='delete_user')
    if add_user_form.validate_on_submit():
        if add_user_form.role.data == 'True':
            role = True
        else:
            role = False
        if add_user_form.status.data == 'True':
            status = True
        else:
            status = False
        u = User(username=add_user_form.username.data.strip(), email=add_user_form.email.data.strip(),
                 role=role, status=status, password='123456')
        db.session.add(u)
        flash({'success': '添加用户<%s>成功！' % add_user_form.username.data.strip()})
    if delete_user_form.validate_on_submit():
        u = User.query.get_or_404(int(delete_user_form.user_id.data.strip()))
        db.session.delete(u)
        flash({'success': '删除用户<%s>成功！' % u.username})

    users = User.query.all()

    return render_template('admin/users.html', users=users, addUserForm=add_user_form,
                           deleteUserForm=delete_user_form)


@admin.route('/user-edit/<user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    edit_user_form = EditUserForm(prefix='edit_user', obj=user)
    if edit_user_form.validate_on_submit():
        user.username = edit_user_form.username.data.strip()
        user.email = edit_user_form.email.data.strip()
        if edit_user_form.role.data == 'True':
            user.role = True
        else:
            user.role = False
        if edit_user_form.status.data == 'True':
            user.status = True
        else:
            user.status = False
        flash({'success': '用户资料已修改成功！'})

    return render_template('admin/edit_user.html', editUserForm=edit_user_form, user=user)


@admin.route('/password', methods=['GET', 'POST'])
@login_required
@admin_required
def password():
    change_password_form = ChangePasswordForm(prefix='change_password')
    if change_password_form.validate_on_submit():
        if current_user.verify_password(change_password_form.old_password.data.strip()):
            current_user.password = change_password_form.password.data.strip()
            # db.session.add(current_user)
            db.session.commit()
            flash({'success': '您的账户密码已修改成功！'})
        else:
            flash({'error': '无效的旧密码！'})

    return render_template('admin/password.html', changePasswordForm=change_password_form)


@admin.route('/upload',methods=['POST'])
@login_required
@admin_required
def upload():
    """图片上传处理"""
    file=request.files.get('file')
    if not allowed_file(file.filename):
        res={
            'code':0,
            'msg':'图片格式异常'
        }
    else:
        url_path = ''
        upload_type = current_app.config.get('H3BLOG_UPLOAD_TYPE')
        ex=os.path.splitext(file.filename)[1]
        filename=datetime.now().strftime('%Y%m%d%H%M%S')+ex
        if upload_type is None or upload_type == '' or upload_type == 'local':
            file.save(os.path.join(current_app.config['H3BLOG_UPLOAD_PATH'],filename))
            url_path = url_for('admin.get_image',filename=filename)
        elif upload_type == 'qiniu':
            try:
                qiniu_cdn_url = current_app.config.get('QINIU_CDN_URL')
                url_path = qiniu_cdn_url + upload_file_qiniu(file.read(),filename)
            except Exception as e:
                return jsonify({'success':0,'message':'上传图片异常'})
        #返回
        pic = Picture(name = file.filename if len(file.filename)< 32 else filename,url = url_path)
        db.session.add(pic)
        res={
            'code':1,
            'msg':u'图片上传成功',
            'url': url_path
        }
    return jsonify(res)


@admin.route('/tags')
@login_required
@admin_required
def tags():
    '''
    标签管理
    '''
    page = request.args.get('page',1,type=int)
    tags = Tag.query.order_by(Tag.id.asc()). \
        paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)
    return   render_template('admin/tags.html',tags=tags)

@admin.route('/categorys',methods=['GET'])
@login_required
@admin_required
def categorys():
    """
    分类
    """
    page = request.args.get('page', 1, type=int)
    categorys = Category.query.order_by(Category.id.asc()).paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)

    return render_template('admin/categorys.html',categorys=categorys)

@admin.route('/categorys/add',methods=['GET','POST'])
@login_required
@admin_required
def categroy_add():
    """
    添加分类
    """
    form = CategoryForm()
    if form.validate_on_submit():
        c = Category(title=form.title.data.strip(),
                name=form.name.data.strip(),
                desp = form.desp.data)
        db.session.add(c)
        db.session.commit()  
        return redirect(url_for('admin.categorys'))

    return render_template('admin/category.html',form=form)

@admin.route('/categorys/edit/<id>',methods=['GET','POST'])
@login_required
@admin_required
def categroy_edit(id):
    """
    修改分类
    """
    c = Category.query.get(id)
    form = CategoryForm()
    if form.validate_on_submit():
        c.title = form.title.data.strip()
        c.name = form.name.data.strip()
        c.desp = form.desp.data
        db.session.commit()
        return redirect(url_for('admin.categorys'))

    form = CategoryForm(obj=c)
    return render_template('admin/category.html',form=form)

@admin.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['H3BLOG_UPLOAD_PATH'], filename)

@admin.route('/imagehosting')
@login_required
@admin_required
def image_hosting():
    """
    图床
    """
    # from app.util import file_list_qiniu
    # imgs = file_list_qiniu()
    page = request.args.get('page',1, type=int)
    imgs = Picture.query.order_by(Picture.id.desc()). \
        paginate(page, per_page=20, error_out=False)
    return render_template('admin/image_hosting.html',imgs = imgs)

@admin.route('/baidu_push_urls',methods=['POST'])
@admin_required
def baidu_push_article():
    urls = request.form.get('urls')
    domain = current_app.config.get('H3BLOG_DOMAIN','https://www.h3blog.com')
    ret = baidu_push_urls(domain,urls)
    return jsonify(ret)

@admin.route('/recommends',methods=['GET'])
@login_required
@admin_required
def recommends():
    '''
    推荐列表
    '''
    page = request.args.get('page',1, type=int)
    recommends = Recommend.query.order_by(Recommend.sn.desc()). \
        paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)
    return render_template('admin/recommends.html',recommends = recommends)

@admin.route('/recommends/add',methods=['GET','POST'])
@login_required
@admin_required
def recommends_add():
    '''
    添加推荐
    '''
    form = RecommendForm()
    if form.validate_on_submit():
        r = Recommend(title=form.title.data.strip(),
                url=form.url.data,
                img = form.img.data,
                sn = form.sn.data,
                state = form.state.data)
        db.session.add(r)
        db.session.commit()  
        return redirect(url_for('admin.recommends'))

    return render_template('admin/recommend.html',form=form)

@admin.route('/recommends/edit/<id>',methods=['GET','POST'])
@login_required
@admin_required
def recommends_edit(id):
    """
    修改推荐
    """
    r = Recommend.query.get(id)
    form = RecommendForm()
    if form.validate_on_submit():
        r.title = form.title.data.strip()
        r.url = form.url.data
        r.img = form.img.data
        r.sn = form.sn.data
        r.state = form.state.data
        db.session.commit()
        return redirect(url_for('admin.recommends'))

    form = RecommendForm(obj=r)
    return render_template('admin/recommend.html',form=form)



@admin.route('/accesslogs',methods=['GET'])
@login_required
@admin_required
def access_logs():
    '''
    搜索引擎抓取记录
    '''
    remark = request.args.get('remark','')
    params = {'remark': remark}
    page = request.args.get('page',1, type=int)
    logs = AccessLog.query.filter(
        AccessLog.remark.like("%" + remark + "%") if remark is not None else ''
        ).order_by(AccessLog.timestamp.desc()). \
        paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)
    return render_template('admin/access_log.html',logs = logs,params = params)

@admin.route('/invitcodes',methods=['GET','POST'])
@login_required
@admin_required
def invit_codes():
    '''
    邀请码
    '''
    form = InvitcodeForm()
    if form.validate_on_submit:
        count = int(form.count.data)
        cs = gen_invit_code(count,15)
        for c in cs:
            ic = InvitationCode(code = c)
            db.session.add(ic)
        db.session.commit()
    page = request.args.get('page',1, type=int)
    codes = InvitationCode.query.order_by(InvitationCode.id.asc()). \
        paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)
    
    return render_template('admin/invit_codes.html',codes = codes,form = form)
