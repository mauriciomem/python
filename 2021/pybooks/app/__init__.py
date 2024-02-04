from flask import Flask, session
from flask_moment import Moment
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

db = SQLAlchemy()
se = Session()

def new_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    se.init_app(app)
    db.init_app(app)
    moment = Moment(app)

    with app.app_context():
        from . import routes, models
        db.create_all()
    
        return app