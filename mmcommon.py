#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import platform
import shutil
import os.path
import collections
import re


MM_CONFIG = r'mm.cfg'
MM_BUILD_CONFIG = r'mm_build.cfg'
MM_STAMP_SOURCE = r'.stamp_source'
MM_SOURCE_SUFFIXES = ['.c', 'cpp', 'hpp', 'cc']


def default_arch():
    return platform.system().lower()


def split_value(value, sep=','):
    return filter(lambda x: x != "", map(lambda x: x.strip(), value.split(sep)))


def join_node(*args):
    lst = []
    for arg in args:
        if arg != "":
            lst.append(arg)
    return ".".join(lst)


def mkdir(path):
    if os.path.isdir(path):
        return
    if os.path.exists(path) and not os.path.isdir(path):
        print("mkdir error : " + path + " is not dir")
        return
    os.makedirs(path)


def find_file(name, path=None, exts=('',)):
    search_path = os.environ['PATH'].split(os.pathsep)
    if path is not None:
        search_path.append = path.split(os.pathsep)
    for dir in search_path:
        for ext in exts:
            binpath = os.path.join(dir, name) + ext
            if os.path.exists(binpath):
                return os.path.abspath(binpath)
    return None


def find_module_config(path):
    modules = []

    def find_func(arg, dirname, names):
        files = [os.path.normpath(os.path.join(dirname, file)) for file in names]
        for file in files:
            if os.path.isdir(file):
                continue
            if os.path.isfile(file) and os.path.basename(file) == MM_CONFIG:
                modules.append(file)

    try:
        os.path.walk(path, find_func, None)
    except os.error:
        print("walk : os.error")
        return modules
    return modules


def copy_file(src, dest, symlinks=False):
    dir = os.path.dirname(dest)
    if not os.path.exists(dir):
        os.makedirs(dir)
    if not os.path.exists(src):
        print(src + " is not exist, skip.")
        return
    if os.path.isdir(src):
        os.makedirs(dest)
    elif os.path.islink(src) and symlinks:
        linkto = os.readlink(src)
        os.symlink(linkto, dest)
    else:
        shutil.copy2(src, dest)


def copy_dir(src, dest, recursive=False, symlinks=False):
    if not os.path.isdir(src):
        print(src + " is not dir, skip.")
        return

    def copyItems(src, dest, symlinks=False):
        for item in os.listdir(src):
            srcPath = os.path.join(src, item)
            if os.path.isdir(srcPath):
                if recursive:
                    srcBasename = os.path.basename(srcPath)
                    destDirPath = os.path.join(dest, srcBasename)
                    if not os.path.exists(destDirPath):
                        os.makedirs(destDirPath)
                    copyItems(srcPath, destDirPath)
            elif os.path.islink(item) and symlinks:
                linkto = os.readlink(item)
                os.symlink(linkto, dest)
            else:
                shutil.copy2(srcPath, dest)

    dest = os.path.join(dest, os.path.basename(os.path.normpath(src)))
    if not os.path.exists(dest):
        os.makedirs(dest)
    copyItems(src, dest)


def create_file(path, info=""):
    f = file(path, 'w')
    f.write(info)
    f.close()


def read_file(path):
    info = ""
    try:
        f = file(path, 'r')
        info = f.read()
        f.close()
    except IOError:
        print("open file %s error" % (path))
    return info


def list_append(src_list, item):
    if item is None:
        return
    if isinstance(item, tuple) or isinstance(item, list):
        for value in item:
            src_list.append(value)
    else:
        src_list.append(item)


def find_source(path, suffixlist=MM_SOURCE_SUFFIXES, recursive=False):
    """

    :rtype : list
    """
    source = []
    if not os.path.isdir(path):
        return source

    def find_func(arg, dirname, names):
        files = [os.path.normpath(os.path.join(dirname, file)) for file in names]
        for file in files:
            if os.path.isdir(file):
                continue
            if len(suffixlist) == 0:
                source.append(file)
            else:
                ext = os.path.splitext(file)[1]
                if ext in suffixlist:
                    source.append(file)

    if recursive:
        os.path.walk(path, find_func, None)
    else:
        try:
            names = os.listdir(path)
            find_func(None, path, names)
        except os.error:
            print("listdir : os.error")
            return source
    return source


def check_version(param):
    ver_match = r'\d\.\d\.\d{1,2}$|\d\.\d\.\d{1,2}-.*'
    m = re.match(ver_match, param)
    return m


def get_module_info(info):
    (repo, name, ver) = ("", "", "")
    items = info.split(':')
    count = len(items)
    if count == 3:
        repo = items[0]
        name = items[1]
        ver = items[2]
    elif count == 2:
        if check_version(items[1]):
            name = items[0]
            ver = items[1]
        else:
            repo = items[0]
            name = items[1]
    elif count == 1:
        name = items[0]
    return (repo, name, ver)


def module_to_dir(name, ver):
    return os.path.join(name.replace(":", os.path.sep), ver)


def module_to_str(name, ver, repo):
    _str = name
    if repo is not "":
        _str = repo + ":" + name
    if ver is not "":
        _str += ":" + ver
    return _str


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def get(self, key):
        try:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        except KeyError:
            return None

    def set(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value


if __name__ == "__main__":
    modules = find_module_config("/work/com/mm/test_repo1")
    for m in modules:
        print m
    print(split_value(",,,,,,,"))
    print(split_value(",      ,    ,  ,  ,"))
    print(split_value("a,b"))
    print(split_value("a,, , , ,       b"))
    print(split_value("a,b,"))


