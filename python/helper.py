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
