#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4:
#
# libido - python prototype
#
# bash_parser : parse a bash input file for libido collecing code
# or for bash input for libido_parser

import sys
import re
import os

re.UNICODE
re.LOCALE

# local import
from rematcher import REMatcher
import libido_parser

class Bash_parser():
    def __init__(self, config, parser_factory):
        self.config = config
        # not used
        self.parser_factory = parser_factory
        self.lines = []
        self.libido_parser = libido_parser.libido_parser(config, parser_factory)

    def print_chunks(self):
        for name in self.chunks:
            print "%s: start=%d, end=%d" % (
                name, self.chunks[name]['start'], self.chunks[name]['end'])
            for i in xrange(self.chunks[name]['start'], self.chunks[name]['end']+1):
                print " %3d=> %s" % (i, self.lines[i-1].rstrip('\n'))

    def get_chunk(self, chunk_ref):
        chunk_lines = []
        for i in xrange(chunk_ref['start'], chunk_ref['end']+1):
            # keep newlines
            chunk_lines.append(self.lines[i-1])
        return chunk_lines

    def verbatim_start(self, verbatim):
        if self.collect:
            raise RuntimeError('parse error:%d: verbatim open nested found' % self.n)

        self.verbatim = verbatim
        self.collect = True
        self.chunks[verbatim] = { 'start' : self.n }

    def verbatim_end(self):
        if self.collect:
            self.chunks[self.verbatim]['end'] = self.n
            self.collect = False
            self.verbatim = None
        else:
            raise RuntimeError('parse error:%d: verbatim close unmatched' % self.n)

    def init_parser(self):
        # some counter
        self.d = {
            'line_count' : 0,
            'comments' : 0,
            'empty' : 0,
            'libido' : 0,
            'function' : 0,
        }

        self.chunks = {}
        self.lines = []

        # reading file (line by line)
        self.n = 0
        self.verbatim = None
        self.collect = False

    def parse(self, filename):
        self.init_parser()

        #open file in reading mode unicode
        f = open(filename, 'rU')
        func_name = None
        for line in f:
            self.n += 1
            self.d['line_count'] += 1
            m = REMatcher(line.rstrip('\n'))
            # line are stored with their \n
            self.lines.append(line)

            # match a libido tag
            if m.match(r'libido:'):
                self.d['libido'] += 1
                self.libido_parser.analyze_line(self, m)

            if m.match(r'^\s*#'):
                self.d['comments'] += 1
            elif m.match(r'^\s*$'):
                self.d['empty'] += 1
            elif m.match(r'^(function)?\s*([a-zA-Z][a-zA-Z0-9_]*)\s*\(\)'):
                self.d['function'] += 1
                func_name = m.group(2)
                self.chunks[func_name] = { 'start' : self.n }
            elif m.match(r'^\}') and func_name:
                self.chunks[func_name]['end'] = self.n
                func_name = None

        f.close()

        return self.d
