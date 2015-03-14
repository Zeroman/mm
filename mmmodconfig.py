#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mmcommon import *
import mmconfig
import mmenv

DEFAULT_SRC_DIR = "dir:src"
DEFAULT_INC_DIR = "include"
DEFAULT_LIB_DIR = "lib"
DEFAULT_EXAMPLE_DIR = "example"
DEFAULT_TEST_DIR = "test"
DEFAULT_UNITTEST_DIR = "test/unit"


class MMModConfig:
    def __init__(self, module_src, arch=''):
        self.__module_src = module_src
        self.__module_arch = arch
        if arch == '':
            self.__module_arch = default_arch()
        self.__config = mmconfig.MMConfig()
        config_path = os.path.join(module_src, MM_CONFIG)
        self.__config.read_config(config_path)

    def __get_split_value(self, node, def_value=None):
        dir = self.__config.get_split_value(node)
        if len(dir) is 0 and def_value is not None:
            dir.append(def_value)
        return dir

    def get_source_info(self):
        dir = self.__get_split_value("module.src", DEFAULT_SRC_DIR)
        return dir


    def get_include_dir(self):
        dir = self.__get_split_value("module.inc_dir", DEFAULT_INC_DIR)
        return dir

    def get_example_dir(self):
        dir = self.__get_split_value("module.example_dir", DEFAULT_EXAMPLE_DIR)
        return dir

    def get_test_dir(self):
        dir = self.__get_split_value("module.test_dir", DEFAULT_TEST_DIR)
        return dir

    def get_unittest_dir(self):
        dir = self.__get_split_value("module.unittest_dir", DEFAULT_UNITTEST_DIR)
        return dir

    def get_lib_dir(self):
        dir = self.__get_split_value("module.lib_dir")
        return dir

    def get_ccflags(self):
        dir = self.__get_split_value("module.ccflags")
        return dir

    def get_cxxflags(self):
        dir = self.__get_split_value("module.cxxflags")
        return dir

    def get_linkflags(self):
        dir = self.__get_split_value("module.linkflags")
        return dir

    def get_depend(self):
        depend = []

        def __get_depends(node):
            depend_names = self.__config.get_items(node)
            for name in depend_names:
                ver = self.__config.get_value(join_node(node, name, "ver"), '')
                repo = self.__config.get_value(join_node(node, name, "repo"), '')
                depend.append((name, ver, repo))

        __get_depends("module.depend")
        __get_depends(join_node("module.depend", self.__module_arch))
        return depend

    def get_source_list(self):
        source = []
        for info in self.get_source_info():
            src_type = "dir"
            src_param = ""
            temp = split_value(info, ':')
            if len(temp) == 2:
                (src_type, src_param) = temp
            else:
                src_param = temp[0]
            if src_param is not "":
                source += self.__get_source_list(src_type, src_param)
        return source

    def __get_source_list(self, src_type, src_param):
        sources = []
        str_len = len(self.__module_src)
        if src_type == 'rec':
            dir = os.path.join(self.__module_src, src_param)
            sources = find_source(dir, mmenv.global_env.src_suffixes, recursive=True)
            sources = map(lambda x: x[str_len:], sources)
        elif src_type == 'dir':
            dir = os.path.join(self.__module_src, src_param)
            sources = find_source(dir, mmenv.global_env.src_suffixes)
            sources = map(lambda x: x[str_len:], sources)
        elif src_type == 'file':
            sources = [src_param]
        # print sources
        # print("node = %s name = %s source = %s" % (module_node, name, source))
        return sources

    def show(self):
        self.__config.show()


if __name__ == "__main__":
    mod_config = MMModConfig("/work/com/zm/gtest/gtest_main")
    print("src_info = %s " % mod_config.get_source_info())
    print("inc_dir = %s " % mod_config.get_include_dir())
    print("lib_dir = %s " % mod_config.get_lib_dir())
    print("test_dir = %s " % mod_config.get_test_dir())
    print(mod_config.get_depend())
