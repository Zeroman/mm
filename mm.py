#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from mmcommon import *
import mmconfig
import mmenv


def create_templete(args):
    mmcfg = mmconfig.MMConfig()

    name = ''
    ver = ''
    for arg in args:
        param = "name="
        if arg.startswith(param):
            name = arg[len(param):]
        param = "ver="
        if arg.startswith(param):
            ver = arg[len(param):]

    path = module_to_dir(name, ver)

    for arg in args:
        param = "depend="
        if arg.startswith(param):
            depend = arg[len(param):]
            mmcfg.set_value(join_node("module.depend", depend, "ver"), "")
            mmcfg.set_value(join_node("module.depend", depend, "repo"), "")
        param = "inc_dir="
        if arg.startswith(param):
            inc_dir = arg[len(param):]
            mmcfg.set_value("module.inc_dir", inc_dir)
    if path != '':
        if os.path.isdir(path):
            print("error " + path + " is dir.")
            return
        mkdir(path)
    mmcfg.save(os.path.join(path, "mm.cfg"))
    mkdir(os.path.join(path, 'example'))
    mkdir(os.path.join(path, 'src'))
    mkdir(os.path.join(path, 'include'))
    mkdir(os.path.join(path, 'test'))


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
    map_argv["s"] = "--tree=all"
    map_argv["sn"] = "--tree=all -n"

    arch = ""
    for arg in sys.argv:
        if arg.startswith("arch="):
            arch = arg[5:]
            sys.argv.remove(arg)
            break

    if len(sys.argv) > 1 and "create" == sys.argv[1]:
        create_templete(sys.argv[1:])
        sys.exit(0)

    for param in map_argv.keys():
        if param in sys.argv:
            sys.argv.remove(param)
            sys.argv.append(map_argv[param])

    mm_env = mmenv.MMEnv()
    # mm_env.show()
    mm_env.build_module(os.getcwd(), " ".join(sys.argv[1:]))

