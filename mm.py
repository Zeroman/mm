#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import mmconfig


class MM:
    def __init__(self):
        self.__depend_stack = []
        self.mm_config_name = r"mm.cfg"
        self.mm_config = mmconfig.MMConfig()
        self.mm_depends = []
        self.mm_all_depends_list = []
        self.mm_all_depends_dict = {}
        self.repo_dirs = []
        self.module_path_dict = {}
        self.module_incdir_dict = {}
        self.depend_config_dict = {}

        self.mm_path = os.path.realpath(os.path.dirname(__file__))
        self.scons_script = os.path.join(self.mm_path, "sconstruct")

        self.module_path = os.path.normpath(os.getcwd())
        self.module_name = self.mm_config.get_value("module.name", os.path.basename(self.module_path))
        self.mm_config.set_value("module.name", self.module_name)

        self.mm_config_path = []
        self.__init_config()

        self.scons_path = self.mm_config.get_value("scons.path", self.__find_file("scons"))
        self.scons_param = self.mm_config.get_value("scons.param")
        site_dir = os.path.join(self.mm_path, "site")
        self.scons_param = self.__add_cmd_param(self.scons_param, "--site-dir=" + site_dir)
        # self.scons_param = self.__add_cmd_param(self.scons_param, "-Q ")


    def __init_config(self):
        self.mm_config_path.append(os.path.realpath(os.getcwd()))
        self.mm_config_path.append(os.path.realpath(os.path.expandvars('$HOME')))
        self.mm_config_path.append(os.path.realpath(self.mm_path))
        self.mm_config_path = list(set(self.mm_config_path))
        for path in self.mm_config_path:
            config_file = os.path.join(path, self.mm_config_name)
            if os.path.exists(config_file) and os.path.isfile(config_file):
                # print("mm  " + config_file)
                self.mm_config.read_config(config_file)

        self.build_dir = self.mm_config.get_value("env.build_dir", self.module_path)
        self.__mkdir(self.build_dir)

        repos = self.mm_config.get_items("repo.local")
        for repo in repos:
            dir = self.mm_config.get_value("repo.local." + repo + ".dir")
            assert os.path.isdir(dir)
            self.repo_dirs.append(dir)

        mm_libs_path = os.getenv('MM_LIBS_PATH')
        if mm_libs_path is not None:
            self.mm_config.set_value("env.libs_dir", mm_libs_path)

        mm_repo_path = os.getenv('MM_REPO_PATH')
        print(mm_repo_path)
        if mm_repo_path is not None:
            self.mm_config.set_value("repo.local.env.dir", mm_repo_path)
            assert os.path.isdir(mm_repo_path)
            self.repo_dirs.append(mm_repo_path)

        self.mm_depends = self.mm_config.get_value("module.depend", "").split(',')
        self.__proc_depends()
        for module_name in self.mm_all_depends_list:
            mm_config = self.get_module_config(module_name)
            inc_dir = mm_config.get_value("module.inc_dir", "include")
            inc_dir = os.path.join(self.get_module_path(module_name), inc_dir)
            self.mm_config.set_value("module.depend." + module_name + '.inc_dir', inc_dir)
        self.mm_config.set_value("module.depend", ",".join(self.mm_all_depends_list))

    def __submodule_name(self, module_name):
        temp_list = module_name.split(':')
        if len(temp_list) <= 1:
            return None
        return temp_list[1]

    def get_module_path(self, module_name):
        name = module_name.split(':')[0]
        if self.module_path_dict.has_key(name):
            return self.module_path_dict[name]
        for dir in self.repo_dirs:
            path = os.path.join(dir, name)
            if os.path.isdir(path):
                self.module_path_dict[name] = path
                return path
        return None

    def get_module_config(self, module_name):
        if self.depend_config_dict.has_key(module_name):
            return self.depend_config_dict[module_name]
        mm_config = mmconfig.MMConfig()

        module_path = self.get_module_path(module_name)
        if module_path is None:
            print("can't find module " + module_name)
            return None
        # print("find module_path =" + module_path)
        mm_config.read_config(os.path.join(module_path, self.mm_config_name))
        self.depend_config_dict[module_name] = mm_config
        return mm_config

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
        mm_config = self.get_module_config(module_name)
        depends_str = mm_config.get_value("module.depend", None)
        if depends_str is None:
            # print("%s -> none " % module_name)
            self.__depend_stack.pop()
            return mm_depends
        depends = depends_str.split(',')
        for depend in depends:
            if depend != "":
                # print("depend -> %s" % depend)
                mm_depends[depend] = self.__get_depends(depend)
        self.__depend_stack.pop()
        return mm_depends

    def __add_cmd_param(self, param, add_param):
        return param + " " + add_param + " ";


    def __find_file(self, name, path=None, exts=('',)):
        search_path = os.environ['PATH'].split(os.pathsep)
        if path is not None:
            search_path.append = path.split(os.pathsep)
        for dir in search_path:
            for ext in exts:
                binpath = os.path.join(dir, name) + ext
                if os.path.exists(binpath):
                    return os.path.abspath(binpath)
        return None

    def __convert_env_config(self, name, bitem=False):
        if bitem:
            value = self.mm_config.get_value(name)
        else:
            value = self.mm_config.get_items(name)
        return "env.Append(%s= '%s)'\n" % (name, value)


    def convert_config(self):
        script = file(os.path.join(self.build_dir, "sconscript"), "w")
        script.writelines(self.mm_config.convert_scons())

    def build_module(self, path, argv=""):
        print("#" * 20 + "Start build %s" % os.path.basename(path) + "#" * 20)
        # os.system(self.scons_path + self.scons_param + " --random --tree=all")
        scons_param = self.__add_cmd_param(self.scons_param, "-f " + self.scons_script)
        scons_param = self.__add_cmd_param(scons_param, argv)
        os.chdir(path)
        os.system(self.scons_path + scons_param)
        print("#" * 20 + "End build %s" % os.path.basename(path) + "#" * 20)
        print("")
        # print(scons_param)

    def build_modules(self, modules, argv=""):
        for module in modules:
            mm.build_module(mm.get_module_path(module), argv)

    def build_depends(self, argv=""):
        self.build_modules(self.mm_all_depends_list, argv)

    def install(self):
        scons_param = self.scons_param
        scons_param = self.__add_cmd_param(scons_param, "install")
        os.system(self.scons_path + scons_param)

    def __mkdir(self, path):
        if not os.path.isdir(path):
            if os.path.exists(path):
                print("error!")
            os.mkdir(path)

    def create_templete(self):
        self.__mkdir('example')
        self.__mkdir('src')
        self.__mkdir('include')
        self.__mkdir('test')

    def __check_file_exist(self, path):
        return os.path.exists(path)

    def __report(self, count, blockSize, totalSize):
        percent = int(count * blockSize * 100 / totalSize)
        sys.stdout.write("\r%d%%" % percent + ' complete')
        sys.stdout.flush()

    def DownloadFile(self, src, dst):
        # sys.stdout.write('\rFetching ' + name + '...\n')
        # urllib.urlretrieve(getFile, saveFile, reporthook=self.__report)
        # sys.stdout.write("\rDownload complete, saved as %s" % (fileName) + '\n\n')
        sys.stdout.flush()

    def show_env(self):
        self.mm_config.show()


    def show_depends(self):
        print("-" * 50)
        print(" -> ".join(self.mm_all_depends_list))
        print("-" * 50)
        self.__show_map("", self.mm_all_depends_dict)
        print("-" * 50)
        for k, v in self.module_path_dict.items():
            print("%10s : %s" % (k, v))
        print("-" * 50)


def find_source(suffixlist, path='.', recursive=False):
    """

    :rtype : list
    """
    sources = []

    def find_func(arg, dirname, names):
        files = [os.path.normpath(os.path.join(dirname, file)) for file in names]
        for file in files:
            if os.path.isdir(file):
                continue
            ext = os.path.splitext(file)[1]
            if ext in suffixlist:
                sources.append(file)

    if recursive:
        os.path.walk(path, find_func, None)
    else:
        try:
            names = os.listdir(path)
            find_func(None, path, names)
        except os.error:
            print("os.error")
            return sources
    return sources


if __name__ == "__main__":
    mm = MM()
    if "create" in sys.argv:
        mm.create_templete()
        sys.exit(0)
    if "show" in sys.argv:
        print("mm path is " + mm.mm_path)
        for repo in mm.repo_dirs:
            print("repo %-10s : [ %s ]" % (repo, dir))
        mm.show_depends()
        mm.show_env()
        sys.exit(0)
    if "pack" in sys.argv:
        sys.exit(0)

    if "build_depends" in sys.argv:
        sys.argv.remove("build_depends")
        mm.build_depends(" ".join(sys.argv[1:]))

    mm.build_module(mm.module_path, " ".join(sys.argv[1:]))


