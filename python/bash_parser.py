#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4:
#
# libido - python prototype
#
# bash_parser : parse a bash input file for collecting bloc of code in the
# libido context. For now, there's 3 kind of code bloc:
#   functions, or verbatim chunks and outsider.
#
# This parser also provide delegated methods for parsing verbatim input for libido_parser.
# See libido_parser.analyze_line()
#
# Line wise parser is able to parse whole functions bloc:
#
#  [function] name_of_the_function() {
#     # Match the function definiton in one line, anchored on the left (no indent).
#     # The opening brace is not parsed and can be on the next line.
#     # The Ending () are mendatory (not in bash) so we distinguish ^identifier of ^function_def().
#     # See the regexp for more accurate matching, in parse().
#
#     function body is collected until the closing unindented brace.
#  }
#
# The parser also identify 'outsider' which are anything else outside a
# function.
#
# verbatim libido bloc, defined in comment are also parsed, by using a libido
# parser. The libido_parser is given as constructor argument.
#
# It is not bash_parser's job to understand libido syntax, but it has to provide delegated methods.
# The Bash_parser doesn't know about dependancies, it is libido_parser's job.

import sys
import re
import os
from collections import OrderedDict

re.UNICODE
re.LOCALE

# local import
from rematcher import REMatcher
from helper import flat_line, printerr

class Bash_parser():
    def __init__(self, config, libido_parser):
        # TODO: remove config if not used
        self.config = config
        # a ref on the libido_parser, which can be None, See below.
        self.libido_parser = libido_parser

        # See also init_parser() for other object properties, created at parse
        # time.

        # seting this bool at True, will disable call to libido_parser.analyze_line()
        # can be used for testing without a real libido_parser or for local parsing
        # to disable modifing of libido_parser.token_map{}
        if libido_parser is None:
            self.ignore_libido_analyze = True
        else:
            self.ignore_libido_analyze = False

    def print_chunks(self, print_code=True, print_outsider=False):
        """
        print_chunks() : formated prints parsed chunks
        print_code : bool code will be printed
        print_outsider: bool, outsider will be identified and printed too
        """
        print("bash parser")

        # chunks are in order from chunks{} + new_chunk{}
        l = 0
        for name in self.get_chunk_keys(interleave_ousider=print_outsider):
            modified = False
            # override with new_chunk{} if any
            if self.new_chunk.has_key(name):
                start = l
                modified = True
            else:
                start = self.chunks[name]['start']

            code = self.get_chunk(name)
            end = start + len(code) - 1
            print("%s: start=%d, end=%d" % (name, start, end))

            if print_code:
                i = start
                for s in self.get_chunk(name):
                    print(" %3d=> %s" % (i, s.rstrip()))
                    i += 1

            # next l
            l = end + 2

            # our assertion check, no fail.
            if not modified:
                if l != self.chunks[name]['end']+2:
                    printerr('AssertionError: l=%d, end=%d' % (
                        l, self.chunks[name]['end']+2
                        ))


    def get_chunk(self, chunk_name, force_old=False):
        """
        get_chunk() : retrieve the lines of code for a chunk updated or not.
        return : an array of string (lines of code) from the parsed chunk.
                 or None if the chunk doesn't exists.
        force_old : can be used to read data from chunks{} (before update) instead
                    of new_chunk{}
        """
        # prefere reading in new_chunk
        if not force_old and self.new_chunk.has_key(chunk_name):
            code = self.new_chunk[chunk_name]
        else:
            if self.chunks.has_key(chunk_name):
                code = self.lines[self.chunks[chunk_name]['start']-1:self.chunks[chunk_name]['end']]
            else:
                code = None
        return code

    # parser helper for statement
    def verbatim_start(self, verbatim):
        if self.verbatim_collect:
            raise RuntimeError('parse error:%d: verbatim open nested found' % self.n)

        self.verbatim = verbatim
        self.verbatim_collect = True
        self.chunks[verbatim] = { 'start' : self.n }

    def verbatim_end(self):
        if self.verbatim_collect:
            self.chunks[self.verbatim]['end'] = self.n
            self.verbatim_collect = False
            self.verbatim = None
        else:
            raise RuntimeError('parse error:%d: verbatim close unmatched' % self.n)

    def init_parser(self):
        # some counters
        self.d = {
            'line_count' : 0,
            'comments' : 0,
            'empty' : 0,
            'libido' : 0,
            'function' : 0,
            'outsider' : 0,
        }

        # store chunk_name => {start:, end:} positions in lines of chunks parsed
        self.chunks = OrderedDict()
        # copy of the lines of the last parsed file
        self.lines = []

        # number of line parsed
        self.n = 0
        # store the last verbatim assign name during the parsing
        self.verbatim = None
        # for verbatim parsing, boolean for collecting lines
        self.verbatim_collect = False
        # copy of the last filename parsed
        self.parsed_filename = None
        # this dict contains list(string) (if update_chunk() is called)
        # this format differ from chunks{} which contains dict(start:, end:)
        self.new_chunk = OrderedDict()

        # collector for collecting outsider during parsing
        # for outsider, we start outside.
        # collected_end isn't needed
        self.collected_start = 1
        self.collecting = True
        # for numbering outsider
        self.outsider = 0

    # for outsider
    def start_collecting(self):
        self.collecting = True
        # we are called on some end (verbatim or function) so we will collect on
        # next line
        self.collected_start = self.n + 1

    def end_collecting(self, end=None):
        if not self.collecting:
            raise RuntimeError('end_collecting:%d: called while not collecting' % self.n)

        if end is None:
            end = self.n - 1

        if self.collected_start > end:
            # last ending called and the code is finished on a closing brace for
            # the last function.
            self.collecting = False
            # nothing to do
            return

        self.collecting = False
        outer_chunk = {
                'start' : self.collected_start,
                'end' : end,
                'is_outside' : True,
                }
        self.collected_start = -1
        # key: 3 digits starting by a number as shell function can't start by a
        # number
        self.outsider += 1
        key = "%03d_outsider" % self.outsider
        if self.chunks.has_key(key):
            raise RuntimeError("end_collecting:%d: key already exists '%s'" % (self.n, key))
        self.chunks[key] = outer_chunk
        # increase stats
        self.d['outsider'] += 1

    def parse(self, filename):
        self.init_parser()

        #open file in reading mode unicode
        f = open(filename, 'rU')
        self.parsed_filename = filename
        func_name = None
        # reading file (line by line)
        for line in f:
            self.n += 1
            self.d['line_count'] += 1
            m = REMatcher(line.rstrip('\n'))
            # line are stored with their \n
            self.lines.append(line)

            # match a libido tag
            # TODO: read libido tag from libido_parser
            if m.match(r'libido:'):
                self.d['libido'] += 1
                if not self.ignore_libido_analyze:
                    self.libido_parser.analyze_line(self, m)

            if m.match(r'^\s*#'):
                self.d['comments'] += 1
            elif m.match(r'^\s*$'):
                self.d['empty'] += 1
            elif m.match(r'^(function)?\s*([a-zA-Z][a-zA-Z0-9_]*)\s*\(\)'):
                self.end_collecting()
                self.d['function'] += 1
                func_name = m.group(2)
                self.chunks[func_name] = { 'start' : self.n }
            elif m.match(r'^\}') and func_name:
                self.start_collecting()
                self.chunks[func_name]['end'] = self.n
                func_name = None
                # it will collect on next line

        # for the last bloc
        if self.collecting:
            self.end_collecting(self.n)

        f.close()

        # return stats for unittests
        return self.d

    def write(self, dest = None):
        """
        write() : rebuild the parsed bash source to the same filename or a new one given by dest
        """
        if dest is None:
            # TODO: write via a tmpfile when overwriting
            dest = self.parsed_filename

        f = open(dest, 'wb')

        for c in self.get_chunk_keys(interleave_ousider=True):
            code = self.get_chunk(c)
            f.write(flat_line(code))

        f.close()

    def update_chunk(self, chunk_name, other):
        """
        update_chunk() : update a chunk in the parser, with the chunk from
        another parser. If the code_old doesn't exist, add the chunk as a new
        one.
        """
        # get foreign chunks (it must have the same API as this parser)
        code_new = other.get_chunk(chunk_name)
        code_old = self.get_chunk(chunk_name)

        if code_new == None:
            raise RuntimeError('update_chunk:error: chunk not found: %s' % chunk_name)

        if code_new == code_old:
            # same code, no update
            return False
        else:
            self.new_chunk[chunk_name] = code_new
            if code_old:
                # only updated if it was present before
                self.chunks[chunk_name]['updated'] = True
            return True

    def remove_outsider_key(self, k):
        """
        remove_outsider_key() : this is a filter function to be used to get
        chunk_name without outsider chunks.
        See: get_chunk_keys(interleave_ousider=True) for usage.
        """
        if self.chunks[k].has_key('is_outside'):
            return False
        else:
            return True

    def get_chunk_keys(self, interleave_ousider=False):
        """
        get_chunk_keys() : retrieve all parsed chunk_names.

        return: list(string), the chunks name ordered as seen in the code.
        interleave_ousider: bool, if True outsider chunks{} are given in
        good order too. When False (default) only libido parsed chunks are
        given.
        """
        if interleave_ousider:
            chunk_names = self.chunks.keys()
        else:
            chunk_names = filter(self.remove_outsider_key, self.chunks)

        # add chunk_names not present in chunks{} (added by update_chunk())
        for n in self.new_chunk.keys():
            if n not in chunk_names:
                chunk_names.append(n)

        # TODO: remove delete chunks

        return chunk_names

