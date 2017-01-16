#!/bin/bash

if [ ! `basename "$PWD"` == 'MyPhotoFolder' ]; then
        echo "Please run me from MyPhotoFolder folder"
        exit 0
fi


if [ ! -d "mpf.ve" ]; then
        echo "Creating virtualenv"
        virtualenv "mpf.ve"
fi


git pull

source mpf.ve/bin/activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head