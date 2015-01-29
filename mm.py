#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import mmconfig


class MM:
    def __init__(self):
        self.mm_config_name = r"mm.cfg"
        self.mm_config = mmconfig.MMConfig()

        self.mm_path = os.path.dirname(__file__)
        self.scons_struct = os.path.join(self.mm_path, "sconstruct")

        self.module_path = os.getcwd()
        self.module_name = self.mm_config.get_value("module.name", os.path.basename(self.module_path))
        self.mm_config.set_value("module.name", self.module_name)

        self.mm_config_path = []
        self.__init_config()
        self.build_dir = self.mm_config.get_value("env.build_dir", os.path.normpath(self.module_path))
        self.__mkdir(self.build_dir)

        self.scons_path = self.mm_config.get_value("scons.path", self.__find_file("scons"))
        self.scons_param = self.mm_config.get_value("scons.param")
        self.scons_param = self.__add_cmd_param(self.scons_param, "-f " + self.scons_struct)
        self.scons_param = self.__add_cmd_param(self.scons_param, "-Q ")


    def __init_config(self):
        self.mm_config_path.append(os.path.realpath(os.getcwd()))
        self.mm_config_path.append(os.path.realpath(os.path.expandvars('$HOME')))
        self.mm_config_path.append(os.path.realpath(self.mm_path))
        self.mm_config_path = list(set(self.mm_config_path))
        for path in self.mm_config_path:
            config_file = os.path.join(path, self.mm_config_name)
            if os.path.exists(config_file) and os.path.isfile(config_file):
                print("mm  " + config_file)
                self.mm_config.read_config(config_file)

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

    def build_module(self, path):
        os.system(self.scons_path + self.scons_param + " --random --tree=all")

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

    def clean_module(self):
        scons_param = self.__add_cmd_param(self.scons_param, "-c")
        print(self.__add_cmd_param(self.scons_path, self.scons_param))
        os.system(self.scons_path + scons_param)

    def show_depends(self):
        depends = self.mm_config.get_value("module.depend", "").split(',')
        print("Depend:" + depend for depend in depends)


def find_source(suffixlist, path='.', recursive=False):
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
    if "clean" in sys.argv:
        mm.clean_module()
        sys.exit(0)
    if "show" in sys.argv:
        mm.show_env()
        mm.show_depends()
    mm.build_module(".")


