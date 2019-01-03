#!/usr/bin/python3

## 
# @package setup.py 
# setup.py for distutils of gencfs
# Copyright 2019 linurs.org 
# Distributed under the terms of the GNU General Public License v2

from distutils.core import setup
setup(
      name="gencfs",
      scripts=["gencfs.py"],
      version="0.5",
      description='Python3 Tkinter Gui for encfs',
      author='Urs Lindegger',
      author_email='urs@linurs.org',
      url='https://github.com/linurs/gencfs',
      download_url = "http://www.linurs.org/download/gencfs-0.5.tgz",
      keywords = ["encfs encryption"],
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security",
      ],
      long_description=open("README.md").read()     
)