#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4:
#
# libido - python prototype
# 
# helpers function common to multiple code
from __future__ import print_function

import sys

QUIET=False

def quiet(v = None):
    global QUIET
    if v is not None: 
        QUIET = v

    return QUIET

def printerr(*args, **kwargs):
    global QUIET
    if not QUIET:
        print(*args, file=sys.stderr, **kwargs)

def flat_line(list_of_lines):
    """
    flat_line() : format a list on line as flat str, if is contains a list expand it
    """
    if isinstance(list_of_lines, str):
        list_of_lines = [ list_of_lines ]

    out = ''
    for l in list_of_lines:
        if isinstance(l, list):
            out += '\n'.join([ ll.rstrip() for ll in l])
        else:
            if l[-1] == '\n':
                out += l
            else:
                out += l + '\n'
    return out
