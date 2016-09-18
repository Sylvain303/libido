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
# Usage: libido [options] [--] SOURCE_FILE ...
#
# /!\ WARNING ! None of this is working yet!
# options:
#  -v          verbose (messages sent to stderr)
#  -b=[suffix] backup with suffix (incremental backup)
#  -r          revert?
#  -e          export back marked piece of code, to remote_project
#  -o FILE     output to a named file (instead of inline edit) [default: None]
#  --diff      no change, diff -u SOURCE_FILE result on stdout
#  -q          quiet, no output on stderr

# empty line above required ^^
from __future__ import print_function

import sys
import re
import os
from tempfile import NamedTemporaryFile
import shutil



# docopt : pip install --user docopt=0.6.2
from docopt import docopt

# libido local lib
import parser_factory
import libido_parser
from helper import printerr, quiet

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
    # command line processing
    arguments = docopt(get_usage(), version='0.1')
    if arguments['-q']:
        quiet(True)

    printerr(arguments)

    # process filename's agrument, only the first for now
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
    lparser = factory.libido_parser
    lparser.parse(filename)

    # destination
    dest = arguments['-o']
    ovrewrite = False
    need_tmp = False

    if dest == 'None' or dest == filename:
        ovrewrite = True
        dest = filename
        need_tmp = True

    if arguments['--diff']:
        need_tmp = True
        ovrewrite = False

    if dest == '-':
        dest = '/dev/stdout'

    if need_tmp:
        out = NamedTemporaryFile(delete=False)
    else:
        out = open(dest, 'w')

    out.write(lparser.dump_result())
    out.close()

    if arguments['--diff']:
        os.system("diff -u %s %s" % (filename, out.name))

    if ovrewrite:
        shutil.move(out.name, filename)
    elif need_tmp:
        os.unlink(out.name)

if __name__ == '__main__':
    main()
