import os
import re

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class Config(object):
    DEBUG = True
    TESTING = False

    """
    PHOTOS_PATH is a folder where all media files will go. Its fine if
    there is some sub-folder structure with files in it.
    I bet you already have something similar (a folder where you keep
    all your photo and video files), so feel free to set it here.

    Structure
    1. Could include any folders with any files, it wouldn't
    affect library processing. So you can keep any folder
    structure you like. MPF will never move your files inside library.
    I bet you already have a folder with your photos and videos. You can
    point PHOTOS_PATH to that folder and it will work. Nothing will change
    inside your folder (except maybe one hidden folder for caching would be
    created).
    2. You can add new files to PHOTOS_PATH folder manually and run import.
    MPF will scan PHOTOS_PATH by default and new files would be available from
    web interface.
    3. MPF will use AUTOIMPORT_PATH to store automatically imported
    files. It will make AUTOIMPORT/yyyy/mm-MMM/dd/ folders structure and use it
    to store automatically imported media files (those with date). Automatically
    imported media files which do not have date inside, will go to
    AUTOIMPORT/import_yyyy_mm-MMM_dd folder. Also MML will try to guess file date
    based on its name when possible.
    """
    # MEDIA_LIB = u'/var/raid/Media/Photo'
    PHOTOS_PATH = '/var/raid/Projects/MyMediaLib/test_files/test_lib'

    """
    MPF_PATH is where system related things are stored.
    """
    MPF_PATH = os.path.join(PHOTOS_PATH, '.mpf')

    """
    Path to store generated thumbs. No need to back it up.
    You're making backups, aren't you??
    """
    CACHE_PATH = os.path.join(MPF_PATH, 'cache')

    """
    Exiftool executable path ( http://www.sno.phy.queensu.ca/~phil/exiftool/ )
    Used to get EXIF data from media files
    """
    EXIFTOOL_PATH = os.path.join(ROOT_PATH, 'util/Image-ExifTool-10.33/exiftool')

    """
    MPF wouldn'd import files which match any of IGNORE_FILE_PATTERNS
    """
    IGNORE_FILE_PATTERNS = (
        re.compile('^(\._)?\.DS_Store$', flags=re.IGNORECASE),
        re.compile('^\..*', flags=re.IGNORECASE)
    )

    """
    Thumbs size
    """
    THUMB_SIZE = (128, 128)

    """
    Previews size
    """
    PREVIEW_SIZE = (2560, 1600)

    """
    Exif data do not store timezones. Will use TIME_ZONE instead.
    """
    TIME_ZONE = 'Europe/Moscow'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Testing(Config):
    TESTING = True
    PHOTOS_PATH = os.path.join(ROOT_PATH, 'tests_data/photos')
    IMPORT_FROM_PATH = os.path.join(ROOT_PATH, 'tests_data/files_for_import')
    AUTOIMPORT_PATH = os.path.join(PHOTOS_PATH, 'autoimport')
    MPF_PATH = os.path.join(PHOTOS_PATH, '.mpf')
    CACHE_PATH = os.path.join(MPF_PATH, 'cache')
    DATABASE_PATH =  '%s/testing.sqlite' % MPF_PATH
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % DATABASE_PATH


class Production(Config):
    PHOTOS_PATH = os.path.join(ROOT_PATH, 'data/photos')
    AUTOIMPORT_PATH = os.path.join(PHOTOS_PATH, 'autoimport')
    MPF_PATH = os.path.join(PHOTOS_PATH, '.mpf')
    CACHE_PATH = os.path.join(MPF_PATH, 'cache')
    DATABASE_PATH = '%s/data.sqlite' % MPF_PATH
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % DATABASE_PATH


configs = {
    'production': Production,
    'testing': Testing,
    'default': Production
}

config_name = os.environ.get('MPF_CONFIG') or 'default'
config = configs.get(config_name) or configs.get('default')
