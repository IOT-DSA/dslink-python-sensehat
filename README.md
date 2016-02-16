# Sense HAT DSLink
This DSLink runs on a Raspberry Pi with the Sense HAT installed.

## Getting Started
### Requirements
- Raspberry Pi 2
- Sense HAT
- Raspbian Jessie
- Password-less sudo(if installing from DGLux)

### Install from DGLux
1. ```sudo apt-get update```
2. ```sudo apt-get install virtualenv python-dev python-pip libjpeg-dev sense-hat```
3. ```sudo pip install pillow```
4. Install via "Install Link from ZIP" in /sys/links/. Use ```https://github.com/IOT-DSA/dslink-python-sensehat/archive/master.zip``` as the URL.
5. Start the link, and wait for the dependencies to be grabbed.
