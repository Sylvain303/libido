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
from collections import OrderedDict

re.UNICODE
re.LOCALE

# local import
from rematcher import REMatcher
from helper import flat_line, printerr

class Bash_parser():
    def __init__(self, config, libido_parser):
        self.config = config
        # store copy of the parsed lines
        self.lines = []
        # a ref on the libido_parser, which can be None, See below.
        self.libido_parser = libido_parser
        # See also init_parser() for other object properties

        # seting this bool at True will disable call to libido_parser.analyze_line()
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
        """
        print("bash parser")

        if print_outsider:
            self.identify_chunk_outsider()

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
        # some counters
        self.d = {
            'line_count' : 0,
            'comments' : 0,
            'empty' : 0,
            'libido' : 0,
            'function' : 0,
        }

        # store chunk_name => {start:, end:} positions in lines of chunks parsed
        self.chunks = OrderedDict()
        # copy of the lines of the last parsed file
        self.lines = []

        # number of line parsed
        self.n = 0
        # store the last verbatim assign name during the parsing
        self.verbatim = None
        # for verbatim parsing, boolean for collecing lines
        self.collect = False
        # copy of the last filename parsed
        self.parsed_fname = None
        # this dict contains list(string) (if update_chunk() is called)
        # this format differ from chunks{} which contains dict(start:, end:)
        self.new_chunk = OrderedDict()

    def parse(self, filename):
        self.init_parser()

        #open file in reading mode unicode
        f = open(filename, 'rU')
        self.parsed_fname = filename
        func_name = None
        # reading file (line by line)
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

    def identify_chunk_outsider(self):
        """
        identify_chunk_outsider() : compare all chunks{} and lines[] to find
        bloc of lines outside of any chunks.

        It is safe to call this method multiple time, as all gap are filled at
        first call. So no gap could be filled twice.

        new_chunk{} is not considered, as it will replace chunk inplace via
        get_chunk(). And added chunk will be appended in get_chunk_keys()

        Modified:
        chunks{} : will be rebuild with additional keys 'outsider_%d' => outer_chunk{}
                   The order will be modified as outsider interleave with chunk_names.
                   outsider are numbered starting at 1.
        """
        outsider = 0
        current_l = 1
        new_ordered_chunks = OrderedDict()

        # loop over current chunks and find un-collected gap
        for c in self.chunks.keys():
            # TODO: care of new_chunk{} ? size may differ or could be deleted
            chunk_start = self.chunks[c]['start']
            if chunk_start > current_l:
                outer_chunk = {
                        'start' : current_l,
                        'end' : chunk_start - 1,
                        'is_outside' : True,
                        }
                outsider += 1
                new_ordered_chunks["outsider_%d" % outsider] = outer_chunk
                # continue after the chunk
                current_l = self.chunks[c]['end'] + 1

            # copy chunk ref
            new_ordered_chunks[c] = self.chunks[c]

        # all chunks are interleaved with outsider, or none if there's no chunk.
        # We check if a code bloc is left at the ending of the file.
        end = len(self.lines)
        if end > current_l:
            outer_chunk = {
                    'start' : current_l,
                    'end' : end,
                    'is_outside' : True,
                    }
            outsider += 1
            new_ordered_chunks["outsider_%d" % outsider] = outer_chunk

        # we repalce with the new built OrderedDict
        self.chunks = new_ordered_chunks

        # could be used in unittests
        return outsider

    def write(self, dest = None):
        """
        write() : rebuild the parsed bash source to the same filename or a new one given by dest
        """
        if dest is None:
            dest = self.parsed_fname

        f = open(dest, 'wb')

        # Note: the call on identify_chunk_outsider() alter chunks{}
        self.identify_chunk_outsider()
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
        get_chunk_keys() : return a list, the chunks name ordered as seen in the
        code.
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

