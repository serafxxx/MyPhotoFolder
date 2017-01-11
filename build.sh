#!/bin/bash

if [ ! `basename "$PWD"` == 'MyPhotoFolder' ]; then
        echo "Please run me from MyPhotoFolder folder"
        exit 0
fi


if [ ! -d "mpf.ve" ]; then
        echo "Creating virtualenv"
        virtualenv "mpf.ve"
fi


source mpf.ve/bin/activate
pip install -r requirements.txt