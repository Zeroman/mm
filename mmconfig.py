#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pprint
import ConfigParser


class MMConfigFile(ConfigParser.ConfigParser):
    def __init__(self, defaults=None):
        ConfigParser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class MMConfig:
    def __init__(self):
        self.dict_configs = {}
        self.dict_values = {}

    def read_config(self, filePath):
        config = MMConfigFile()
        config.read(filePath)
        sections = config.sections()
        for section in sections:
            items = config.items(section)
            for i, v in items:
                self.dict_values[section + '.' + i] = v
                # print('%s.%s = %s' % (section, i, v))

        for k in self.dict_values.keys():
            self.__set_value(k.split('.'), self.dict_values[k], self.dict_configs)

    def __set_value(self, name, value, map_config):
        # print(name, value, map_config)
        name_len = len(name)
        if name_len == 0:
            return
        key = name[0]
        if not map_config.has_key(key):
            map_config[key] = {}
        if name_len == 1:
            map_config[key][''] = value
        else:
            self.__set_value(name[1:], value, map_config[key])

    def __get_dict_node(self, node):
        split_strs = node.split('.')
        dict_node = self.dict_configs
        for key in split_strs:
            if key == "":
                break
            if not dict_node.has_key(key):
                return None
            dict_node = dict_node[key]
        return dict_node

    def get_items(self, node):
        items = []
        dict_node = self.__get_dict_node(node)
        if dict_node is None:
            return items
        for key in dict_node.keys():
            if key != "":
                items.append(key)
        return items

    def get_value(self, node, defvalue=""):
        dict_node = self.__get_dict_node(node)
        if dict_node is None:
            return defvalue
        if not dict_node.has_key(""):
            print("%s no value" % node)
            return defvalue
        return dict_node[""]

    def show(self, node=""):
        dict_node = self.__get_dict_node(node)
        if dict_node is not None:
            self.__show("", dict_node)

    def show_values(self):
        for k in sorted(self.dict_values.keys()):
            print('%s = %s' % (k, self.dict_values[k]))

    def convert_scons(self, node=""):
        scons_lines = []
        scons_lines.append("Import('env')\n")
        node_len = len(node)

        def append_to_list(key, value):
            env = key.replace('.', '_')
            scons_lines.append("env.Append(%s= '%s')\n" % (env, value))

        for (key, value) in sorted(self.dict_values.items()):
            if node_len == 0:
                append_to_list(key, value)
                continue
            key_len = len(key)
            if key_len < node_len:
                continue
            if key_len == node_len:
                if key != node:
                    continue
                append_to_list(key, value)
            if key[:node_len] == node + '.':
                append_to_list(key, value)
        return scons_lines


    def __show(self, base, map_data):
        data = map_data.items()
        while data:
            k, v = data.pop(0)
            if isinstance(v, dict):
                value = ""
                if v.has_key(""):
                    value = v[""]
                print '%s%s : %s' % (base, k, value)
                if data:
                    self.__show(base + '|   ', v)
                else:
                    self.__show(base + '    ', v)

    def set_value(self, node, value):
        self.__set_value(node.split('.'), value, self.dict_configs)


if __name__ == "__main__":
    mm = MMConfig()
    # mm.read_config("mm_1.ini")
    # mm.read_config("mm_2.ini")
    mm.read_config("mm.cfg")
    mm.set_value("set.s", 1)
    mm.set_value("set.r", 2)
    mm.show()
    # mm.show_values()
    # mm.show("module.depend")
    # print(mm.get_items("module.depend"))
    # print(mm.get_value("module.depend.test1.config"))
    # print(mm.get_value("module.depend.test1.max_version"))
