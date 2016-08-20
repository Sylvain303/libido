#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4:
#
# libido - python prototype
#
# parser for libido embeded syntax, it uses subparser and parser_factory
#

from __future__ import print_function
import sys
import re
import glob
from collections import namedtuple

# local lib
sys.path.append('.')
from rematcher import REMatcher
from helper import printerr

re.UNICODE
re.LOCALE

def flat_line(list_of_lines):
    if isinstance(list_of_lines, str):
        list_of_lines = [ list_of_lines ]

    out = ''
    for l in list_of_lines:
        if isinstance(l, list):
            out += '\n'.join(l)
        else:
            if l[-1] == '\n':
                out += l
            else:
                out += l + '\n'
    return out

class libido_parser():
    def __init__(self, config, parser_factory):
        self.config = config
        # avoid libido open_marker match in this code itself
        self.open_marker = config.get('open_marker', 'libido' + ':')
        self.token_map = {}
        self.named_chunk = []
        self.expand_memo = {}
        self.lines = []
        self.parser_factory = parser_factory
        self.code_lib = {}
        self.chunks_resolved = {}

    def tokenize(self, m):
        """
        tokenize() : divide a libido line into recognized token

        token are variable:
            # libido# bash_code=bash(die, some_func)
            -> { action: assign, var: bash_code, parser: bash, args: [die, some_func] }
            # libido# expand bash_code
            -> { action: expand, args: bash_code }
        """
        if m.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([a-z_]+)\s*\(([^)]+)\)'):
            libido_token = namedtuple('libido_token', 'action var parser args')
            var = m.group(1)
            parser = m.group(2)
            args = [a.strip() for a in m.group(3).split(',')]
            return libido_token('assign', var, parser, args) 

        if m.match(r'expand\s+([a-zA-Z_][a-zA-Z0-9_]*)'):
            libido_token = namedtuple('libido_token', 'action args')
            args = m.group(1)
            # single arg
            return libido_token('expand', args) 

        if m.match(r'depend\s*\(([^)]+)\)'):
            libido_token = namedtuple('libido_token', 'action args')
            dependencies = [a.strip() for a in m.group(1).split(',')]
            return libido_token('depend', dependencies) 

        # example: libido# verbatim(bash_main) {
        if m.match(r'verbatim\s*\(([^)]+)\)\s*\{'):
            libido_token = namedtuple('libido_token', 'action args open close')
            verbatim = m.group(1)
            match_end = r'\s*\}'
            return libido_token('verbatim', verbatim, True, False) 

        # example: libido# }
        if m.match(r'\s*\}\s*$'):
            libido_token = namedtuple('libido_token', 'action args open close')
            return libido_token('verbatim', None, False, True) 

        # failure
        return None

    def need_to_find(self, named_chunk):
        self.named_chunk.append(named_chunk)

    def assign(self, num, var, val):
        self.token_map[var] = {'num' : num, 'val' : val }
        for s in val:
            self.need_to_find(s)

    def add_expansion(self, num, expand_name):
        l = self.expand_memo.get(expand_name)
        if l:
            l.append(num)
        else:
            self.expand_memo[expand_name] = [ num ]
        self.need_to_find(expand_name)

    def find_chunk(self, named_chunk):
        self.load_lib()
        c = self.chunks_resolved.get(named_chunk)
        if c:
            return c

        # self.code_lib is a dict of parser associated to files found
        # in config[lib_source]
        for f, p in self.code_lib.items():
            c = p.chunks.get(named_chunk)
            if c:
                # return a list of line
                self.chunks_resolved[named_chunk] = p.get_chunk(c)
                return self.chunks_resolved[named_chunk]
        return None

    def load_lib(self, force=False):
        """
        load_lib() 

            self.code_lib dict will contain a list of parser instancied to source code file 
            found in the 'lib_source' config parameter

            return int, number of entries in self.code_lib or -1 if not re-run
        """
        # if not forced run only once
        if not force and len(self.code_lib) > 0:
            return -1

        config_location = self.config.get('lib_source')
        if not config_location:
            raise RuntimeError("load_lib(): config_location not found no lib available")

        self.code_lib = {}
        n = 0
        for f in glob.glob(config_location):
            parser = self.parser_factory.get_parser(f)
            printerr("location=%s, type=%s" % (f, parser.name))
            parser.parse(f)
            self.code_lib[f] = parser
            n += 1

        return n

    def apply_chunk(self, named_chunk, chunk_of_code):
        where = self.expand_memo.get(named_chunk)
        # duplicate lines
        self.output = self.lines[:]
        for n in where:
            old_l = self.output[n-1]
            self.output[n-1] = [old_l, chunk_of_code ]

    def analyze_line(self, parser, matcher):
        """
        analyze_line() : parse a single line of libido code and collect info
        Called from inside languages parser only. See bash_parser.parse()
        """
        t = self.tokenize(matcher)

        if t:
            if t.action == 'verbatim' and t.open:
                parser.verbatim_start(t.args)
            elif t.action == 'verbatim' and t.close:
                parser.verbatim_end()

    def parse(self, filename):
        #open file in reading mode unicode
        f = open(filename, 'rU')
        # some counter
        self.d = {
                'line_count' : 0,
                'libido' : 0,
                }

        # reading file (line by line)
        n = 0
        for line in f:
            n += 1
            self.d['line_count'] += 1
            m = REMatcher(line.rstrip('\n'))
            self.lines.append(line)

            if m.match(self.open_marker):
                self.d['libido'] += 1

                p = self.tokenize(m)
                
                if p:
                    if p.action == 'assign':
                        self.assign(n, p.var, p.args)
                    elif p.action == 'expand':
                        self.add_expansion(n, p.args)
                    elif p.action == 'depend':
                        # in specific parser? ex: bash
                        pass
                else:
                    printerr('parsre error:%d:%s' % (n, line.rstrip()))

        f.close()
        return self.d

    def resolve_assignement(self):
        self.chunks_resolved = {}
        for var, info in self.token_map.items():
            self.chunks_resolved[var] = []
            for tok in info['val']:
                chunk_lines = self.find_chunk(tok)
                if chunk_lines:
                    self.chunks_resolved[var].append(flat_line(chunk_lines))
                else:
                    self.chunks_resolved[var].append('# missing: %s' % tok)

    def dump_result(self):
        self.resolve_assignement()

        for tok, places in self.expand_memo.items():
            chunk_lines = self.find_chunk(tok)
            if not chunk_lines:
                raise RuntimeError("named_chunk not found: %s" % tok)
            self.apply_chunk(tok, chunk_lines)

        out = ''
        for l in self.output:
            out += flat_line(l)

        return out
