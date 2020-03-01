from flask import request,current_app
from flask import abort
from flask_login import current_user
from functools import wraps
import requests
import json
import logging
import re

def admin_required(func):
    """ 检查管理员权限 """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin():
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator(func)


def author_required(func):
    """ 检查作者权限 """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_author():
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator(func)

def isAjax() -> bool :
    '''
    判断是否是ajax请求
    '''
    ajax_header = request.headers.get('X-Requested-With')
    if ajax_header and ajax_header == 'XMLHttpRequest':
        return True
    return False

def upload_file_qiniu(inputdata,filename=None):
    from qiniu import Auth, put_data, etag
    access_key = current_app.config.get('QINIU_ACCESS_KEY')
    secret_key = current_app.config.get('QINIU_SECRET_KEY')
    '''
    :param inputdata: bytes类型的数据
    :return: 文件在七牛的上传名字
    '''
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'h3blog'

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name)
    #如果需要对上传的图片命名，就把第二个参数改为需要的名字
    ret1,ret2=put_data(token,filename,data=inputdata)
    print('ret1:',ret1)
    print('ret2:',ret2)

    #判断是否上传成功
    if ret2.status_code!=200:
        raise Exception('文件上传失败')

    return ret1.get('key')

def file_list_qiniu():
    from qiniu import Auth, BucketManager
    access_key = current_app.config.get('QINIU_ACCESS_KEY')
    secret_key = current_app.config.get('QINIU_SECRET_KEY')
    cdn = current_app.config.get('QINIU_CDN_URL')
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)
    bucket_name = 'h3blog'
    # 前缀
    prefix = None
    # 列举条目
    limit = 100
    # 列举出除'/'的所有文件以及以'/'为分隔的所有前缀
    delimiter = None
    # 标记
    marker = None
    ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
    # print(info)
    # assert len(ret.get('items')) is not None
    items = ret.get('items')
    return [ {'key':item['key'],'url': cdn + item['key']} for item in items]

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['H3BLOG_ALLOWED_IMAGE_EXTENSIONS']


def baidu_push_urls(domain,urls):
    """
    主动推送给百度
    """
    headers = {'Content-Type':'text/plain'}
    url = 'http://data.zz.baidu.com/urls?site={}&token={}'. \
        format(domain,current_app.config.get('BAIDU_PUSH_TOKEN'))
    try:
        ret = requests.post(url, headers = headers, data = urls, timeout = 3).text
        return json.loads(ret)
    except Exception as e :
        logging.error(e)
        return {'success':0,'msg':'超时错误'}

def strip_tags(string, allowed_tags=''):
    """
    去除html标签
    """
    if allowed_tags != '':
        # Get a list of all allowed tag names.
        allowed_tags = allowed_tags.split(',')
        allowed_tags_pattern = ['</?'+allowed_tag+'[^>]*>' for allowed_tag in allowed_tags]
        all_tags = re.findall(r'<[^>]+>', string, re.I)
        not_allowed_tags = []
        tmp = 0
        for tag in all_tags:
            for pattern in allowed_tags_pattern:
                rs = re.match(pattern,tag)
                if rs:
                    tmp += 1
                else:
                    tmp += 0
            if not tmp:
                not_allowed_tags.append(tag)
            tmp = 0
        for not_allowed_tag in not_allowed_tags:
            string = re.sub(re.escape(not_allowed_tag), '',string)
        print(not_allowed_tags)
    else:
        # If no allowed tags, remove all.
        string = re.sub(r'<[^>]*?>', '', string)
  
    return string