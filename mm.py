#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from mmcommon import *
import mmenv


def create_templete(self):
    mkdir('example')
    mkdir('src')
    mkdir('include')
    mkdir('test')


if __name__ == "__main__":
    map_argv = {}
    map_argv["-p"] = "packall"
    map_argv["p"] = "packall"
    map_argv["-P"] = "pack"
    map_argv["P"] = "pack"
    map_argv["b"] = "build"
    map_argv["-b"] = "build"
    map_argv["B"] = "build_depends"
    map_argv["-B"] = "build_depends"

    arch = ""
    for arg in sys.argv:
        if arg.startswith("arch="):
            arch = arg[5:]
            sys.argv.remove(arg)
            break

    if "create" in sys.argv:
        create_templete()
        sys.exit(0)

    for param in map_argv.keys():
        if param in sys.argv:
            sys.argv.remove(param)
            sys.argv.append(map_argv[param])

    mm_env = mmenv.MMEnv()
    # mm_env.show()
    mm_env.build_module(os.getcwd(), " ".join(sys.argv[1:]))

