from flask import Flask, g
from werkzeug.utils import find_modules, import_string
import os
from .latexcreator.mainsite.views import *
def create_app(config=None):
    app = Flask('latexcreator')
    
    app = Flask(__name__.split('.')[0])

    app.config.update(dict(
        DATABASE=os.path.join(app.root_path, 'latexcreator.db'),
        DEBUG=True,
        SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
        USERNAME='admin',
        PASSWORD='nw!TjJc}c9&,A6d!'
    ))
    app.config.update(config or {})
    
    from latexcreator.latexcreator.pdfcreator.views import api
    api.init_app(app)
    # register_cli(app)
    # register_teardowns(app)
    register_blueprints(app)
    return app


def register_blueprints(app):
    """Register all blueprint modules

    Reference: Armin Ronacher, "Flask for Fun and for Profit" PyBay 2016.
    """
    
    for name in find_modules('latexcreator.latexcreator.mainsite'):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)
    return None


# def register_cli(app):
    # @app.cli.command('initdb')
    # def initdb_command():
        # """Creates the database tables."""
        # init_db()
        # print('Initialized the database.')


# def register_teardowns(app):
    # @app.teardown_appcontext
    # def close_db(error):
        # """Closes the database again at the end of the request."""
        # if hasattr(g, 'sqlite_db'):
            # g.sqlite_db.close()
app = create_app()
