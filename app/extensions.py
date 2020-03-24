
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_sitemap import Sitemap
from flask_login import LoginManager
from flask_migrate import Migrate


class AppHelper(object):
    def init_app(self, app, db=None, directory=None, **kwargs):
        self.app = app
        
db = SQLAlchemy()
sitemap = Sitemap()
login_manager = LoginManager()
migrate = Migrate()
app_helper = AppHelper()



@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

login_manager.session_protection = 'strong'
login_manager.login_view = 'admin.login'
# login_manager.login_message = 'Your custom message'
login_manager.login_message_category = 'warning'
