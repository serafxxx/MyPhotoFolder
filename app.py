import os
import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from config import config
from config_logging import LOGGING
# from util.myfiles import import_media
from util import mkdir_p
from logging import config as logging_config

app = Flask(__name__)
app.config.from_object(config)
log = app.logger
logging_config.dictConfig(LOGGING)

Bootstrap(app)

db = SQLAlchemy(app, session_options={'autocommit': False, 'autoflush': False} )

mkdir_p(app.config['MPF_PATH'])

if not os.path.isfile(app.config['DATABASE_PATH']):
    db.create_all()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

@app.cli.command()
@click.option('--from-path', help='Path to get media files from')
def copy_media(from_path):
    '''Console command for import media from given path
    Usage example:
    $ flask copy_media --from-path "/path/to/folder"
    '''
    from util.myfiles import import_media

    if not os.path.exists(from_path):
        log.warning('Not existent folder: %s' % from_path)
        return
    log.debug('Importing from %s' % from_path)
    imprt = import_media(from_path)

