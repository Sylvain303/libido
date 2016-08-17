#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4:
#
# libido - python prototype
# 
# example: python libido.py ../examples/libido/shell_lib.bash
#
# Usage: libido [OPTIONS] SOURCE_FILE ...
#
# OPTIONS:
#  -n          dry run
#  -v          verbose
#  -b=[suffix] backup with suffix (incremental backup)
#  -r          revert?
#  -e          export back marked piece of code

import sys
import re
import os

import parser_factory

def usage():
    # with sed: [[ "$1" == "--help" ]] && { sed -n -e '/^# Usage:/,/^$/ s/^# \?//p' < $0; exit; }
    f = open(sys.argv[0])
    match = False
    for l in f:
        if match and re.match(r'^\s*$', l):
            match = False
            break

        if re.match(r'^# Usage:', l):
            match = True

        if match:
            out = re.sub(r'^# ?', '', l)
            print(out.rstrip())
    f.close()

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
            print("config:error:%d:split on:'%s'" % (i, l))
            continue

        if var:
            print('config(%d):%s : %s' % (i, var, val))
            config[var] = val
        else:
            print('config:error:%d:no match: %s' % (i,l))

def main():
    # verify script number of arguments
    nargv = len(sys.argv)
    if nargv <= 1:
        usage()
        sys.exit(1)
      
    # process agrument
    filename = sys.argv[1]

    # process config
    config_base = 'libido.conf'

    config = config_base
    conf = {}
    if os.path.isfile(config):
        conf = readconfig(config)

    print('filename=%s' % filename)
    factory = parser_factory.parser_factory(config)

    parser = factory.get_parser(filename)
    if not parser:
        print("no parser found for '%s' type: %s" % (filename, file_type))
        sys.exit(1)

    d = parser.parse(filename)

    # output stats
    out = "# %s " % ( os.path.basename(filename) )
    no_print = []
    out += '('
    for stat in d:
        if stat in no_print:
           continue
        # or trunk to 2 chars with stat[0:2]
        out += "%s : %d, " % (stat, d[stat])

    out = re.sub(r', $', ')', out)

    # display all functions found
    if d['function'] > 0:
        # list all
        out += "\n%s" % ' '.join(parser.chunks.keys())
        # output + start
        for f in parser.chunks.keys():
            out += "\n%s:%d" % (f, parser.chunks[f]['start'])
        # print all matched chunks of code
        parser.print_chunks()

    print out


if __name__ == '__main__':
    main()
