#!/usr/bin/env python

"""
Copyright (c) Build Your Own Arch Linux Repository developers
See the file 'LICENSE' for copying permission
"""

import os
import sys
import shutil
import logging
import subprocess
import multiprocessing

from core.settings import UPSTREAM_REPOSITORY
from core.settings import IS_DEVELOPMENT
from core.settings import IS_TRAVIS

from datetime import datetime
from imp import load_source
from core.data import conf
from core.data import paths
from core.data import update_disabled
from core.data import remote_repository
from utils.editor import edit_file
from utils.editor import replace_ending
from utils.process import extract
from utils.process import git_remote_path
from utils.process import has_git_changes
from utils.process import output
from utils.process import strict_execute
from utils.style import title
from utils.style import bold
from utils.validator import validate


manager = multiprocessing.Manager()
packages = manager.list()

class Repository():
    def pull_main_repository(self):
        if IS_DEVELOPMENT or update_disabled("bot"):
            return

        print("Updating repository bot:")

        try:
            output("git remote | grep upstream")
        except:
            self._execute(f"git remote add upstream {UPSTREAM_REPOSITORY}")

        self._execute(
            "git fetch upstream; "
            "git pull --no-ff --no-commit -X theirs upstream master; "
            "git reset HEAD README.md; "
            "git checkout -- README.md; "
            "git commit -m 'Core: Pull main repository project';"
        )

        print("  [ ✓ ] up to date")

    def synchronize(self):
        sys.path.append(paths.pkg)

        print(bold("Check for any updates:"))

        pool = multiprocessing.Pool()
        results = pool.imap_unordered(self._initialize, conf.packages)
        pool.close()

        for result in results:
            if result is "asdfasdf":
                pool.terminate()
                break

        pool.join()

        print(packages)

    def _initialize(self, name):
        package = Package(name)

        package.clean_directory()
        package.check_module_source()
        package.check_module_name()

        if len(package.errors) > 0:
            errors = "\n".join(["  - " + str(error) for error in package.errors])
            print(f"[ x ] {package.name}\n" + errors)
            return

        package.pull_repository()

        if "pre_build" in dir(package.module):
            package.pre_build()

        package.set_real_version()
        package.set_variables()

        if package.has_new_version():
            packages.append(name)
            print(f"[ - ] {package.name}")
            return True

        print(f"[ ✓ ] {package.name}")


class Package():
    def __init__(self, name):
        self.errors = []

        self.name = name
        self.path = os.path.join(paths.pkg, name)
        self.module = load_source(name + ".package", os.path.join(self.path, "package.py"))

    def clean_directory(self):
        files = os.listdir(self.path)

        for f in files:
            path = os.path.join(self.path, f)

            if os.path.isdir(path):
                shutil.rmtree(path)

            elif os.path.isfile(path) and f != "package.py":
                os.remove(path)

    def has_new_version(self):
        if has_git_changes(self.path):
            return True

        for f in os.listdir(paths.mirror):
            if f.startswith(self.module.name + '-' + self._epoch + self._version + '-'):
                return False

        return True

    def set_variables(self):
        self._version = extract(self.path, "pkgver")
        self._name = extract(self.path, "pkgname")
        self._epoch = extract(self.path, "epoch")

        if self._epoch:
            self._epoch += ":"

    def pre_build(self):
        self._execute("""
        python -c 'from package import pre_build; pre_build()'
        """)

    def set_real_version(self):
        try:
            os.path.isfile(self.path + "/PKGBUILD")
            output("source " + self.path + "/PKGBUILD; type pkgver &> /dev/null")
        except:
            return

        self._execute("""
        mkdir -p ./tmp; \
        makepkg \
            SRCDEST=./tmp \
            --nobuild \
            --nodeps \
            --nocheck \
            --nocolor \
            --noconfirm \
            --skipinteg; \
        rm -rf ./tmp;
        """)

    def check_module_source(self):
        if not _attribute_exists(self.module, "source"):
            self.errors.append("No source variable is defined in package.py")


    def check_module_name(self):
        if _attribute_exists(self.module, "name") is False:
            self.errors.append("No name variable is defined in package.py")

        elif self.name != self.module.name:
            self.errors.append("The name defined in package.py is the not the same in PKGBUILD.")

    def pull_repository(self):
        self._execute(f"""
        git init --quiet;
        git remote add origin {self.module.source};
        git pull origin master;
        rm -rf .git;
        rm -f .gitignore;
        """)

    def _execute(self, process):
        #subprocess.call(process, shell=True, cwd=self.path)
        subprocess.call(process, shell=True, cwd=self.path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def _attribute_exists(module, name):
    try:
        getattr(module, name)
        return True
    except AttributeError:
        return False


repository = Repository()
