#!/bin/bash

TEMP_FOLDER='pre_install'
HAS_VENV=$(python -c 'import pkgutil; print(1 if pkgutil.find_loader("virtualenv") else 0)')
HAS_TENSORFLOW=$(python -c 'import pkgutil; print(1 if pkgutil.find_loader("tensorflow") else 0)')
HAS_OPENCV=$(python -c 'import pkgutil; print(1 if pkgutil.find_loader("cv2") else 0)')

if [[ $HAS_VENV -eq "1" ]]; then
    python3 -m pip install virtualenv --user
    echo -e "\n\nVirtualenv install done"
else
    echo -e "Virtualenv Installed!"
fi

if [[ $HAS_TENSORFLOW -eq "1" ]]; then
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
