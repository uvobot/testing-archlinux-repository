#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

name = "dwm"
source = "https://aur.archlinux.org/dwm-git.git"

def pre_build():
    for line in edit_file("PKGBUILD"):
        if line.startswith("pkgname="):
            print("pkgname=dwm")
        else:
            print(line)
