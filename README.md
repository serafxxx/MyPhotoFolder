# My Photo Folder
A simple service to run on your home server to keep your family photos
and videos organized and in good mood.

## The idea
You probably already have a folder (probably a shared one) where all your
media files go. It worked well in old times when you have to copy photos
from your camera. But everything got more complicated when mobile devices
came into play and its now really hard to keep all media accessible from
one place and organized.

MPF will help to perform 2 things: it will copy your photos/videos
to the folder where you'd like all files to be and it will populate it
via web service to your local network.

## How it works
1. To install clone repo and run `build.sh`
```
$ git clone https://github.com/serafxxx/MyPhotoFolder.git
$ cd MyPhotoFolder
$ ./buid.sh
```
2. Set `MPF_PHOTOS_PATH` env variable to point to the folder with your files.
The folder could already have your collection of home photos/videos, it will
stay on its place. MPF wouldn't move any files from/inside `MPF_PHOTOS_PATH` folder.

3. To add new files to your folder run import. MPF will copy files to `autoimport`
folder inside `MPF_PHOTOS_PATH` (`autoimport` folder will have structure based on dates)

```
$ flask copy_media --from-path="/path/to/new/files"
```

4. Another way is to put your files inside `MPF_PHOTOS_PATH` manually in any subdirectory
you like and run import from `MPF_PHOTOS_PATH` itself. MPF will scan your folder, ignore
old files and analyse new files. In this way new files would be available through the
web interface.

```
$ flask analyze_lib
```