import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    # Create and configure the app.
    app = Flask(__name__, instance_relative_config=True)

    # Load the instance config, if it exists.
    app.config.from_pyfile('config.py', silent=True)

    # Ensure the instance folder exists.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Setup db and migrations.
    db.init_app(app)
    migrate.init_app(app, db)
    from invest.models import tables

    # Setup login manager
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Home.
    @app.route('/')
    def index():
        return render_template('index.html')

    # Register blueprints.
    from invest.controllers import auth, restricted
    app.register_blueprint(auth.bp)
    app.register_blueprint(restricted.bp)

    # Setup shell.
    from invest.models.tables import User

    @app.shell_context_processor
    def make_shell():
        return dict(
            app=app,
            db=db,
            User=User
        )

    return app
