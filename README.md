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

## Usage
### Set Pixels
Set pixels takes an array of arrays, each child array contains three values: red, green, and blue values from 0-255.
You must have 64 children arrays, and they must have proper color values.
[Example that sets all pixels to white](https://gist.github.com/logangorence/5c9b3779627c0a3087ec)
