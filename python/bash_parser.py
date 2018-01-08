#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4:
#
# libido - python prototype
#
# bash_parser : parse a bash input file for libido collecing code
# or as a delegate class for bash input for libido_parser See libido_parser.analyze_line()

import sys
import re
import os

re.UNICODE
re.LOCALE

# local import
from rematcher import REMatcher
from helper import flat_line

class Bash_parser():
    def __init__(self, config, libido_parser):
        self.config = config
        self.lines = []
        self.libido_parser = libido_parser
        # See also init_parser() for other object properties

        # seting this bool at True will disable call to libido_parser.analyze_line()
        # can be used for testing without a real libido_parser or for local parsing
        # to disable modifing of libido_parser.token_map{}
        if libido_parser is None:
            self.ignore_libido_analyze = True
        else:
            self.ignore_libido_analyze = False

    def print_chunks(self):
        """
        print_chunks() : simple debug function
        """
        print("bash parser")
        for name, chunk in self.sorted_chunks():
            print("%s: start=%d, end=%d" % (
                name, chunk['start'], chunk['end']))
            for i in xrange(chunk['start'], chunk['end']+1):
                print(" %3d=> %s" % (i, self.lines[i-1].rstrip('\n')))

    def get_chunk(self, chunk_name, force_old=False):
        if not force_old and self.new_chunk.has_key(chunk_name):
            code = self.new_chunk[chunk_name]
        else:
            code = self.lines[self.chunks[chunk_name]['start']-1:self.chunks[chunk_name]['end']]
        return code

# old verbatim assignment with line delta
#-                if m.match(r'verbatim\(([^)]+)\)'):
#-                    collect = true
#-                    verbatim = m.group(1)
#-                    self.chunks[verbatim] = { 'start' : n+1 }
#-                elif m.match(r'\}') and collect:
#-                    self.chunks[verbatim]['end'] = n-1
#-                    collect = false
#-                    verbatim = none
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
        self.parsed_fname = None
        self.new_chunk = {}

    def parse(self, filename):
        self.init_parser()

        #open file in reading mode unicode
        f = open(filename, 'rU')
        self.parsed_fname = filename
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
                if not self.ignore_libido_analyze:
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

    def sorted_chunks(self):
        """
        sorted_chunks(): return a list of pair (chunk_name, code) in the same order
        as in the source code.
        """
        return [ (c, self.chunks[c]) for c in self.get_chunk_keys() ]

    def identify_chunk_outsider(self):
        """
        identify_chunk_outsider() : compare all chunks{} and lines[] to find line outside any chunks
        """
        outsider = 0
        self.outsider = []

        chunks =  self.sorted_chunks()
        current_l = 1

        for c, chunk in chunks:
            i = chunk['start']
            if i > current_l:
                outsider += 1
                outer_chunk = {'start' : current_l, 'end' : i - 1}
                self.chunks["outsider_%d" % outsider] = outer_chunk
                current_l = self.chunks[c]['end'] + 1

        end = len(self.lines)
        if  end > current_l:
            outer_chunk = {'start' : current_l, 'end' : end}
            outsider += 1
            self.chunks["outsider_%d" % outsider] = outer_chunk

    def write(self, dest = None):
        """
        write() : rebuild the parsed bash source to the same filename or a new one given by dest
        """
        if dest is None:
            dest = self.parsed_fname

        f = open(dest, 'wb')

        self.identify_chunk_outsider()
        chunks =  self.sorted_chunks()

        for c, chunk in chunks:
            if self.new_chunk.has_key(c):
                code = self.new_chunk[c]
            else:
                code = self.lines[chunk['start']-1:chunk['end']]
            f.write(flat_line(code))

        f.close()

    def update_chunk(self, chunk_name, parser):
        # get foreign chunks (same API as this parser)
        code_new = parser.get_chunk(chunk_name)
        code_old = self.get_chunk(chunk_name)

        if code_new == code_old:
            return False
        else:
            self.new_chunk[chunk_name] = code_new
            # keep the chunk from parsed chunk
            self.chunks[chunk_name]['updated'] = True
            return True

    def get_chunk_keys(self):
        """
        get_chunk_keys() : return the chunks name, as seen in the code.
        """
        chunk_names =  self.chunks.keys()
        # order as in the file
        chunk_names.sort(lambda a, b: cmp(self.chunks[a]['start'], self.chunks[b]['start']))

        return chunk_names

