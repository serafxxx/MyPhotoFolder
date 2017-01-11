import StringIO
import hashlib
import os
import re
import shutil
from datetime import datetime

import pytz
from PIL import Image

from app import app, db, log
from util import hashfile, maybe_add_number_to_file_name, mkdir_p, crop_rect
from util.exiftool import ExifTool
from util.my_exceptions import MyException


TYPE_NONE = None
TYPE_PHOTO = '1'
TYPE_RAW = '2'
TYPE_VIDEO = '3'

FILE_TYPES = [TYPE_PHOTO, TYPE_RAW, TYPE_VIDEO]
FILE_TYPE_NAMES = {
    TYPE_NONE: 'none',
    TYPE_PHOTO: 'photo',
    TYPE_RAW: 'raw',
    TYPE_VIDEO: 'video'
}

EXTENSION_FILE_TYPE = {
    'jpg': TYPE_PHOTO,
    'thm': TYPE_PHOTO,
    'cr2': TYPE_RAW,
    'mp4': TYPE_VIDEO,
    'mov': TYPE_VIDEO,
    'lrv': TYPE_VIDEO
}

class MyFile(db.Model):
    __tablename__ = 'myfiles'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(*FILE_TYPES), default=None)
    imported_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    created_date = db.Column(db.DateTime(timezone=True), doc='Date from file metadata')
    hash = db.Column(db.String(64), index=True, unique=True, nullable=False, doc='Unique file identifier')
    path = db.Column(db.String(512), doc='File path')
    imported_from_path = db.Column(db.String(512), doc='File path as was before import, for history')
    imprt_id = db.Column(db.Integer, db.ForeignKey('imprts.id'), doc='All files from one import have same imprt object')
    imprt = db.relationship('Imprt', backref=db.backref('myfiles', lazy='dynamic', cascade='all'))

    _thumb = db.Column(db.String(512), doc='Thumb path')
    _preview = db.Column(db.String(512), doc='Preview path')
    is_system = db.Column(db.Boolean, default=False, doc='If file needs to be hidden')

    def start_exiftool(function):
        '''Decorator to use for MyFile methods.
        It ensures that ExifTool instance is running. Use it for all methods where ExifTool is using.
        '''
        def wrapper(self, *args, **kw):

            if not hasattr(self, '_exiftool') or not self._exiftool:
                # Make an instance of ExifTool
                self._exiftool = ExifTool(executable_=app.config['EXIFTOOL_PATH'])

            if not self._exiftool.running:
                self._exiftool.start()
                ret = function(self, *args, **kw)
                self._exiftool.terminate()
            else:
                ret = function(self, *args, **kw)
            return ret
        return wrapper

    def set_exiftool(self, exiftool):
        self._exiftool = exiftool

    def __str__(self):
        return 'File t=%s (%s) %s %s' % (FILE_TYPE_NAMES[self.type], self.created_date, self.path, self.hash)

    @start_exiftool
    def get_date(self):
        # EXIF_DateTimeOriginal = self._exiftool.get_tag('EXIF:DateTimeOriginal', self.path)
        create_date = self._exiftool.get_tag('CreateDate', self.path)
        if create_date:
            date = datetime.strptime(create_date, '%Y:%m:%d %H:%M:%S')
            if self.type == TYPE_VIDEO:
                # Video files usually stores UTC time
                utc_date = pytz.utc.localize(date)
            else:
                # All other types should store local time
                tz = pytz.timezone(app.config['TIME_ZONE'])
                local_date = tz.localize(date)
                utc_date = local_date.astimezone(pytz.utc)
            return utc_date
        return None

    def hashfile(self):
        with open(self.path, 'rb') as f:
            return hashfile(f, hashlib.sha256())

    def is_duplicate(self):
        if not self.hash:
            raise MyException('File do not have hash. Fail to decide if its duplicate.')
        if MyFile.query.filter_by(hash=self.hash).count():
            return True
        return False

    def copy_to_lib(self):
        '''
        Will generate target path where to place file, copy file,
        change self.path and self.imported_from.
        If file situated inside media library - it will stay on its place.
        '''
        if self.path.startswith(app.config['PHOTOS_PATH']):
            self.imported_from_path = self.path
            return

        if self.created_date:
            # We have date when file was created. Lets put it into the date folders structure
            subfolders = self.created_date.strftime('%Y/%m-%b/%d')
        else:
            # File with no creation date. Put it to import_date folder
            subfolders = repr(self.imprt)

        target_folder_path = os.path.join(app.config['AUTOIMPORT_PATH'], subfolders)
        old_folder_path, file_name = os.path.split(self.path)
        target_path = os.path.join(target_folder_path, file_name)
        target_path = maybe_add_number_to_file_name(target_path)
        mkdir_p(target_folder_path)

        shutil.copy(self.path, target_path)
        self.imported_from_path = self.path
        self.path = target_path

    @property
    def dcim_number(self):
        '''Integer found in file name'''
        head, file_name = os.path.split(self.path)
        match = re.match('.*?([0-9]+)\.[a-zA-Z]+', file_name)
        if match:
            return match.group(1)
        return 0

    @property
    def thumb(self):
        if not self._thumb or not os.path.isfile(self._thumb):
            try:
                self.gen_thumbs()
            except MyException as e:
                log.exception(e)
        return self._thumb

    @property
    def preview(self):
        if not self._preview or not os.path.isfile(self._preview):
            try:
                self.gen_thumbs()
            except MyException as e:
                log.exception(e)
        return self._preview

    def del_thumbs(self):
        ''' Remove generated images. '''
        if self._thumb and os.path.isfile(self._thumb):
            os.remove(self._thumb)
            self._thumb = ''
        if self._preview and os.path.isfile(self._preview):
            os.remove(self._preview)
            self._preview = ''

    # def gen_preview(self):
    #     raise NotImplementedError

    def gen_cache_path(self):
        '''
        Generate file name based on MyFile path and CACHE_PATH.
        It will be the same file_name as original file but with
        path in cache dir.
        '''
        if not os.path.isfile(self.path):
            raise MyException('MyFile.path is not a file')

        file_path_relative_to_lib = os.path.relpath(self.path, app.config['PHOTOS_PATH'])
        return os.path.join(app.config['CACHE_PATH'], file_path_relative_to_lib)

    @property
    @start_exiftool
    def metadt(self):
        if self.path and os.path.isfile(self.path):
            with self._exiftool as et:
                return et.get_metadata(self.path)
        return None

    def get_pil_im(self):
        if self.type == TYPE_PHOTO:
            return Image.open(self.path)
        elif self.type == TYPE_RAW:
            im_data = self._exiftool.execute('-b', '-PreviewImage', self.path)
            return Image.open(StringIO.StringIO(im_data))
        else:
            log.warning('get_pil_im is not emplemented for %s' % self)

    @start_exiftool
    def gen_thumbs(self):
        '''
        Remove old thumb and make new one.
        '''
        self.del_thumbs()

        if self.path and os.path.isfile(self.path):
            # Make a name for the thumbs
            preview_path = self.gen_cache_path() + '.preview.jpg'
            thumb_path = self.gen_cache_path() + '.thumb.jpg'

            # Be sure directories are created
            mkdir_p(os.path.dirname(thumb_path))

            im = self.get_pil_im()

            if not im:
                return

            try:
                # Fix EXIF orientation
                EXIF_Orientation = self._exiftool.get_tag('EXIF:Orientation', self.path)
                if EXIF_Orientation:
                    if EXIF_Orientation == 3:
                        im = im.rotate(180, expand=True)
                    elif EXIF_Orientation == 6:
                        im = im.rotate(270, expand=True)
                    elif EXIF_Orientation == 8:
                        im = im.rotate(90, expand=True)
            except:
                pass

            # Generate preview
            im.thumbnail(app.config['PREVIEW_SIZE'], Image.ANTIALIAS)
            im.save(preview_path)
            self._preview = preview_path

            # From preview make thumb
            im = crop_rect(im)
            im.thumbnail(app.config['THUMB_SIZE'], Image.ANTIALIAS)
            im.save(thumb_path)
            self._thumb = thumb_path


class Imprt(db.Model):
    '''
    Model to store list of files imported at once
    '''
    __tablename__ = 'imprts'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    def count_files(self):
        return self.myfiles.count()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        # Affects library folder structure
        return 'import_%i-%s' % (self.id, self.date.strftime('%Y.%m.%d'))