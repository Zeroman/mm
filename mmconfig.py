#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser

import mmcommon


class MMConfigFile(ConfigParser.ConfigParser):
    def __init__(self, defaults=None):
        ConfigParser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class MMConfig:
    def __init__(self):
        self.dict_configs = {}

    def read_config(self, filePath):
        dict_values = {}
        config = MMConfigFile()
        config.read(filePath)
        sections = config.sections()
        for section in sections:
            items = config.items(section)
            for i, v in items:
                dict_values[section + '.' + i] = v
                # print('%s.%s = %s' % (section, i, v))

        for k in dict_values.keys():
            self.__set_value(k.split('.'), dict_values[k], self.dict_configs)

    def __set_value(self, name, value, map_config):
        # print(name, value, map_config)
        name_len = len(name)
        if name_len == 0:
            return
        key = name[0]
        if not map_config.has_key(key) or map_config[key] is None:
            map_config[key] = {}
        if name_len == 1:
            map_config[key][''] = value
        else:
            self.__set_value(name[1:], value, map_config[key])

    def get_node_dict(self, node, create=False):
        keys = node.split('.')
        dict_node = self.dict_configs
        for key in keys:
            if key == "":
                break
            if not dict_node.has_key(key):
                if create:
                    dict_node[key] = {}
                else:
                    return None
            dict_node = dict_node[key]
        return dict_node

    def add_node_dict(self, node, value):
        self.__set_node_dict(node, value, True)

    def set_node_dict(self, node, value):
        self.__set_node_dict(node, value, False)

    def __set_node_dict(self, node, value, is_add):
        keys = node.split('.')
        dict_node = self.dict_configs
        key_count = len(keys)
        for key_index in range(key_count - 1):
            key = keys[key_index]
            if dict_node is None:
                dict_node = {}
            if not dict_node.has_key(key):
                dict_node[key] = {}
            dict_node = dict_node[key]
        key = keys[-1]
        if is_add and value is not None and dict_node.has_key(key):
            merge_dict = dict(dict_node[key].items() + value.items())
            dict_node[key] = merge_dict
        else:
            dict_node[key] = value

    def move_node(self, src_node, dst_node):
        dict_node = self.get_node_dict(src_node)
        if dict_node is not None:
            self.set_node_dict(src_node, None)
            self.set_node_dict(dst_node, dict_node)

    def get_items(self, node):
        items = []
        dict_node = self.get_node_dict(node)
        if dict_node is None:
            return items
        for key in dict_node.keys():
            if key != "":
                items.append(key)
        return items

    def get_value(self, node, defvalue=""):
        dict_node = self.get_node_dict(node)
        if dict_node is None:
            return defvalue
        if not dict_node.has_key(""):
            print("%s no value" % node)
            return defvalue
        return dict_node[""]

    def save(self, path, node=""):
        config = MMConfigFile()
        dict_values = self.__to_dict_values(node)
        for (k, v) in dict_values.items():
            nodes = k.split('.')
            section = ".".join(nodes[:-1])
            if section == "":
                continue
            key = nodes[-1]
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, key, v)
        config.write(file(path, 'w'))

    def show(self, node=""):
        dict_node = self.get_node_dict(node)
        if dict_node is not None:
            self.__show("", dict_node)

    def show_values(self, node=""):
        dict_values = self.__to_dict_values(node)
        for k in sorted(dict_values.keys()):
            print('%s = %s' % (k, dict_values[k]))

    def __to_dict_values(self, node=""):
        dict_values = {}

        def __to_values(str_node, dict_value):
            if dict_value is None:
                return
            for key in dict_value.keys():
                value = dict_value[key]
                temp_node = mmcommon.join_node(str_node, key)
                # print("%s : %s = %s" % (str_node, key, value))
                if key != "":
                    __to_values(temp_node, value)
                else:
                    dict_values[temp_node] = value

        __to_values(node, self.get_node_dict(node))
        return dict_values

    def convert_scons(self, node=""):
        dict_values = {}
        scons_lines = []
        scons_lines.append("Import('env')\n")
        node_len = len(node)

        def append_to_list(key, value):
            env = key.replace('.', '_')
            scons_lines.append("env.Append(%s= '%s')\n" % (env, value))

        for (key, value) in sorted(dict_values.items()):
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

    mm = MMConfig()
    mm.set_value("set.s", 1)
    mm.set_value("set.r", 2)
    mm.show()
    mm.add_node_dict("set.t", {"":3})
    mm.show()
    mm.move_node("set", "test.move.set")
    mm.show()
    # mm.show_values()
    # mm.show("module.depend")
    # print(mm.get_items("module.depend"))
    # print(mm.get_value("module.depend.test1.config"))
    # print(mm.get_value("module.depend.test1.max_version"))
