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
import magic
import os

# add parser here + __init__ + detect
import bash_parser
import dummy_parser
import libido_parser

class parser_factory():
    def __init__(self, configparser):
        self.config = configparser
        self.parsers = { 
                'bash' : bash_parser.Bash_parser,
                'dummy' : dummy_parser.dummy_parser,
                }

        # inter dependant parser, we share config and the factory
        self.libido_parser = libido_parser.libido_parser(self.config['libido'], self)

    def detect(self, filename):
        if re.search(r'\.(sh|bash)$', filename):
            return 'bash'
        elif re.search(r'^[^.]+$', os.path.basename(filename)):
            # no extension
            m = magic.open(magic.MAGIC_NONE)
            m.load()
            typef = m.buffer(open(filename).read())
            if re.search(r'Bourne-Again shell script', typef):
                return 'bash'

        return 'dummy'

    def get_parser(self, filename, type_parser=None):
        if filename and not type_parser:
            # default behavior
            file_type = self.detect(filename)
        elif type_parser and not filename:
            file_type = type_parser
        else:
            raise RuntimeError('get_parser: filename or type_parser')

        parser = self.parsers.get(file_type)

        # attribute itself so a parser can create another parser
        p =  parser(self.config['libido'], self.libido_parser)
        p.name = file_type

        return p
