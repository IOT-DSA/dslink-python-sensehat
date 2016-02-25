from setuptools import setup

setup(
    name="dslink-python-sensehat",
    version="0.2.0",
    description="DSLink for Sense HAT on Raspberry Pi",
    url="http://github.com/IOT-DSA/dslink-python-sensehat",
    author="Logan Gorence",
    author_email="lgorence@dglogik.com",
    license="Apache 2.0",
    install_requires=[
        "dslink == 0.6.4",
        "evdev",
        "sense_hat"
    ]
)
