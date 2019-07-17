#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

name = "screen-recorder"
source = "https://github.com/lognoz/archlinux-packages"

def pre_build():
    os.system("mv ./screen-recorder/* ./")

    files = os.listdir(".")
    for f in files:
        if os.path.isdir(f):
            os.system("rm -rf " + f)
        elif os.path.isfile(f) and f != "package.py" and f != "PKGBUILD" and f != "screen-recorder.sh":
            os.remove(f)
