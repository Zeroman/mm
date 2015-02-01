#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Zipper
import AccumulatorAction


def TOOL_ADD_HEADER(env):
    """A Tool to add a header from $HEADER to the source file"""
    # add builder to accumulate files
    accuBuilder = env.Builder(action=AccumulatorAction.accumulatorFunction,
        source_factory=SCons.Node.FS.default_fs.Entry,
        target_factory=SCons.Node.FS.default_fs.Entry,
        multi=1)
    env['BUILDERS']['Accumulate'] = accuBuilder

    # add builder to zip files
    zipBuilder = env.Builder(action=Zipper.zipperFunction,
       source_factory=SCons.Node.FS.default_fs.Entry,
       target_factory=SCons.Node.FS.default_fs.Entry,
       multi=0)
    env['BUILDERS']['Zipper'] = zipBuilder


