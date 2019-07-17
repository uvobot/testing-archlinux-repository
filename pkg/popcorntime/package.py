#!/usr/bin/env python
# -*- coding:utf-8 -*-

name = "popcorntime"
source = "https://aur.archlinux.org/popcorntime-bin.git"

def pre_build():
    for line in edit_file("PKGBUILD"):
        if line.startswith("pkgname="):
            print("pkgname=popcorntime")
        else:
            print(line)
