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

        pool = multiprocessing.Pool()
        pool.map(self._initialize, conf.packages)
        pool.close()

    def _initialize(self, name):
        package = Package(name)

        package.set_utils()
        package.clean_directory()
        package.check_module_source()
        package.check_module_name()

        if len(package.errors) > 0:
            errors = "\n".join(["  - " + str(error) for error in package.errors])
            print(f"[ x ] \033[1m{package.name}\033[0m\n\033[0;31m" + errors + "\033[0m")
            return

        package.pull_repository()

        #if "pre_build" in dir(package.module):
        #   package.module.pre_build()

        print(f"[ ✓ ] \033[1m{package.name}\033[0m to {package.module.source}")


class Package():
    def __init__(self, name):
        self.errors = []

        self.name = name
        self.path = os.path.join(paths.pkg, name)
        self.module = load_source(name + ".package", os.path.join(self.path, "package.py"))

    def set_utils(self):
        self.module.edit_file = edit_file
        self.module.replace_ending = replace_ending

    def clean_directory(self):
        files = os.listdir(self.path)

        for f in files:
            path = os.path.join(self.path, f)

            if os.path.isdir(path):
                shutil.rmtree(path)

            elif os.path.isfile(path) and f != "package.py":
                os.remove(path)

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
        subprocess.call(process, shell=True, cwd=self.path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def _attribute_exists(module, name):
    try:
        getattr(module, name)
        return True
    except AttributeError:
        return False


repository = Repository()
