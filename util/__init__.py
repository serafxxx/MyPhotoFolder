import os
import subprocess
import errno


def match_at_least_one(s, regexp_list):
    """
    Go through the list of regexps and return True on the first match
    :param s: Search string
    :param regexp_list: List of regexps to try
    """
    for regexp in regexp_list:
        if regexp.match(s):
            return True
    return False


def hashfile(afile, hasher, blocksize=65536):
    """Make a hash number for given file"""
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


def maybe_add_number_to_file_name(file_path):
    """Add number to the file name if there is already file with such name
    :param file_path: File path with extension (/path/to/file.ext)
    """

    if not os.path.isfile(file_path):
        return file_path

    folder_path, file_name = os.path.split(file_path)

    splitted = file_name.split('.')
    file_name_wo_ext = '.'.join(splitted[:-1])
    file_ext = splitted[-1]
    counter = 1
    new_file_name_tpl = '%s-%i.%s'
    new_file_name = new_file_name_tpl % (file_name_wo_ext, counter, file_ext)
    new_file_path = os.path.join(folder_path, new_file_name)
    while os.path.isfile(new_file_path):
        counter += 1
        new_file_name = new_file_name_tpl % (file_name_wo_ext, counter, file_ext)
        new_file_path = os.path.join(folder_path, new_file_name)

    return new_file_path


def mkdir_p(path):
    """Recursivly create missing folders in path"""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise Exception('Failed to create path %s' % path)


def call(cmd, *args):
    """Make a simple subprocess call"""

    # BASE_PATH = os.path.abspath(os.path.dirname(__file__))
    # path = functools.partial(os.path.join, BASE_PATH)
    cmd_list = [cmd] + list(args)
    proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
    proc.wait()
    lines = [line.strip() for line in proc.stdout.readlines() if line != '\n']
    return lines


def crop_rect(im):
    '''Crop image to rectangular size'''
    x, y = im.size
    size = x if x <= y else y
    x_padding = (x - size) / 2
    y_padding = (y - size) / 2
    return im.crop((x_padding, y_padding, x - x_padding, y - y_padding))
