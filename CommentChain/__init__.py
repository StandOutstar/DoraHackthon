# -*- coding: UTF-8 -*-

# Description: application
#      Author: zhangxingkui
#    Datetime: 2019-07-20 07:27
import os

from flask import Flask, render_template, g


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    @app.route('/')
    def index():
        if g.user:
            return render_template("home.html", user={"username": g.user["username"]})
        return render_template('auth/login.html')

    @app.route('/home')
    def home():
        return render_template('home.html')

    from . import auth
    from . import comment
    from . import goods
    app.register_blueprint(auth.bp)
    app.register_blueprint(comment.bp)
    app.register_blueprint(goods.bp)

    return app
