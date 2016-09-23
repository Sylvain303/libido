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
#  -e          export marked piece of code, to remote_project
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
import fnmatch
# pip install --user configparser
from configparser import ConfigParser, ExtendedInterpolation


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

# for ipython debugging
# => import libido
# => reload(libido); l = libido.create_l('../examples/readme_ex0.sh')
def create_l(filename):
    l = libido({})
    l.load_config()
    l.init_factory()
    l.parse_input(filename)
    return l

# this class keep track of all information of the libido process
class libido:
    def __init__(self, arguments):
        self.arguments = arguments

        # process config
        self.config_base = 'libido.conf'
        self.conf = None

        # eval our own location
        self.mydir = os.path.dirname(os.path.realpath(__file__))

    def load_config(self):
        """
        load_config() : search and load libido.conf in `conf`, now use ConfigParser.
        """
        look_for_config = [ '.', '.libido', '~/.libido', self.mydir ]
        conf_parser = ConfigParser(interpolation=ExtendedInterpolation(), default_section='libido')
        self.conf = None
        for d in look_for_config:
            config_file = os.path.join(os.path.expanduser(d), self.config_base)
            if os.path.isfile(config_file):
                printerr('configparser=%s' % config_file)
                r = conf_parser.read(config_file)
                # when a config is found stop
                if r[0] == config_file:
                    self.conf = conf_parser
                    break

        if self.conf == None:
            raise RuntimeError("no config found")

    def init_factory(self):
        # init factory parser which contains the libido_parser
        self.factory = parser_factory.parser_factory(self.conf)
        self.lparser = self.factory.libido_parser

    def parse_input(self, filename):
        self.lparser.parse(filename)

    def readconfig(self, fname):
        """
        DEPRECATED.
        readconfig() : internal config parser, parse a bash like syntax, ignore inifile section
        """
        f = open(fname)
        i = 0
        var, val = None, None
        config = {}

        # not used yet
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

        missing = []
        # parse config
        for l in f:
            i += 1
            # skip comment
            if re.match(r'^\s*#', l):
                continue
            # skip inifile section, See load_config()
            if re.match(r'^\[', l):
                continue

            l = l.rstrip()
            # skip empty line
            if l == '':
                continue

            try:
                var, val = re.split(r'\s*=\s*', l)
            except ValueError:
                printerr("config:error:%d:split on:'%s'" % (i, l))
                continue

            if not var:
                # split has failed, not an allowed config directive
                printerr('config:error:%d:no match: %s' % (i,l))
                continue

            printerr('config(%d):%s : %s' % (i, var, val))

            m = re.match(r'^\$(\i+)', val)
            if m:
                # var expand assignment
                ref = m.group(1)
                if config.get(ref):
                    config[var] = config.get(ref)
                else:
                    missing.append(ref)
            else:
                # normal assignment
                config[var] = val

        for ref in missing:
            if config.get(ref):
                config[var] = config.get(ref)
            else:
                # no fail assign an empty var
                config[var] = None

        f.close()
        return config

    def process_output(self, filename, dest):
        ovrewrite = False
        need_tmp = False

        if dest == 'None' or dest == filename:
            ovrewrite = True
            dest = filename
            need_tmp = True

        if self.arguments['--diff']:
            ovrewrite = False
            # need_tmp will force tmpfile
            need_tmp = True

        if dest == '-':
            dest = '/dev/stdout'

        if need_tmp:
            out = NamedTemporaryFile(delete=False)
        else:
            out = open(dest, 'w')

        out.write(self.lparser.dump_result())
        out.close()

        if self.arguments['--diff']:
            os.system("diff -u %s %s" % (filename, out.name))

        # finalyze
        if ovrewrite:
            shutil.move(out.name, filename)
        elif need_tmp:
            os.unlink(out.name)

    def process_export(self, filename):
        # filename is already parsed as libido
        # we have to parse it as it self
        p = self.factory.get_parser(filename)
        p.parse(filename)

        tokens =  p.chunks.keys()
        # order as in the file
        tokens.sort(lambda a, b: cmp(p.chunks[a]['start'], p.chunks[b]['start']))
        export_f = fnmatch.filter(tokens, '*')

        # open destination project
        dest = self.conf['libido'].get('remote_project', "libido_exported.%s")
        # auto add parser extension
        if re.search(r'%s', dest):
            dest = dest % (p.name)
        dest = os.path.join(self.remote_location, dest)
        f = open(dest, 'wt')
        for func in export_f:
            f.write("# %s\n" % (func))
            f.write(libido_parser.flat_line(p.get_chunk(p.chunks[func])))
        f.close()

        printerr("%d func written to '%s'" % (len(export_f), dest))

        return dest

    def ensure_remote_access(self):
        remote_location = self.conf['libido'].get('remote_location')
        remote_location = os.path.dirname(os.path.expanduser(remote_location))
        self.remote_location = os.path.realpath(remote_location)
        return self.remote_location

def main():
    # command line processing
    arguments = docopt(get_usage(), version='0.2')
    if arguments['-q']:
        quiet(True)

    printerr(arguments)

    l = libido(arguments)
    l.load_config()
    l.init_factory()

    export = False

    # destination, default 'None'
    dest = arguments['-o']
    if arguments['-e']:
        if dest != 'None':
            raise RuntimeError('-o not supported with -e')
        else:
            l.ensure_remote_access()
            export = True

    # process filename's agrument, only the first for now
    filename = arguments['SOURCE_FILE'][0]
    printerr('filename=%s, dest=%s' % (filename, dest))

    l.parse_input(filename)

    if export:
        l.process_export(filename)
    else:
        l.process_output(filename, dest)


if __name__ == '__main__':
    main()
