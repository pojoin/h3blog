from flask_login import current_user
from flask import url_for, request 
import re

def register_template_filter(app):
    '''注册模板过滤器'''

    @app.template_filter('hidden_content')
    def hidden_content(content):
        if current_user.is_authenticated:
            return content.replace('[h3_hidden]','').replace('[/h3_hidden]','')
        else:
            login_url = url_for('main.login') + '?next=' + request.path
            repl = '''
            <p class="border border-warning p-2 text-center">
            本文隐藏内容 <a href="{}">登陆</a> 后才可以浏览
            </p>
            '''.format(login_url)
            return re.sub('\[h3_hidden\].*?\[/h3_hidden\]',repl,content,flags=re.DOTALL)


if __name__ == '__main__':
    content = '''
    我是中国人1
    我是中国人2
    我是中国人3
    [hidden]
    我是中国人4
    我是中国人5
    [/hidden]
    '''
    m_tr =  re.findall('\[hidden\].*?\[/hidden\]',content,re.DOTALL)
    print(m_tr)
    m_tr = re.sub('\[hidden\].*?\[/hidden\]','我爱你',content,flags=re.DOTALL)
    print(m_tr)