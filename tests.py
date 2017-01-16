import shutil

import config
from util import mkdir_p

config.config = config.Testing

import os
import unittest

from models import app, db, log, TYPE_VIDEO, MyFile
from util.myfiles import import_media


class MPFTestCase(unittest.TestCase):
    def setUp(self):
        if os.path.isfile(app.config['DATABASE_PATH']):
            os.unlink(app.config['DATABASE_PATH'])
        if os.path.isdir(app.config['PHOTOS_PATH']):
            shutil.rmtree(app.config['PHOTOS_PATH'])
            mkdir_p(app.config['MPF_PATH'])

        db.drop_all()
        db.create_all()

    def tearDown(self):
        # db.drop_all()
        # os.unlink(app.config['DATABASE_PATH'])
        pass

    def testImportMedia(self):
        imprt = import_media(from_path=app.config['IMPORT_FROM_PATH'])
        log.info('%i files imported' % imprt.myfiles.count())

        # We have 24 different files for import
        self.assertEqual(imprt.myfiles.count(), 24)

        # Run import again
        imprt = import_media(from_path=app.config['IMPORT_FROM_PATH'])
        # Nothing should be imported
        self.assertIsNone(imprt)


if __name__ == '__main__':
    unittest.main()
