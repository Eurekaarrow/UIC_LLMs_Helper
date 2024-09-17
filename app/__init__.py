from flask import Flask
from flask_mail import Mail
from app.controller import user
from app.controller import HelpTopic
from app.controller import course, test, Request, AssignQ
import base64


mail = Mail()

def register_blueprints(app):
    app.register_blueprint(user.userBP, url_prefix='/user')
    app.register_blueprint(HelpTopic.HelpTopicBP, url_prefix='/')
    app.register_blueprint(course.courseBP, url_prefix='/')
    app.register_blueprint(test.testBP, url_prefix='/')
    app.register_blueprint(Request.RequestBP, url_prefix='/')
    app.register_blueprint(AssignQ.AssignQBP, url_prefix='/')

def register_plugin(app):
    from app.models.base import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

def b64encode_filter(value):
    """Encode binary data to base64 string."""
    return base64.b64encode(value).decode('utf-8') if value else ''


def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object('app.config.secure')  # 加载配置

    app.config['SECRET_KEY'] = 'ssfwer32'
    app.config['MAIL_SERVER'] = 'smtp.163.com'
    app.config['MAIL_PORT'] = 25
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'eureka_gyc@163.com'
    app.config['MAIL_PASSWORD'] = 'BYXPCBCQCGVVAJPT'  # 授权码

    mail.init_app(app)  # 初始化 Mail 对象与 app 关联

    app.jinja_env.filters['b64encode'] = b64encode_filter

    register_blueprints(app)

    register_plugin(app)

    return app
