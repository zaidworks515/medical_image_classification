import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.engine.url import make_url
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_database_if_not_exists(app):
    db_url = make_url(app.config["SQLALCHEMY_DATABASE_URI"])
    conn = pymysql.connect(
        host=db_url.host,
        user=db_url.username,
        password=db_url.password,
        port=db_url.port or 3306,
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_url.database}")
    cursor.close()
    conn.close()


def create_app():
    app = Flask(__name__, static_url_path="/local", static_folder="../static")
    app.config.from_object(Config)

    create_database_if_not_exists(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    with app.app_context():
        db.create_all()

    from app.routes import routes

    app.register_blueprint(routes)

    return app
