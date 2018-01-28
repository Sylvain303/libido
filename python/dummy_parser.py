#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4:
#
# libido - python prototype
#
# dummy_parser a stupid parser just giving parser api
#
import re
from rematcher import REMatcher

re.UNICODE
re.LOCALE

class dummy_parser():
    def __init__(self, config, parser_factory):
        self.config = config
        self.parser_factory = parser_factory
        self.lines = []

    def parse(self, filename):
        # some counter
        self.d = {
                'line_count' : 0,
                'comment' : 0,
                'empty' : 0,
                'libido' : 0,
                }
        # reset
        self.line = []


        #open file in reading mode unicode
        f = open(filename, 'rU')
        # reading file (line by line)
        n = 0
        for line in f:
            n += 1
            self.d['line_count'] += 1
            m = REMatcher(line.rstrip('\n'))
            self.lines.append(line)

            if m.match(r'libido:'):
                self.d['libido'] += 1
            if m.match(r'^\s*#'):
                self.d['comment'] += 1
            elif m.match(r'^\s*$'):
                self.d['empty'] += 1

        f.close()

        return self.d

