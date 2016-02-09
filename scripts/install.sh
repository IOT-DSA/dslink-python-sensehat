#!/usr/bin/env bash

# Setup RTIMULib
git clone https://github.com/RPi-Distro/RTIMULib.git
cd RTIMULib/Linux/python
../../../packages/bin/python setup.py install
