#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

import mmcommon
import mmmodconfig


class MMRepo:
    def get_name(self):
        return ""

    def have_module(self, name, ver):
        return False

    def find_module(self, regexp):
        return False

    def add_module(self, path):
        pass

    def remove_module(self, name):
        pass

    def pull_module(self, path, name, ver):
        pass

    def show(self):
        pass


def mm_module_copy(module_path, dest_path):
    module_config = mmmodconfig.MMModConfig(module_path)
    print("pull module path is " + dest_path)
    mm_cfg = os.path.join(module_path, mmcommon.MM_CONFIG)
    mmcommon.copy_file(mm_cfg, os.path.join(dest_path, mmcommon.MM_CONFIG))
    src_dir = os.path.join(module_path, module_config.get_source_dir())
    # print("pull " + src_dir)
    mmcommon.copy_dir(src_dir, dest_path)
    inc_dir = os.path.join(module_path, module_config.get_include_dir())
    mmcommon.copy_dir(inc_dir, dest_path)
    lib_dir = os.path.join(module_path, module_config.get_lib_dir())
    mmcommon.copy_dir(lib_dir, dest_path)
    test_dir = os.path.join(module_path, module_config.get_test_dir())
    mmcommon.copy_dir(test_dir, dest_path)


class MMDirRepo(MMRepo):
    def __init__(self, name, path):
        self.__path = os.path.normpath(path)
        self.__modules = self.__get_modules()
        self.__name = name

    def __get_modules(self):
        modules = []
        all_configs = mmcommon.find_module_config(self.__path)
        for config in all_configs:
            module_path = os.path.dirname(config)
            temp_name = module_path.replace(self.__path, '')[1:]
            modules.append(temp_name.replace(os.path.sep, '.'))
        return modules

    def get_name(self):
        return self.__name

    def have_module(self, name, ver=""):
        module_path = os.path.join(self.__path, mmcommon.module_to_dir(name, ver))
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

    def pull_module(self, path, name, ver=""):
        module_path = os.path.join(self.__path, mmcommon.module_to_dir(name, ver))
        if os.path.exists(module_path):
            dest = os.path.join(path, mmcommon.module_to_dir(name, ver))
            mm_module_copy(module_path, dest)
            return True
        else:
            print("no module <" + name + ":" + ver + ">" + " in repo [" + self.__name + "]")
            return False


class MMSingleRepo(MMDirRepo):
    def __init__(self, name, path):
        self.__path = path
        self.__name = name
        pardir = os.path.normpath(os.path.join(path, os.path.pardir))
        MMDirRepo.__init__(self, self.__name, pardir)

    def have_module(self, name, ver=''):
        module_path = os.path.join(self.__path, ver)
        return name == self.__name and os.path.exists(module_path)

    def find_module(self, regexp):
        return False

    def add_module(self, path):
        pass

    def remove_module(self, name):
        pass

    def show(self):
        pass


if __name__ == "__main__":
    repo = MMDirRepo("test", "/work/com/mm/test_repo1")
    repo.pull_module("/tmp/mm_module/", "ab")
    repo.pull_module("/tmp/mm_module/", "aa.a.c")
    repo.show()
    print(repo.find_module("aa.."))
    print(repo.find_module("ab"))

    repo = MMDirRepo("test1", "/work/com/zm/")
    repo.pull_module("/tmp/mm_module/", "sqlite3")
    repo.show()

    repo = MMSingleRepo("sqlite3pp", "/work/com/zm/sqlite3pp")
    print("test have_module : %s " % repo.have_module("aaaaa"))
    print("test have_module : %s " % repo.have_module("sqlite3pp"))
    repo.pull_module("/tmp/mm_module/", "sqlite3pp")

