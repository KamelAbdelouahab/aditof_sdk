#!/bin/bash

#This script can be used to rebuild the SDK depending on various platforms and cameras.
#Its purpose is to be called from a shortcut placed on desktop.
#It expects the parameters passed as the CMAKE command.

#Possible build flag for the camera: -DUSE_FXTOF1=1 
#The implicit build, if no parameters are passed is for AD-96TOF1-EBZ.


cd $(dirname $(dirname $(dirname $(realpath $0)))) 
git pull
sudo rm -r -f build
mkdir build
cd build

if [ "$#" -eq 1 ]; then
	cmake "$1" -DXAVIERNX=1 -DWITH_OPENCV=on -DWITH_PYTHON=on -DCMAKE_PREFIX_PATH="/opt/glog;/opt/protobuf;/opt/websockets" ..

else
	cmake -DXAVIERNX=1 -DWITH_OPENCV=on -DWITH_PYTHON=on -DCMAKE_PREFIX_PATH="/opt/glog;/opt/protobuf;/opt/websockets" ..
fi

sudo cmake --build . --target install
