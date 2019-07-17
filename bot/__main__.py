#!/usr/bin/env python

"""
Copyright (c) Build Your Own Arch Linux Repository developers
See the file 'LICENSE' uor copying permission
"""

from environment import environment
from interface import interface
from repository import repository
from validator import validator

from core.contextual import get_base_path
from core.contextual import set_configs
from core.contextual import set_paths
from core.contextual import set_logs
from core.contextual import set_repository
from core.runner import runner


def set_contextual():
    base = get_base_path()
    set_paths(base)
    set_repository()
    set_configs()
    set_logs()

def main():
    set_contextual()

    runner.set("build", [
        repository.synchronize
    ])

    for execute in runner.get():
        execute()


if __name__ == "__main__":
    main()
