import os
from datetime import datetime
import pytz

from util import match_at_least_one
from util.exiftool import ExifTool

from models import app, db, log, MyFile, Imprt, EXTENSION_FILE_TYPE


def restore_dates_by_dcim_number(myfiles):
    '''
    Will sort files by number and suggest
    created date for those who miss it.
    Will change objects inplace
    '''
    sorted_by_dcim = sorted(myfiles, key=lambda f: f.dcim_number)

    # Initial date (in case all files in import wouldn't have created_date
    date = datetime.now(tz=pytz.utc)

    for myfile in sorted_by_dcim:
        if not myfile.created_date:
            # Set suggested date
            myfile.created_date = date
        else:
            # Update date. So file with no created date will
            # have same created date as previous file in list
            date = myfile.created_date


# def process_livephotos(myfiles):
#     '''
#     Go through the list and try to find pairs of photo-video files which
#     forms LivePhoto introduced by Apple.
#     Live Photo consists of photo file and video file with same name (minus extension)
#     and same date.
#     '''
#
#     for file in myfiles:
#         file_path_no_ext = ''.join(file.path.split('.')[:-1])
#         print file_path_no_ext


def import_media(from_path):

    imported_files = []
    imported_hashes = []
    unknown_files = []
    ignored_files = []
    duplicate_files = []

    imprt = Imprt()
    db.session.add(imprt)
    db.session.commit()

    counter_total = 0

    # Make an instance of ExifTool for batch file processing
    exiftool = ExifTool(executable_=app.config['EXIFTOOL_PATH'])
    exiftool.start()

    try:
        for root, dirs, files in os.walk(from_path):
            for file_name in files:
                counter_total += 1
                file_path = os.path.join(root, file_name)
                if file_path.startswith(app.config['MPF_PATH']):
                    # Do not import files from system folder
                    continue

                if match_at_least_one(file_name, app.config['IGNORE_FILE_PATTERNS']) \
                        or '.' not in file_name:
                    # Ignore file
                    f = MyFile(path=file_path)
                    ignored_files.append(f)
                    log.debug('Ignoring file: %s' % f)
                else:
                    extension = file_name.split('.')[-1].lower()
                    if extension in EXTENSION_FILE_TYPE:
                        # If extension matched

                        file_type = EXTENSION_FILE_TYPE[extension]

                        # File instance
                        f = MyFile(type=file_type, path=file_path)
                        # Pass running ExifTool instance into the object
                        f.set_exiftool(exiftool)
                        f.created_date = f.get_date()
                        f.hash = f.hashfile()

                        log.debug('Found: %s' % f)

                        # Check for duplicates in db and in current import
                        if not f.is_duplicate() and f.hash not in imported_hashes:
                            # f.copy_to_lib()
                            # f.save()
                            imported_files.append(f)
                            imported_hashes.append(f.hash)
                        else:
                            duplicate_files.append(f)
                            log.debug('Skipping duplicate: %s' % f)
                    else:
                        # Unknown file type
                        f = MyFile(path=file_path)
                        unknown_files.append(f)
                        log.warning('Unknown file: %s' % f)

        # Try to restore missed dates
        restore_dates_by_dcim_number(imported_files)

        # Move files to the lib
        for f in imported_files:
            # Bind imprt to current Imprt. Can do it only here because `f` would be added to the session automatically base on cascades.
            # So no need to add `f` to session manually
            f.imprt = imprt
            f.copy_to_lib()
            log.debug('Imported: %s' % f)
        db.session.commit()

        log.info(
            '%s Total:%i, Imported:%i, Unknown:%i, Duplicates:%i, Ignored:%i' %
            (str(imprt), counter_total, len(imported_files), len(unknown_files), len(duplicate_files), len(ignored_files))
        )

        log.info('Generating thumbnails...')
        for f in imported_files:
            try:
                f.gen_thumbs()
                db.session.add(f)
            except Exception as e:
                log.exception(e)

        db.session.commit()

        if not imprt.count_files():
            # If nothing was imported remove imprt object
            db.session.delete(imprt)
            db.session.commit()
            return None
        return imprt

    finally:
        exiftool.terminate()
