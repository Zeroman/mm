#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import mmenv
import mmmodule
from mmcommon import *

class MMBuilder:
    def __init__(self, env, config_path):
        self.env = env
        self.__config = mmconfig.MMConfig()
        self.__config.read_config(config_path)

        self.arch = self.get_env("module.arch")

        self.__init_arch()
        self.module_name = self.get_env("module.name")
        self.dep_modules = self.get_env_list('module.depend', [])
        self.libs_dir = self.get_env("env.libs_dir")
        assert self.libs_dir is not None
        self.libs_dir = os.path.join(self.libs_dir, self.arch)
        self.list_dep_inc = self.get_depend_module_dir()
        self.build_dir = os.path.join(self.get_env("env.build_dir"), self.module_name, self.arch)
        if self.build_dir is not None:
            VariantDir(self.build_dir, ".", duplicate=0)
        self.share_libs = []
        self.static_libs = []
        self.dict_targets = {}
        self.install_dir = self.get_env("module.install_dir")

        ccflags = self.get_env("module." + self.arch + ".CCFLAGS")
        if ccflags is not None:
            self.env.Append(CCFLAGS=ccflags)
        cxxflags = self.get_env("module." + self.arch + ".CXXFLAGS")
        if cxxflags is not None:
            self.env.Append(CXXFLAGS=cxxflags)
        linkflags = self.get_env("module." + self.arch + ".LINKFLAGS")
        if linkflags is not None:
            self.env.Append(LINKFLAGS=cxxflags)
        libs = self.get_env_list("module." + self.arch + ".LIBS")
        if libs is not None:
            self.env.Append(LIBS=libs)
            # print("LIBS = " + env.Dump('LIBS'))

        self.local_libs = []
        local_libs_dir = os.path.join("lib", self.arch)
        if os.path.isdir(local_libs_dir):
            self.local_libs = mm.find_source([], local_libs_dir)

        self.depend_lib_files = self.__init_depend_lib_files()

    def install(self):
        target = []
        if self.install_dir is not None:
            target.append(self.env.Install(self.install_dir, self.static_libs))
            target.append(self.env.Install(self.install_dir, self.share_libs))
        return target

    def get_env_list(self, env_name, default=None):
        value = self.__config.get_value(env_name, None)
        if value is None or value is "":
            return default
        return value.split(',')

    def get_env(self, env_name):
        return self.__config.get_value(env_name, None)


    def get_mm_module_name(self, module_node):
        name = self.get_env(module_node + '.name')
        if name is None:
            name = module_node.split('.')[-1]
        return name


    def get_depend_module_dir(self):
        inc_dir = []
        # print self.dep_modules
        for submodule in self.dep_modules:
            node = 'module.depend.' + submodule
            dirs = self.get_env_list(node + '.inc_dir')
            if dirs is None:
                continue
            for dir in dirs:
                inc_dir.append(dir)
        return inc_dir

    def get_node_sources(self, node):
        name = self.get_mm_module_name(node)
        sources = self.get_env_list(node + '.sources', [])
        if 'none' in sources:
            return []
        src_dir = self.get_env(node + '.src_dir')
        if src_dir is None:
            src_dir = "src"
        if not os.path.isdir(src_dir):
            return []
        if 'all' in sources:
            sources = mm.find_source(self.get_env_list('env.src_suffixes'), src_dir, recursive=True)
        elif len(sources) is 0:
            sources = mm.find_source(self.get_env_list('env.src_suffixes'), src_dir)
        else:
            sources_count = len(sources)
            for index in xrange(sources_count):
                sources[index] = os.path.join(src_dir, sources[index])
        # print sources
        # print("node = %s name = %s source = %s" % (module_node, name, source))
        assert isinstance(sources, list)
        return sources

    def get_node_inc_dir(self, node):
        inc_dir = self.get_env_list(node + ".inc_dir")
        if inc_dir is None:
            inc_dir = []
            if os.path.isdir('include'):
                inc_dir = ["include"]
        return inc_dir

    def get_node_src_dir(self, node):
        dir = self.get_env_list(node + ".src_dir")
        if dir is None:
            if os.path.isdir('src'):
                dir = "src"
        return dir


    def build_module_node(self, module_node):
        sources = self.get_node_sources(module_node)
        sources_count = len(sources)
        if sources_count == 0:
            return
        for index in xrange(sources_count):
            sources[index] = os.path.join(self.build_dir, sources[index])
        # print sources
        # print("node = %s name = %s source = %s" % (module_node, name, source))
        list_inc = []
        self.list_append(list_inc, self.get_node_inc_dir(module_node))
        self.list_append(list_inc, self.get_node_src_dir(module_node))
        self.list_append(list_inc, self.list_dep_inc)
        self.list_append(list_inc, self.get_env_list(module_node + ".build.inc_dir"))
        name = self.get_mm_module_name(module_node)
        lib_name = os.path.join(self.libs_dir, name)
        sharelib = self.env.SharedLibrary(target=lib_name, source=sources, CPPPATH=list_inc)
        staticlib = self.env.StaticLibrary(target=lib_name, source=sources, CPPPATH=list_inc)
        self.share_libs.append(sharelib)
        self.static_libs.append(staticlib)
        self.dict_targets[name] = [staticlib, sharelib]

    def copy_locallibs(self):
        target = []
        local_libs_dir = os.path.join("lib", self.arch)
        if os.path.isdir(local_libs_dir):
            for lib in self.local_libs:
                target.append(self.env.Install(self.libs_dir, lib))
        return target

    def __init_arch(self):
        arch_node = 'arch.' + self.arch
        env_cc = self.get_env(arch_node + ".CC")
        if env_cc is not None:
            self.env['CC'] = env_cc
        env_cxx = self.get_env(arch_node + ".CXX")
        if env_cxx is not None:
            self.env['CXX'] = env_cxx
        env_ccflags = self.get_env(arch_node + ".CCFLAGS")
        if env_ccflags is not None:
            self.env.Append(CCFLAGS=env_ccflags)
        env_cxxflags = self.get_env(arch_node + ".CXXFLAGS")
        if env_cxxflags is not None:
            self.env.Append(CXXFLAGS=env_cxxflags)
        env_linkflags = self.get_env(arch_node + ".LINKFLAGS")
        if env_linkflags is not None:
            self.env.Append(LINKFLAGS=env_linkflags)

    def dump(self):
        print self.env.Dump("CCFLAGS")
        print self.env.Dump("CXXFLAGS")
        print self.env.Dump("SHLINKFLAGS")

    def __init_depend_lib_files(self):
        libs = []
        for module in self.dep_modules:
            # print 'module = %s' % module
            sharelib_name = self.env['LIBPREFIX'] + module + self.env['SHLIBSUFFIX']
            libs.append(os.path.join(self.libs_dir, sharelib_name))
            static_name = self.env['LIBPREFIX'] + module + self.env['LIBSUFFIX']
            libs.append(os.path.join(self.libs_dir, static_name))
        return libs

    def packall(self):
        zip_dir = os.path.join(self.build_dir, "zip")
        self.env.Accumulate(zip_dir, self.list_dep_inc)
        zip_libdir = os.path.join(zip_dir, "lib")
        self.env.Accumulate(zip_libdir, self.local_libs)
        self.env.Accumulate(zip_libdir, self.depend_lib_files)
        zip_path = os.path.join(self.build_dir, self.module_name + "_all")
        zipall = self.env.Zipper(zip_path, zip_dir)
        return zipall

    def build_example(self):
        target = []
        list_inc = []
        sources = mm.find_source(self.get_env_list('env.src_suffixes'), 'example')
        self.list_append(list_inc, self.list_dep_inc)
        self.list_append(list_inc, self.get_node_inc_dir(self.module_name))
        test_env = env.Clone()
        test_env.Append(LIBS=self.dep_modules)
        test_env.Append(LIBPATH=self.libs_dir)
        test_env.Append(CPPPATH=list_inc)
        test_env.Append(LINKFLAGS='-Wl,-rpath,' + self.libs_dir)
        for src in sources:
            bin = os.path.join(self.build_dir, os.path.splitext(src)[0])
            src = os.path.join(self.build_dir, src)
            example = test_env.Program(target=bin, source=src)
            target.append(example)
        return target




Import("env")
Import("current_module")
Return("module_libs")
