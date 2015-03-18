#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'zm'

import sys
import dis
import StringIO


def __parse_bytecodes(bufvalue):
    var_names = []
    bytecodes = bufvalue.split('\n')
    length = len(bytecodes)
    var_count = 0
    for i in range(length - 1, -1, -1):
        bytecode = bytecodes[i]

        if var_count != 0:
            var_names.append(bytecode.split()[-1][1:-1])
            var_count -= 1

        if '-->' in bytecode:
            var_count = int(bytecode.split()[-1])

    var_names.reverse()
    return var_names


def mm_debug(*args):
    # replace standard stdout with a StringIO object
    buf = StringIO.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf

    # call dis.disco to get bytecodes
    f = sys._getframe(1)
    dis.disco(f.f_code, f.f_lasti)

    # restore standard stdout
    sys.stdout = old_stdout

    # process bytecode
    var_names = __parse_bytecodes(buf.getvalue())
    buf.close()

    #print var name and var value
    for i, var_name in enumerate(var_names):
        print '%s = %s' % (var_name, args[i])