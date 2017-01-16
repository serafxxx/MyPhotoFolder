import os
import click
from flask import Blueprint
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from config import config
from config_logging import LOGGING
# from util.myfiles import import_media
from util import mkdir_p
from logging import config as logging_config

app = Flask(__name__)
# Apply configuration
app.config.from_object(config)
# Setup logger
log = app.logger
logging_config.dictConfig(LOGGING)

# Setup twitter bootstrap
Bootstrap(app)

# Setup database. Don't forget to run migrations
# manually to setup db from the ground.
db = SQLAlchemy(app, session_options={'autocommit': False, 'autoflush': False} )
mkdir_p(app.config['MPF_PATH'])
if not os.path.isfile(app.config['DATABASE_PATH']):
    db.create_all()

# Register blueprint to serve our photos folder as static files
photos_blueprint = Blueprint('photos', __name__, static_url_path='/static/photos', static_folder=app.config['PHOTOS_PATH'])
app.register_blueprint(photos_blueprint)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

@app.cli.command()
@click.option('--from-path', help='Path to new media files')
def copy_media(from_path):
    '''Console command for import media from given path
    Usage example:
    $ flask copy_media --from-path "/path/to/new/files"
    '''
    from util.myfiles import import_media

    if not os.path.exists(from_path):
        log.warning('Not existent folder: %s' % from_path)
        return
    log.debug('Importing from %s' % from_path)
    imprt = import_media(from_path)


@app.cli.command()
def analyze_lib():
    '''Console command for analyze new media in the PHOTOS_PATH
    Usage example:
    $ flask analyze-lib
    '''
    from util.myfiles import import_media
    log.debug('Importing from %s' % app.config['PHOTOS_PATH'])
    imprt = import_media(app.config['PHOTOS_PATH'])