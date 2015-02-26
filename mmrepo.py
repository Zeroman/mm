#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

import mmcommon
import mmmodconfig


class MMRepo:
    def have_module(self, name):
        return False

    def find_module(self, regexp):
        return False

    def add_module(self, path):
        pass

    def remove_module(self, name):
        pass

    def pull_module(self, name, path, ver=""):
        pass

    def show(self):
        pass


class MMLocalRepo(MMRepo):
    def __init__(self, path):
        self.__path = os.path.realpath(path)
        self.__modules = self.__get_modules()

    def __name2dir(self, name):
        return name.replace(".", os.path.sep)

    def __name2path(self, name):
        return os.path.join(self.__path, self.__name2dir(name))

    def __path2name(self, path):
        temp_name = path.replace(self.__path, '')[1:]
        return temp_name.replace(os.path.sep, '.')

    def __get_modules(self):
        modules = []
        all_configs = mmcommon.find_module_config(self.__path)
        for config in all_configs:
            modules.append(self.__path2name(os.path.dirname(config)))
        return modules

    def have_module(self, name):
        module_path = self.__name2path(name)
        return os.path.exists(module_path)


    def show(self):
        print(self.__path + " : ")
        print("  " + " ".join(self.__modules))


    def find_module(self, pattern):
        modules = []
        for module in self.__modules:
            m = re.match(pattern, module)
            if m:
                modules.append(module)
        if len(modules) > 0:
            return modules
        else:
            return None

    def add_module(self, path):
        pass

    def remove_module(self, name):
        pass

    def pull_module(self, name, path, ver=""):
        module_path = self.__name2path(name)
        module_config = mmmodconfig.MMModConfig(module_path)
        if os.path.exists(module_path):
            dest = os.path.join(path, self.__name2dir(name))
            print("pull module path is " + dest)
            mm_cfg = os.path.join(module_path, mmcommon.MM_CONFIG)
            mmcommon.copy_file(mm_cfg, os.path.join(dest, mmcommon.MM_CONFIG))
            src_dir = os.path.join(module_path, module_config.get_source_dir())
            print("pull " + src_dir)
            mmcommon.copy_dir(src_dir, dest)
            inc_dir = os.path.join(module_path, module_config.get_include_dir())
            mmcommon.copy_dir(inc_dir, dest)
            lib_dir = os.path.join(module_path, module_config.get_lib_dir())
            mmcommon.copy_dir(lib_dir, dest)
            test_dir = os.path.join(module_path, module_config.get_test_dir())
            mmcommon.copy_dir(test_dir, dest)
            return True
        else:
            print("no module " + name)
            return False


if __name__ == "__main__":
    repo = MMLocalRepo("/work/com/mm/test_repo1")
    repo.pull_module("ab", "/tmp/mm_module/")
    repo.pull_module("aa.a.c", "/tmp/mm_module/")
    repo.show()
    print(repo.find_module("aa.."))
    print(repo.find_module("ab"))
    repo = MMLocalRepo("/work/com/zm/")
    repo.pull_module("sqlite3", "/tmp/mm_module/")
    repo.show()
