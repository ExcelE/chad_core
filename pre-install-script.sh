#!/bin/bash

TEMP_FOLDER='pre_install'
PYTHON_VER_CHECK=$(python3 -c '
import sys;
if not sys.version_info.major == 3 and sys.version_info.minor >= 5:
    print(0);
else:
    print(1);
')
HAS_VENV=$(python3 -c 'import pkgutil; print(1 if pkgutil.find_loader("virtualenv") else 0)')
HAS_TENSORFLOW=$(python3 -c 'import pkgutil; print(1 if pkgutil.find_loader("tensorflow") else 0)')
HAS_OPENCV=$(python3 -c 'import pkgutil; print(1 if pkgutil.find_loader("cv2") else 0)')

if [[ $PYTHON_VER_CHECK -eq "1" ]]; then
    echo -e "Python check passed!"
else
    echo -e "Please ensure you have Python3 with at least version 3.5"
    exit
fi

if [[ $HAS_VENV -eq "1" ]]; then
    echo -e "\n\nVirtualenv install done"
    python3 -m pip install virtualenv --user
    echo -e "\n\nVirtualenv install done"
else
    echo -e "Virtualenv Installed!"
fi

if [[ $HAS_TENSORFLOW -eq "1" ]]; then
    echo -e "Tensorflow not found. Installing"
    apt-get install libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev
    apt-get install python3-pip
    pip3 install -U pip
    pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v42 tensorflow-gpu
    echo -e "Tensorflow Installed."
else
    echo -e "Tensorflow Installed!"
fi

if [[ $HAS_OPENCV -eq "1" ]]; then
    git clone https://github.com/jetsonhacks/buildOpenCVTX2.git pre_install/Opencv
    ./pre_install/Opencv/buildOpenCV.sh > /dev/null
    echo -e "Opencv Installed."
else
    echo -e "Opencv Installed!"
fi
