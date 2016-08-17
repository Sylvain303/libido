#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4:
#
# libido - python prototype
#
# parser for libido embeded syntax:
#
# libido: bash_code=bash(die, docopts)
# libido: expand bash_code

from __future__ import print_function
import sys
import re
import os
from collections import namedtuple

# local lib
sys.path.append('.')
from rematcher import REMatcher

re.UNICODE
re.LOCALE

class libido_parser():
    def __init__(self, config, open_marker = 'libido:'):
        self.config = config
        self.open_marker = config.get('open_marker', open_marker)
        self.token_map = {}
        self.named_chunk = []
        self.expand_memo = {}
        self.lines = []

    def tokenize(self, m):
        if m.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([a-z_]+)\(([^)]+)\)'):
            var = m.group(1)
            parser = m.group(2)
            args = [a.strip() for a in m.group(3).split(',')]
            libido_token = namedtuple('libido_token', 'action var parser args')
            return libido_token('assign', var, parser, args) 

        if m.match(r'expand\s+([a-zA-Z_][a-zA-Z0-9_]*)'):
            expand_arg = m.group(1)
            libido_token = namedtuple('libido_token', 'action expand_arg')
            return libido_token('expand', expand_arg) 

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

        # fetch outside ref
        # merge ref in assign if any
        return None

    def load_lib(self):
        config_location = self.config.get('lib_source')
        for l in config_location:
            # open l as file or dir
        return None

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
        collect = False
        verbatim = None
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
                        self.add_expansion(n, p.expand_arg)
                else:
                    print('error:%d:%s' % (n, line.rstrip()))

        f.close()

        return self.d


    def dump_result(self):
        for tok in self.named_chunk:
            chunk = self.find_chunk(tok)
            if chunk:
                pass

        for l in self.lines:
            print(l, end='')
