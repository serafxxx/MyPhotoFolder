import subprocess
from models import app


def get_preview(video_file_path):
    """Get preview from video file with ffmpeg and return it as string"""

    cmd = [app.config['FFMPEG_BIN'],
           # Suppress info messages
           '-v', 'fatal',
           # Seek to second 2
           # '-ss', '2',
           # Input file
           '-i', video_file_path,
           # Process only one frame
           '-vframes', '1',
           # Output format
           '-f', 'image2pipe',
           # Push result to the stdout
           '-']

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    # Read output
    data = b''
    for line in iter(proc.stdout.readline, ""):
        data += line

    return data.strip()

def mp4_generator(video_file_path):
    cmd = [app.config['FFMPEG_BIN'],
           # Suppress info messages
           # '-v', 'fatal',
           # Seek to second 2
           # '-ss', '0',
           # Input file
           '-i', video_file_path,

           # '-qscale', '0',
           '-c:v', 'libx264',
           '-c:a', 'aac',




           # Output format
           '-f', 'mpegts',
           # Push result to the stdout
           '-']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    try:
        f = proc.stdout
        byte = f.read(8192)
        while byte:
            yield byte
            byte = f.read(8192)
    finally:
        proc.kill()