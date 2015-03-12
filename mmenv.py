#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import mmcommon
import mmconfig
import mmrepo


class MMEnv:
    def __init__(self):
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

        self.build_dir = self.__config.get_value("env.build_dir", "mm_build")
        mmcommon.mkdir(self.build_dir)
        self.source_dir = self.__config.get_value("env.src_dir", "mm_source")
        mmcommon.mkdir(self.source_dir)
        self.lib_dir = self.__config.get_value("env.lib_dir", "mm_lib")
        mmcommon.mkdir(self.lib_dir)
        self.src_suffixes = self.__config.get_split_value("env.src_suffixes")

        self.__repo_objs = []
        repos = self.__config.get_items("repo.dir")
        for repo in repos:
            url = self.__config.get_value("repo.dir." + repo + ".url")
            assert os.path.isdir(url)
            self.__repo_objs.append(mmrepo.MMDirRepo(repo, url))
        repos = self.__config.get_items("repo.single")
        for repo in repos:
            url = self.__config.get_value("repo.single." + repo + ".url")
            assert os.path.isdir(url)
            self.__repo_objs.append(mmrepo.MMSingleRepo(repo, url))

        mm_lib_path = os.getenv('MM_LIB_PATH')
        if mm_lib_path is not None:
            self.__config.set_value("env.lib_dir", mm_lib_path)
            self.lib_dir = mm_lib_path

        mm_repo_path = os.getenv('MM_REPO_LOCAL_PATH')
        if mm_repo_path is not None:
            self.__config.set_value("repo.dir.env.url", mm_repo_path)
            assert os.path.isdir(mm_repo_path)
            self.__repo_objs.append(mmrepo.MMDirRepo('env', mm_repo_path))

    def __add_cmd_param(self, param, add_param):
        return param + " " + add_param + " "

    def get_repo(self):
        return self.__repo_objs

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
