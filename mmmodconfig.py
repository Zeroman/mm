#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mmcommon import *
import mmconfig

DEFAULT_SRC_DIR = "src"
DEFAULT_INC_DIR = "include"
DEFAULT_LIB_DIR = "lib"
DEFAULT_EXAMPLE_DIR = "example"
DEFAULT_TEST_DIR = "test"
DEFAULT_UNITTEST_DIR = "test/unit"


class MMModConfig:
    def __init__(self, module_path, arch=''):
        self.__module_path = module_path
        self.__module_arch = arch
        if arch == '':
            self.__module_arch = default_arch()
        self.__config = mmconfig.MMConfig()
        config_path = os.path.join(module_path, MM_CONFIG)
        self.__config.read_config(config_path)

    def get_source_dir(self):
        dir = self.__config.get_value("module.src_dir", DEFAULT_SRC_DIR)
        return dir

    def get_include_dir(self):
        dir = self.__config.get_value("module.inc_dir", DEFAULT_INC_DIR)
        return dir

    def get_example_dir(self):
        dir = self.__config.get_value("module.example_dir", DEFAULT_EXAMPLE_DIR)
        return dir

    def get_test_dir(self):
        dir = self.__config.get_value("module.test_dir", DEFAULT_TEST_DIR)
        return dir

    def get_unittest_dir(self):
        dir = self.__config.get_value("module.unittest_dir", DEFAULT_UNITTEST_DIR)
        return dir

    def get_lib_dir(self):
        dir = self.__config.get_value("module.lib_dir", DEFAULT_LIB_DIR)
        return dir

    def get_depend(self):
        depend = self.__config.get_value("module.depend", '').split(',')
        node = join_node("module.depend", self.__module_arch)
        arch_depend = self.__config.get_value(node, '').split(',')
        depends = depend + arch_depend
        while depends.count('') > 0:
            depends.remove('')
        return depends

    def show(self):
        self.__config.show()


if __name__ == "__main__":
    mod_config = MMModConfig("/work/com/zm/gtest/gtest_main")
    print("src_dir = " + mod_config.get_source_dir())
    print("inc_dir = " + mod_config.get_source_dir())
    print("lib_dir = " + mod_config.get_lib_dir())
    print("test_dir = " + mod_config.get_test_dir())
