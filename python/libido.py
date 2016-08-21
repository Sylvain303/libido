#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4:
#
# libido - python prototype
# 
# examples: 
#   # expand or update readme_ex0.sh with code defined in 'lib_source' See libido.conf
#   ./libido.py ../examples/readme_ex0.sh
#
# Usage: libido [options] SOURCE_FILE ...
#
# /!\ WARNING ! None of this is working yet!
# options:
#  -n          dry run
#  -v          verbose
#  -b=[suffix] backup with suffix (incremental backup)
#  -r          revert?
#  -e          export back marked piece of code

# empty line above ^^
from __future__ import print_function

import sys
import re
import os

# docopt : pip install --user docopt=0.6.2
from docopt import docopt

# libido local lib
import parser_factory
import libido_parser
from helper import printerr

def get_usage(filename=None):
    """
    get_usage() : only extract top header comment

    with sed: [[ "$1" == "--help" ]] && { sed -n -e '/^# Usage:/,/^$/ s/^# \?//p' < $0; exit; }
    """
    if filename == None:
        filename = sys.argv[0]
    f = open(filename)
    match = False
    collector = ''
    for l in f:
        if match and re.match(r'^\s*$', l):
            match = False
            break

        if re.match(r'^# Usage:', l):
            match = True

        if match:
            out = re.sub(r'^# ?', '', l)
            collector += out
    f.close()
    return collector

def readconfig(fname):
    f = open(fname)
    i = 0
    var, val = None, None
    config = {}

    keywords = """
        remote_location
        remote_project
        search_scan_offset
        libido_keyword
        git_auto_commit
        auto_inc_duplicate
        auto_quote_string
        disable_add_ref
        lib_source
    """
    allowed = [ k.strip() for k in keywords.strip().split('\n') if len(k) > 1 ]

    for l in f:
        i += 1
        if re.match(r'^#', l):
            continue

        l = l.rstrip()
        if l == '':
            continue

        try:
            var, val = re.split(r'\s*=\s*', l)
        except ValueError:
            printerr("config:error:%d:split on:'%s'" % (i, l))
            continue

        if var:
            printerr('config(%d):%s : %s' % (i, var, val))
            config[var] = val
        else:
            printerr('config:error:%d:no match: %s' % (i,l))

    return config

def main():
    arguments = docopt(get_usage(), version='0.1')
    printerr(arguments)

    # process agrument
    filename = arguments['SOURCE_FILE'][0]

    # process config
    config_base = 'libido.conf'
    conf = None

    # eval our own location
    mydir = os.path.dirname(os.path.realpath(__file__))
    look_for_config = [ '.', '.libido', '~/.libido', mydir ]
    for d in look_for_config:
        config_file = os.path.join(os.path.expanduser(d), config_base)
        if os.path.isfile(config_file):
            printerr('readconfig=%s' % config_file)
            conf = readconfig(config_file)
            break

    if conf == None:
        raise RuntimeError("no config found")

    printerr('filename=%s' % filename)
    factory = parser_factory.parser_factory(conf)

#    parser = factory.get_parser(filename)
#    if not parser:
#        raise RuntimeError("no parser found for '%s' type: %s" % (filename, file_type))
#
#    d = parser.parse(filename)
#
#    # output stats
#    out = "# %s " % ( os.path.basename(filename) )
#    no_print = []
#    out += '('
#    for stat in d:
#        if stat in no_print:
#           continue
#        # or trunk to 2 chars with stat[0:2]
#        out += "%s : %d, " % (stat, d[stat])
#
#    out = re.sub(r', $', ')', out)
#
#    # display all functions found
#    if d['function'] > 0:
#        # list all
#        out += "\n%s" % ' '.join(parser.chunks.keys())
#        # output + start
#        for f in parser.chunks.keys():
#            out += "\n%s:%d" % (f, parser.chunks[f]['start'])
#        # print all matched chunks of code
#        parser.print_chunks()
#
#    printerr(out)

    lparser = libido_parser.libido_parser(conf, factory)
    lparser.parse(filename)
    # no extra newline
    print(lparser.dump_result(), end='')


if __name__ == '__main__':
    main()
