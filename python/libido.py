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
# Usage:
#  libido [options] [--] export [--match=<func_match>...] SOURCE_FILE
#  libido [options] [--] diff SOURCE_FILE
#  libido [options] [--] parse [-f] [--outsider] SOURCE_FILE
#  libido [options] [--] [do] SOURCE_FILES...
#
# options:
#  -v           verbose (messages sent to stderr)
#  -b=[suffix]  backup with suffix (incremental backup)
#  -o FILE      output to a named file (instead of inline edit, not with export) [default: None]
#  -q           quiet, no output on stderr
#  -c CONFFILE  override libido.conf with CONFFILE
#
# Options:
#  -m <func_match>, --match=<func_match>  filter exported function
#  -f                 show only function name, aka: | grep -E '^[^0-9 ]'
#  --outsider         show also outsider chunks
#
# actions:
#  do       changes SOURCE_FILES, change libido code inplace, default behavior
#  export   export marked piece of code, to remote_project
#  diff     no change, `diff -u SOURCE_FILE result` on stdout
#  parse    no change, parses SOURCE_FILE displaying parsed informations on stdout

# empty line above required, See get_usage() ^^
from __future__ import print_function

import sys
import re
import os
from tempfile import NamedTemporaryFile
# shutil for move()
import shutil
# fnmatch provides support for Unix shell-style wildcards
import fnmatch
from collections import OrderedDict

# pip install --user configparser
from configparser import ConfigParser, ExtendedInterpolation, MissingSectionHeaderError

# docopt : pip install --user docopt=0.6.2
from docopt import docopt

# libido local lib
import parser_factory
import libido_parser
from helper import printerr, quiet

def get_usage(filename=None):
    """
    get_usage() : only extract top Usage header in the comment at the beginning

    with sed: [[ "$1" == "--help" ]] && { sed -n -e '/^# Usage:/,/^$/ s/^# \?//p' < $0; exit; }
    """
    if filename == None:
        filename = sys.argv[0]
    f = open(filename)
    match = False
    collector = ''
    for l in f:
        if match and re.match(r'^\s*$', l):
            # finish collecting lines, as we matched an empty line.
            # we stop the loop
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

    def load_config(self, this_conf=None):
        """
        load_config() : search and load libido.conf in `conf`, use ConfigParser
        ini file format.
        """
        if this_conf:
            look_for_config = [ this_conf ]
        else:
            # will search in that order
            look_for_config = [ '.', '.libido', '~/.libido', self.mydir ]
        conf_parser = ConfigParser(interpolation=ExtendedInterpolation(), default_section='libido')
        # reset conf
        self.conf = None
        for d in look_for_config:
            if os.path.isfile(d):
                # for this_conf, this not a directory to look for libido.conf
                # it is a filename
                config_file = d
            else:
                config_file = os.path.join(os.path.expanduser(d), self.config_base)

            if os.path.isfile(config_file):
                try:
                    r = conf_parser.read(config_file)
                except MissingSectionHeaderError as e:
                    print("wrong format: %s" % config_file)
                    r = []

                # when a config is found stop
                if len(r) > 0 and r[0] == config_file:
                    printerr('configparser=%s FOUND' % config_file)
                    self.conf = conf_parser
                    break

                printerr("configparser: '%s' is not a valid format" % config_file)

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

        if self.arguments['diff']:
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

        if self.arguments['diff']:
            os.system("diff -u %s %s" % (filename, out.name))

        # finalyze
        if ovrewrite:
            shutil.move(out.name, filename)
        elif need_tmp:
            os.unlink(out.name)

    def expand_chunk_names(self, chunk_names, globpat, collector):
        """
        expand_chunk_names(): return bool, True if globpat matched.
        chunk_names: a list, containing all words.
        globpat: glob like pattern to match in chunk_names.
        collector: a list to be modified, on succesfull match.
        """
        # As pattern macthimg could match multiple time the same chunk_name, OrderedDict will
        # unduplicates keys. Order is kept, but by filter order too.
        matched = fnmatch.filter(chunk_names, globpat)
        if matched:
            for c in matched:
                if c not in collector:
                    collector.append(c)
            return True
        else:
            return False

    def process_export(self, filename, only_those_func=None):
        """
        process_export() : reparse the filename as an input for our library.
        Library destination is given by self.remote_location See: ensure_remote_access()

        For now it exports all functions found by the parser.

        only_those_func: can be an array of shell like glob, to filter chunk names
        """
        # filename is already parsed as libido file ignoring any other
        # statement.
        # Now we have to parse it as itself, requesting the correct parser
        p = self.factory.get_parser(filename)
        p.parse(filename)

        export_f = []
        chunk_names = p.get_chunk_keys()

        # 3 usecase tested in order: exported, filtered, all

        # do we have exported chucks?
        if self.lparser.exported_chucks:
            # use a tagged export, written in a libido statement
            for c in self.lparser.exported_chucks:
                r = self.expand_chunk_names(chunk_names, c, export_f)
                if not r:
                    printerr("export: '%s' not found in chunks" % (c))
        elif only_those_func:
            # expand_chunk_names() takes care of dedup chunk_names.
            for f in only_those_func:
                # we ignore unmatched filter
                self.expand_chunk_names(chunk_names, f, export_f)
        else:
            # All
            export_f = chunk_names

        # TODO: put 'dest' computation code into a parameter method of the
        # config object or something new.

        # open destination project
        dest = self.conf['libido'].get('remote_project', "libido_exported.%s")

        # auto add parser extension
        if re.search(r'%s', dest):
            dest = dest % (p.name)

        # build at fullpath pointing to a source file (ex: ${lib_source}/libido_exported.bash)
        dest = os.path.join(self.remote_location, dest)

        dp = None
        if os.path.isfile(dest):
            # parse destination file, to detect function's name collision
            dp = self.factory.get_parser(dest)
            dp.ignore_libido_analyze = True
            dp.parse(dest)

        if not dp:
            # create a new export lib, it doesn't exists yet
            f = open(dest, 'wt')
            for func in export_f:
                printerr('func: %s' % func)
                f.write("# %s\n" % (func))
                f.write(libido_parser.flat_line(p.get_chunk(func)))
            f.close()

            printerr("new file, %d func written to '%s'" % (len(export_f), dest))
        else:
            # dest already exist, we perform overwrite if any.
            for chunk_name in export_f:
                if dp.update_chunk(chunk_name, p):
                    printerr("updated chunks: '%s'" % chunk_name)
                else:
                    printerr("chunks: identical '%s'" % chunk_name)
            # TODO: if no modified chunks don't write
            dp.write()

        return dest

    def ensure_remote_access(self):
        remote_location = self.conf['libido'].get('remote_location')
        #remote_location = os.path.dirname(os.path.expanduser(remote_location))
        self.remote_location = os.path.realpath(remote_location)
        return self.remote_location

    def process_parse(self, filename, print_code=True, print_outsider=False):
        """
        process_parse() : filename is reparsed with the language parser.
                          parsed result is displayed on stdout.
        print_code:    bool, control the printing of the code too.
        print_outsider: bool, control if we print outsider chunks too.
        """
        # filename is already parsed as libido input.
        # we have to parse it as itself
        p = self.factory.get_parser(filename)
        p.parse(filename)

        p.print_chunks(print_code, print_outsider)


def main():
    # command line processing
    arguments = docopt(get_usage(), version='0.2')
    if arguments['-q']:
        quiet(True)

    printerr(arguments)

    # build main object and give it parsed agurments
    # TODO: do not use arguments{} in libido class but pass them as argument
    # from main()
    l = libido(arguments)
    l.load_config(arguments['-c'])
    l.init_factory()

    # command line options
    action = None
    # destination, default 'None'
    dest = arguments['-o']

    if arguments['export']:
        if dest != 'None':
            raise RuntimeError('-o not supported with export')
        else:
            l.ensure_remote_access()
            action = 'export'

    if len(arguments['SOURCE_FILES']) > 0:
        # process filename's agrument, only the first for now
        filename = arguments['SOURCE_FILES'][0]
    else:
        # SOURCE_FILES will be set only for 'do', here falling back to SOURCE_FILE without S
        filename = arguments['SOURCE_FILE']

    printerr('filename=%s, dest=%s' % (filename, dest))

    # parse libido tokens only
    l.parse_input(filename)

    if action == 'export':
        l.process_export(filename)
    elif arguments['parse']:
        # -f print only functions, --outsider prints outsider too
        l.process_parse(filename, 
                print_code=(not arguments['-f']),
                print_outsider=arguments['--outsider']
                )
    else: # arguments['do'] default
        l.process_output(filename, dest)


if __name__ == '__main__':
    main()
