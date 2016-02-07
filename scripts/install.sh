#!/usr/bin/env bash

# Setup virtualenv
virtualenv packages
source packages/bin/activate

# Setup DSLink packages
python setup.py install

# Setup RTIMULib
git clone https://github.com/RPi-Distro/RTIMULib.git
cd RTIMULib/Linux/python
python setup.py install
