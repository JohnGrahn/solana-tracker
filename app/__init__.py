from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from celery import Celery
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
migrate = Migrate()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app, db)
    celery.conf.update(app.config)

    from app import routes
    app.register_blueprint(routes.bp)

    from app.models import User, init_app as init_models
    init_models(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'main.login'

    return app
