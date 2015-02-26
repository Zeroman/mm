#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from mmcommon import *
import mmcommon
import mmenv
import mmconfig
import mmmodconfig


class MMModule:
    def __init__(self, name='', repo='', ver='', srcs_dir='', env=None):
        self.env = env
        if self.env is None:
            self.env = mmenv.MMEnv()

        self.module_name = name
        if name == '':
            self.module_name = os.path.basename(self.module_path)

        self.repos = self.env.get_repo()
        self.sources_dir = srcs_dir
        if self.sources_dir == '':
            self.sources_dir = self.env.sources_dir()
            self.get_sources_from_repo(self.module_name)

        if name == "":
            self.module_path = os.path.normpath(os.getcwd())
        else:
            self.module_path = self.__module_path(self.module_name)

        self.module_ver = ver
        self.module_repo = repo

        self.__mod_config = mmmodconfig.MMModConfig(self.module_path)

        self.__depend_stack = []
        self.mm_depends = []
        self.mm_all_depends_list = []
        self.mm_all_depends_dict = {}
        self.module_incdir_dict = {}
        self.depend_config_dict = {}

        self.mm_depends = self.__mod_config.get_depend()
        self.__proc_depends()

        # self.__init_config()


    def __init_config(self):
        for module_name in self.mm_all_depends_list:
            __config = self.get_module_config(module_name)

            node = join_node("module", "inc_dir");
            inc_dir = __config.get_value(node, "include")
            inc_dir = os.path.join(self.__module_path(module_name), inc_dir)
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
        self.__config.set_value("module.depend", ",".join(self.mm_all_depends_list))

    def get_sources_from_repo(self, module_info):
        def get_module(name, ver):
            dest_path = self.sources_dir
            source_ok = os.path.join(dest_path, name, ver, mmcommon.MM_SOURCE)
            if os.path.exists(source_ok):
                info = mmcommon.read_file(source_ok)
                if info == module_info:
                    return True
            print('dest path = ' + dest_path)
            if repo.pull_module(name, dest_path, ver):
                mmcommon.create_file(source_ok, module_info)
                return True
            return False

        ret = False
        (repo_name, module_name, module_ver) = mmcommon.get_module_info(module_info)
        for repo in self.repos:
            if repo_name != '':
                if repo.get_name() == repo_name:
                    ret = get_module(module_name, module_ver)
                    break
            else:
                ret = get_module(module_name, module_ver)
                if ret:
                    break
        return ret


    def __module_path(self, module_name):
        path = os.path.join(self.sources_dir, module_name)
        if os.path.exists(path):
            return path
        else:
            return None

    def get_module_config(self, module_name):
        if self.depend_config_dict.has_key(module_name):
            return self.depend_config_dict[module_name]
        __config = mmconfig.MMConfig()

        module_path = self.__module_path(module_name)
        if module_path is None:
            print("can't find module " + module_name)
            return None
        # print("find module_path =" + module_path)
        __config.read_config(os.path.join(module_path, MM_CONFIG))
        self.depend_config_dict[module_name] = __config
        return __config

    def __proc_depends(self):
        dict_depends = {}
        for depend in self.mm_depends:
            # print("depend -> %s" % depend)
            dict_depends[depend] = self.__get_depends(depend)
        self.mm_all_depends_dict[self.module_name] = dict_depends
        self.__depends_dict_to_list(self.mm_all_depends_dict, self.mm_all_depends_list)

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

    def __get_depends(self, module_name):
        mm_depends = {}
        if module_name in self.__depend_stack:
            print("Error : depend come back to self: %s" % (module_name))
            return mm_depends
        self.__depend_stack.append(module_name)
        self.get_sources_from_repo(module_name)
        module_path = self.__module_path(module_name)
        module_config = mmmodconfig.MMModConfig(module_path)
        depends = module_config.get_depend()
        if len(depends) is 0:
            # print("%s -> none " % module_name)
            self.__depend_stack.pop()
            return mm_depends
        for depend in depends:
            if depend != "":
                # print("depend -> %s" % depend)
                mm_depends[depend] = self.__get_depends(depend)
        self.__depend_stack.pop()
        return mm_depends


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
        config.set_node_dict("env", self.__config.get_node_dict("env"))
        node = join_node("module", "depend")
        config.set_node_dict(node, self.__config.get_node_dict(node))
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
        self.__mod_config.show()


    def show_depends(self):
        print("-" * 50)
        self.__show_map("", self.mm_all_depends_dict)


if __name__ == "__main__":
    # mm_module = MMModule(name="sqlite3pp", srcs_dir="/work/com/zm")
    # mm_module.show_depends()
    mm_module = MMModule(name="sqlite3pp")
    mm_module.get_sources_from_repo("gtest")
    mm_module.show_depends()
    mm_module.show_env()
