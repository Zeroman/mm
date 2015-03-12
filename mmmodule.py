#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from mmcommon import *
import mmenv
import mmconfig
import mmmodconfig


config_cache = LRUCache(100)
module_cache = LRUCache(100)


def get_module_config(module_dir, module_arch):
    assert os.path.exists(module_dir)

    config = config_cache.get(module_dir)
    if config is not None:
        return config

    module_config = mmmodconfig.MMModConfig(module_dir, module_arch)
    config_cache.set(module_dir, module_config)
    return module_config


def get_module(name='', ver='', repo='', arch='', env=None):
    info = module_to_str(name, ver, repo)
    module = module_cache.get(info)
    if module is not None:
        return module
    module = MMModule(name, ver, repo, arch, env)
    module_cache.set(info, module)
    return module


class MMModule:
    def __init__(self, name='', ver='', repo='', arch='', env=None):
        self.env = env
        if self.env is None:
            self.env = mmenv.MMEnv()

        self.module_arch = arch
        if arch == '':
            self.module_arch = default_arch()

        self.module_name = name
        self.module_ver = ver
        self.module_repo_name = ""
        if self.module_name is '':
            curpath = os.getcwd()
            self.module_name = os.path.basename(curpath)
            self.module_repo = None
            self.module_path = curpath
            self.module_dir = ''
        else:
            self.module_repo = self.__find_module_repo(repo)
            self.module_repo_name = self.module_repo.get_name()
            assert self.module_repo is not None
            self.module_dir = module_to_dir(self.module_name, self.module_ver)
            self.module_path = os.path.join(self.env.source_dir, self.module_dir)
        self.module_info = module_to_str(self.module_name, self.module_ver, self.module_repo_name)

        self.module_depend = []

        self.source_dir = None
        self.lib_dir = None
        self.install_lib_dir = None

        self.inc_dir = []
        self.dep_inc_dir = []
        self.ccflags = []
        self.dep_ccflags = []
        self.cxxflags = []
        self.dep_cxxflags = []
        self.linkflags = []
        self.dep_linkflags = []

        self.__all_depends_dict = None
        self.all_module_depend = []

    def __find_module_repo(self, name):
        for repo in self.env.get_repo():
            # print("find module " + module_name + " in " + repo.get_name())
            if name is not '' and repo.get_name() != name:
                continue
            if repo.have_module(self.module_name, self.module_ver):
                return repo
        return None

    def __str__(self):
        return "<" + self.module_info + ">"


    def init_config(self):
        self.module_config = get_module_config(self.module_path, self.module_arch)
        self.module_depend = self.module_config.get_depend()
        self.source_dir = self.module_config.get_source_dir()
        self.lib_dir = self.module_config.get_lib_dir()
        self.install_lib_dir = self.env.lib_dir

    def init_depend(self):
        self.all_module_depend = []
        self.__all_depends_dict = {}
        self.__proc_depends()

    def init_source(self):
        if self.module_repo is None:
            return True

        ret = False
        stamp_source = os.path.join(self.module_path, MM_STAMP_SOURCE)
        if os.path.exists(stamp_source):
            info = read_file(stamp_source)
            if info == self.module_info:
                return True

        if self.module_repo.pull_module(self.env.source_dir, self.module_name, self.module_ver):
            create_file(stamp_source, self.module_info)
            ret = True

        if not ret:
            print("Cann't find module " + self.module_info)
        return ret

    def __proc_depends(self):
        param = (self.module_name, self.module_ver, self.module_repo_name)
        self.__all_depends_dict[self.module_name] = self.__get_depends(*param)
        self.__depends_dict_to_list(self.__all_depends_dict, self.all_module_depend)

    def __depends_dict_to_list(self, depends_dict, depends_list):
        data = depends_dict.items()
        while data:
            k, v = data.pop(0)
            if k is not self.module_name and k is not "":
                if k in depends_list:
                    depends_list.remove(k)
                depends_list.append(k)
            self.__depends_dict_to_list(v, depends_list)

    def __show_map(self, base, map_data):
        data = map_data.items()
        while data:
            k, v = data.pop(0)
            sys.stdout.write('%s->%s' % (base, k))
            items = v.items()
            if len(items) == 1:
                (ik, iv) = items[0]
                if not iv.items():
                    sys.stdout.write('->%s' % ik)
                    sys.stdout.write('\n')
                    continue
            sys.stdout.write('\n')
            if data:
                self.__show_map(base + '|   ', v)
            else:
                self.__show_map(base + '    ', v)

    def __get_depends(self, name, ver, repo, dep_stack=[]):
        module_depend = {}
        info = module_to_str(name, ver, repo)
        if info in dep_stack:
            print("Error : depend come back to self: %s" % (info))
            return module_depend
        dep_stack.append(info)
        path = os.path.join(self.env.source_dir, module_to_dir(name, ver))
        module_config = get_module_config(path, self.module_arch)
        depends = module_config.get_depend()
        for depend in depends:
            print("depend -> %s" % depend)
            module_depend[module_to_str(*depend)] = self.__get_depends(*depend, dep_stack=dep_stack)
        dep_stack.pop()
        return module_depend


    def __convert_env_config(self, name, bitem=False):
        if bitem:
            value = self.__config.get_value(name)
        else:
            value = self.__config.get_items(name)
        return "env.Append(%s= '%s)'\n" % (name, value)


    def convert_config(self):
        script = file(os.path.join(self.build_dir, "sconscript"), "w")
        script.writelines(self.__config.convert_scons())


    def __check_file_exist(self, path):
        return os.path.exists(path)

    def __report(self, count, blockSize, totalSize):
        percent = int(count * blockSize * 100 / totalSize)
        sys.stdout.write("\r%d%%" % percent + ' complete')
        sys.stdout.flush()

    def save_module_config(self, path):
        config = mmconfig.MMConfig()
        # config.set_node_dict("env", self.module_config.get_node_dict("env"))
        # node = join_node("module", "depend")
        # config.set_node_dict(node, self.module_config.get_node_dict(node))
        # config.show()
        config.show_values()
        config.save(path)

    def get_source_list(self):
        assert self.source_dir is not None
        if not os.path.isdir(self.source_dir):
            return []
        source = self.module_config.get_source()
        if source is 'all':
            sources = find_source(self.env.src_suffixes, self.source_dir, recursive=True)
        elif source is '':
            sources = find_source(self.env.src_suffixes, self.source_dir)
        else:
            sources_count = len(source)
            for index in xrange(sources_count):
                source[index] = os.path.join(self.source_dir, source[index])
        # print sources
        # print("node = %s name = %s source = %s" % (module_node, name, source))
        assert isinstance(source, list)
        return source


    def DownloadFile(self, src, dst):
        # sys.stdout.write('\rFetching ' + name + '...\n')
        # urllib.urlretrieve(getFile, saveFile, reporthook=self.__report)
        # sys.stdout.write("\rDownload complete, saved as %s" % (fileName) + '\n\n')
        sys.stdout.flush()

    def show(self):
        print("-" * 50)
        print("source dir : " + self.env.source_dir)
        print("depend %s " % self.module_depend)
        # self.module_config.show()
        if self.__all_depends_dict is not None:
            self.__show_map("", self.__all_depends_dict)


if __name__ == "__main__":
    # mm_module = MMModule(name="sqlite3pp", source_dir="/work/com/zm")
    # mm_module.show_depends()

    mm_module = MMModule("sqlite3")
    mm_module.init_source()

    mm_module = MMModule("sqlite3pp")
    mm_module.init_source()
    mm_module.init_config()
    mm_module.init_depend()
    mm_module.show()

    mm_module = MMModule("abc")
    mm_module.init_source()
    mm_module.init_config()
    mm_module.init_depend()
    mm_module.show()

