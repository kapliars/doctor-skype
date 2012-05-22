import os
from setuptools import setup

def read_local_file(fname):
    """ read file in current directory """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="doctorskype",
    version="0.1",
    author="Arseniy Kaploun",
    url="https://github.com/kapliars/doctor-skype",
    description=("Monitor dying linux skype and restart it"),
    packages=['doctorskype'],
    long_description=read_local_file('README.md'),
    package_data= { 'doctorskype': ['logging.conf']},
    install_requires=["psi","python-daemon"]
)

