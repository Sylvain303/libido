#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4:
#
# libido - python prototype
#
# factory to detect language type and create parser
#
# Usage:
#    import parser_factory
#    conf = { 'lib_source' : 'some/path/to/your/lib' }
#    f = parser_factory.parser_factory(conf)
#    a_parser = f.get_parser(some_file_to_parse)
#    a_parser.parse(some_file_to_parse)

import re

# add parser here + __init__ + detect
import bash_parser
import dummy_parser

class parser_factory():
    def __init__(self, config):
        self.config = config
        self.parsers = { 
                'bash' : bash_parser.Bash_parser,
                'dummy' : dummy_parser.dummy_parser,
                }

    def detect(self, filename):
        if re.search(r'\.(sh|bash)$', filename):
            return 'bash'
        else:
            return 'dummy'

    def get_parser(self, filename):
        file_type = self.detect(filename)

        parser = self.parsers.get(file_type)

        # attribute itself so a parser can create another parser
        p =  parser(self.config, self)
        p.name = file_type

        return p
