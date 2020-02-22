from flask import Blueprint

main = Blueprint('main', __name__, template_folder="themes/tend", static_url_path='',
				 static_folder='themes/tend/static')

# 在末尾导入相关模块，是为了避免循环导入依赖，因为在下面的模块中还要导入蓝本main
from . import views, errors
