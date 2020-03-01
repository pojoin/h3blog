from flask import render_template, redirect, request, current_app, \
    url_for, g, send_from_directory
from . import main
from ..models import Article, Tag, Category, article_tag
from .forms import SearchForm
from ..import db, sitemap


@main.before_request
def before_request():
    if '/css/' in request.path or '/js/' in request.path or '/img/' in request.path:
        return
    g.tags = Tag.query.all()
    g.categorys = Category.query.all()
    g.recent_articles = Article.query.filter_by(state=1).order_by(Article.timestamp.desc()).limit(5).all()
    # articles = Article.query.order_by(Article.timestamp.desc()).all()
    # time_tag = []
    # for a in articles:
    #     if a.timestamp.strftime('%Y-%m') not in time_tag:
    #         time_tag.append(a.timestamp.strftime('%Y-%m'))
    # g.time_tag = time_tag
    g.search_form = SearchForm(prefix='search')


@main.route('/', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter_by(state=1). \
        order_by(Article.timestamp.desc()). \
        paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)

    return render_template('index.html', articles=articles)
@main.route('/hot/',methods=['GET'])
def hot():
    page = request.args.get('page',1,type=int)
    articles = Article.query.filter_by(state=1). \
        order_by(Article.vc.desc()). \
        paginate(page,per_page=current_app.config['H3BLOG_POST_PER_PAGE'],error_out=False)
    return render_template('index.html',articles=articles)

@main.route('/about/', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@main.route('/article/<name>/', methods=['GET', 'POST'])
def article(name):
    article = Article.query.filter_by(name=name).first()
    article.vc = article.vc + 1
    db.session.commit()
    return render_template('article.html', article=article)


@main.route('/tag/<t>/', methods=['GET'])
def tag(t):
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.filter_by(name=t).first()
    articles = tag.articles.filter(Article.state == 1).\
        order_by(Article.timestamp.desc()). \
        paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)
    # articles = Article.query.join(article_tag,tag_id==tag.id). \
    #     filter(article_tag.article_id==Article.id,Article.state == 1). \
    #     order_by(Article.timestamp.desc).\
    #     paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)
    
    # articles = Article.query.join(TagSpaces, TagSpaces.tag_id == tag.id).filter(TagSpaces.article_id == Article.id,Article.state == 1 ). \
    #     order_by(Article.timestamp.desc()). \
    #     paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)

    return render_template('tag.html', articles=articles, tag=tag,orderby='time')

@main.route('/tag/<t>/hot/', methods=['GET'])
def tag_hot(t):
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.filter_by(name=t).first()
    articles = tag.articles.filter(Article.state == 1).\
        order_by(Article.vc.desc()). \
        paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)
    return render_template('tag.html', articles=articles, tag=tag,orderby='hot')


@main.route('/category/<c>/', methods=['GET', 'POST'])
def category(c):
    """
    文章分类列表
    """
    page = request.args.get('page', 1, type=int)
    cty = Category.query.filter_by(name=c).first()
    articles = Article.query.filter_by(category=cty,state=1).order_by(Article.timestamp.desc()). \
        paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)

    return render_template('category.html', articles=articles, category=cty,orderby='time')

@main.route('/category/<c>/hot/', methods=['GET', 'POST'])
def category_hot(c):
    page = request.args.get('page', 1, type=int)
    cty = Category.query.filter_by(name=c).first()
    articles = Article.query.filter_by(category=cty,state=1).order_by(Article.vc.desc()). \
        paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)

    return render_template('category.html', articles=articles, category=cty,orderby='hot')

@main.route('/archive/',methods=['GET'])
def archive():
    """
    根据时间归档
    """
    articles = Article.query.filter_by(state=1).order_by(Article.timestamp.desc()).all()
    time_tag = []
    current_tag = ''
    for a in articles:
        a_t = a.timestamp.strftime('%Y-%m')
        if  a_t != current_tag:
            tag = dict()
            tag['name'] = a_t
            tag['articles'] = []
            time_tag.append(tag)
            current_tag = a_t
        tag = time_tag[-1]
        tag['articles'].append(a)
    return render_template('archives.html',time_tag = time_tag)

@main.route('/search/', methods=['GET', 'POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('.index'))

    return redirect(url_for('.search_results', query=g.search_form.search.data.strip()))


@main.route('/search_results/<query>', methods=['GET', 'POST'])
def search_results(query):
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter(Article.body.like('%%%s%%' % query)).order_by(Article.timestamp.desc()). \
        paginate(page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)
    return render_template('search_result.html', articles=articles, query=query)

@sitemap.register_generator
def sitemap():
    """
    sitemap生成
    """
    articles = Article.query.all()
    categories = Category.query.all()
    tags = Tag.query.all()
    import datetime
    now = datetime.datetime.now()
    yield 'main.index',{},now.strftime('%Y-%m-%dT%H:%M:%S'),'always',1.0
    yield 'main.about',{},now.strftime('%Y-%m-%dT%H:%M:%S'),'always',0.5
    for category in categories:
        yield 'main.category',{'c':category.name},now.strftime('%Y-%m-%dT%H:%M:%S'),'always',0.9
    for categories in categories:
        yield 'main.category_hot',{'c':category.name},now.strftime('%Y-%m-%dT%H:%M:%S'),'always',0.9

    for t in tags:
        yield 'main.tag',{'t':t.name},now.strftime('%Y-%m-%dT%H:%M:%S'),'always',0.9
    for t in tags:
        yield 'main.tag_hot',{'t':t.name},now.strftime('%Y-%m-%dT%H:%M:%S'),'always',0.9

    for a in articles:
        #posts.post是文章视图的endpoint,后面是其参数
        yield 'main.article',{'name':a.name}

@main.route('/robots.txt')
def robots():
    return send_from_directory(main.static_folder,'robots.txt')