#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import mmconfig

mm_path = os.path.dirname(__file__)

mm_path_config = mm_path + "/sconstruct"
mm_config_dirname = r"/.mm"
mm_config_path = [os.getcwd(), os.path.expandvars('$HOME'), mm_path]

module_path = os.getcwd()
module_name = os.path.basename(module_path)


def add_cmd_param(param, add_param):
    return param + " " + add_param + " ";


def find_file(name, path=None, exts=('',)):
    """Search PATH for a binary.

    Args:
      name: the filename to search for
      path: the optional path string (default: os.environ['PATH')
      exts: optional list/tuple of extensions to try (default: ('',))

    Returns:
      The abspath to the binary or None if not found.
    """
    search_path = os.environ['PATH'].split(os.pathsep)
    if path is not None:
        search_path.append = path.split(os.pathsep)
    for dir in search_path:
        for ext in exts:
            binpath = os.path.join(dir, name) + ext
            if os.path.exists(binpath):
                return os.path.abspath(binpath)
    return None


if __name__ == "__main__":
    if "create" in sys.argv:
        os.mkdir('example')
        os.mkdir('src')
        os.mkdir('include')
        os.mkdir('test')
        sys.exit(0)

    mm_config = mmconfig.MMConfig()

    scons_path = mm_config.get_value("scons.path", find_file("scons"))
    scons_param = mm_config.get_value("scons.param")

    scons_param = add_cmd_param(scons_param, "-f " + mm_path_config)
    scons_param = add_cmd_param(scons_param, "module_name=" + module_name)
    print(scons_path + scons_param)
    # os.system(scons_path + scons_param)

    for path in mm_config_path:
        print(path)
    print os.path.basename(mm_path)

