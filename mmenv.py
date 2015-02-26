#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import mmcommon
import mmconfig
import mmrepo


class MMEnv:
    def __init__(self):
        self.__local_repo_dirs = []
        self.__config_path = []

        self.mm_path = os.path.dirname(os.path.realpath(__file__))
        self.__config = mmconfig.MMConfig()

        self.scons_path = self.__config.get_value("scons.path", mmcommon.find_file("scons"))
        self.scons_param = self.__config.get_value("scons.param")
        site_dir = os.path.join(self.mm_path, "site")
        self.scons_param = self.__add_cmd_param(self.scons_param, "--site-dir=" + site_dir)
        self.scons_script = os.path.join(self.mm_path, "sconstruct")
        # self.scons_param = self.__add_cmd_param(self.scons_param, "-Q ")

        self.__config_path.append(os.path.realpath(os.getcwd()))
        self.__config_path.append(os.path.realpath(os.path.expandvars('$HOME')))
        self.__config_path.append(os.path.realpath(self.mm_path))
        self.__config_path = list(set(self.__config_path))
        for path in self.__config_path:
            config_file = os.path.join(path, mmcommon.MM_CONFIG)
            if os.path.exists(config_file) and os.path.isfile(config_file):
                # print("mm  " + config_file)
                self.__config.read_config(config_file)

        self.build_dir = self.__config.get_value("env.build_dir", ".")
        mmcommon.mkdir(self.build_dir)

        repos = self.__config.get_items("repo.local")
        for repo in repos:
            dir = self.__config.get_value("repo.local." + repo + ".dir")
            assert os.path.isdir(dir)
            self.__local_repo_dirs.append(dir)

        mm_libs_path = os.getenv('MM_LIBS_PATH')
        if mm_libs_path is not None:
            self.__config.set_value("env.libs_dir", mm_libs_path)

        mm_repo_path = os.getenv('MM_REPO_PATH')
        if mm_repo_path is not None:
            self.__config.set_value("repo.local.env.dir", mm_repo_path)
            assert os.path.isdir(mm_repo_path)
            self.__local_repo_dirs.append(mm_repo_path)

    def __add_cmd_param(self, param, add_param):
        return param + " " + add_param + " "

    def get_repo(self):
        repo_objs = []
        for repo in self.__local_repo_dirs:
            repo_objs.append(mmrepo.MMLocalRepo(repo))
        return repo_objs

    def sources_dir(self):
        return self.__config.get_value("env.srcs_dir", "mm_srcs")

    def build_module(self, path, argv=""):
        print("+" * 20 + "Start build %s" % os.path.basename(path) + "+" * 20)
        # os.system(self.scons_path + self.scons_param + " --random --tree=all")
        scons_param = self.__add_cmd_param(self.scons_param, "-f " + self.scons_script)
        scons_param = self.__add_cmd_param(scons_param, argv)
        os.chdir(path)
        ret = os.system(self.scons_path + scons_param)
        # print (" ret = %d" % ret)
        print("-" * 20 + "End build %s" % os.path.basename(path) + "-" * 20)
        print("")
        return ret
        # print(scons_param)

    def show(self):
        self.__config.show()

if __name__ == "__main__":
    env = MMEnv()
    env.show()
    repos = env.get_repo()
    for repo in repos:
        repo.show()
