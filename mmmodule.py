#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from mmcommon import *
import mmcommon
import mmenv
import mmconfig
import mmmodconfig


config_cache = mmcommon.LRUCache(100)
module_cache = mmcommon.LRUCache(100)


def get_module_config(module_dir, module_arch):
    assert os.path.exists(module_dir)

    config = config_cache.get(module_dir)
    if config is not None:
        return config

    module_config = mmmodconfig.MMModConfig(module_dir, module_arch)
    config_cache.set(module_dir, module_config)
    return module_config


def get_module(name='', ver='', repo='', arch='', env=None):
    info = mmcommon.module_to_str(name, ver, repo)
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
        repo_name = ""
        if self.module_name is '':
            curpath = os.getcwd()
            self.module_name = os.path.basename(curpath)
            self.module_repo = None
            self.module_path = curpath
            self.module_dir = ''
        else:
            self.module_repo = self.__find_module_repo(repo)
            repo_name = self.module_repo.get_name()
            assert self.module_repo is not None
            self.module_dir = mmcommon.module_to_dir(self.module_name, self.module_ver)
            self.module_path = os.path.join(self.env.source_dir, self.module_dir)
        self.module_info = mmcommon.module_to_str(self.module_name, self.module_ver, repo_name)

        self.module_depend = []
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
        # self.__init_config()

    def init_depend(self):
        self.__depend_stack = []
        self.all_module_depend = []
        self.__all_depends_dict = {}
        self.__proc_depends()

    def __init_config(self):
        for module_name in self.all_module_depend:
            __config = get_module_config(module_name)

            node = join_node("module", "inc_dir");
            inc_dir = __config.get_value(node, "include")
            inc_dir = os.path.join(self.module_dir, inc_dir)
            node = join_node("module", "depend", module_name, "inc_dir");
            self.__config.set_value(node, inc_dir)

            def set_depend_config(module_name, param):
                node = join_node("module", param)
                value = __config.get_value(node, "")
                node = join_node("module", "depend", module_name, param)
                if value is not None and value is not "":
                    self.__config.set_value(node, value)

            set_depend_config(module_name, "CCFLAGS")
            set_depend_config(module_name, "CXXFLAGS")
            set_depend_config(module_name, "LINKFLAGS")

        self.__config.set_value("module.name", self.module_name)
        self.__config.set_value("module.depend", ",".join(self.all_module_depend))

    def init_source(self):
        if self.module_repo is None:
            return True

        ret = False
        stamp_source = os.path.join(self.module_path, mmcommon.MM_STAMP_SOURCE)
        if os.path.exists(stamp_source):
            info = mmcommon.read_file(stamp_source)
            if info == self.module_info:
                return True

        if self.module_repo.pull_module(self.env.source_dir, self.module_name, self.module_ver):
            mmcommon.create_file(stamp_source, self.module_info)
            ret = True

        if not ret:
            print("Cann't find module " + self.module_info)
        return ret

    def __proc_depends(self):
        dict_depends = {}
        for (name, ver, repo) in self.module_depend:
            # print("depend -> %s" % depend)
            info = mmcommon.module_to_str(name, ver, repo)
            dict_depends[info] = self.__get_depends(name, ver, repo)

        self.__all_depends_dict[self.module_name] = dict_depends
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

    def __get_depends(self, name, ver, repo):
        module_depend = {}
        info = mmcommon.module_to_str(name, ver, repo)
        if info in self.__depend_stack:
            print("Error : depend come back to self: %s" % (info))
            return module_depend
        self.__depend_stack.append(info)
        module_config = get_module_config(module_dir)
        depends = module_config.get_depend()
        if len(depends) is 0:
            # print("%s -> none " % module_name)
            self.__depend_stack.pop()
            return module_depend
        for depend in depends:
            if depend != "":
                # print("depend -> %s" % depend)
                module_depend[depend] = self.__get_depends(depend)
        self.__depend_stack.pop()
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

    def DownloadFile(self, src, dst):
        # sys.stdout.write('\rFetching ' + name + '...\n')
        # urllib.urlretrieve(getFile, saveFile, reporthook=self.__report)
        # sys.stdout.write("\rDownload complete, saved as %s" % (fileName) + '\n\n')
        sys.stdout.flush()

    def show_env(self):
        print("-" * 50)
        print("source dir : " + self.env.source_dir)
        print("depend %s " % self.module_depend)
        self.module_config.show()


if __name__ == "__main__":
    # mm_module = MMModule(name="sqlite3pp", source_dir="/work/com/zm")
    # mm_module.show_depends()
    mm_module = MMModule("sqlite3pp")
    mm_module.init_source()
    mm_module.init_config()
    mm_module.show_env()

    mm_module = MMModule()
    mm_module.init_source()
    mm_module.init_config()
    mm_module.show_env()
