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
            out += '\n'.join([ ll.rstrip() for ll in l])
        else:
            if l[-1] == '\n':
                out += l
            else:
                out += l + '\n'
    return out

symbol = namedtuple('symbol', 'var chunk deps')

class libido_parser():
    def __init__(self, config, parser_factory):
        self.config = config
        # avoid libido open_marker match in this code itself
        self.open_marker = config.get('open_marker', 'libido' + ':')

        # token_map{} store by chunk names, with dependency as array
        self.token_map = {}
        # expand_memo{} store where expandsion will occur
        self.expand_memo = {}
        # input lines
        self.lines = []
        # parser_factory creates itself libido_parser
        self.parser_factory = parser_factory
        self.code_lib = {}
        self.chunks_resolved = {}
        self.chunks_dep = {}

    def tokenize(self, m):
        """
        tokenize() : divide a libido line into recognized token, or return None
        returned token are variable: See code below in libido_token(()
        """
        # libido# bash_code=bash(die, some_func)
        # -> { action: assign, var: bash_code, parser: bash, args: [die, some_func] }
        if m.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([a-z_]+)\s*\(([^)]+)\)'):
            libido_token = namedtuple('libido_token', 'action var parser args')
            var = m.group(1)
            parser = m.group(2)
            args = [a.strip() for a in m.group(3).split(',')]
            return libido_token('assign', var, parser, args)

        # libido# expand bash_code
        # -> { action: expand, args: bash_code }
        if m.match(r'expand\s+([a-zA-Z_][a-zA-Z0-9_]*)'):
            libido_token = namedtuple('libido_token', 'action args')
            args = m.group(1)
            # single arg
            return libido_token('expand', args)

        # libido# depend test_tool(die, eecho)
        # -> { action: depend, what: test_tool, args: [die, eecho] }
        if m.match(r'depend\s*([a-zA-Z_0-9]+)\s*\(([^)]+)\)'):
            libido_token = namedtuple('libido_token', 'action what args')
            what = m.group(1)
            dependencies = [a.strip() for a in m.group(2).split(',')]
            return libido_token('depend', what, dependencies)

        # libido# verbatim(bash_main) {
        # -> { action: verbatim, args: bash_main, open=True, close=False }
        if m.match(r'verbatim\s*\(([^)]+)\)\s*\{'):
            libido_token = namedtuple('libido_token', 'action args open close')
            verbatim = m.group(1)
            match_end = r'\s*\}'
            return libido_token('verbatim', verbatim, True, False)

        # libido# }
        # -> { action: verbatim, args: None, open=False, close=True }
        if m.match(r'\s*\}\s*$'):
            libido_token = namedtuple('libido_token', 'action args open close')
            return libido_token('verbatim', None, False, True)

        # failure
        return None

    def assign(self, chunk_name, deps):
        self.token_map[chunk_name] = symbol(var=True, chunk=False, deps=deps)

    def add_dependency(self, top_func, deps):
        """
        add_dependency() : top_func will depend on deps. all are chunk_names
        Which means that top_func, if expanded, will also expand once all related chunks in deps
        See apply_chunk()
        """
        if top_func in self.token_map:
            self.token_map[top_func].deps.extend(deps)
        else:
            # not an assign (ie: no line num)
            self.token_map[top_func] = symbol(var=False, chunk=True, deps=deps)
        # add all deps symbols without dependency
        for name in deps:
            if name not in self.token_map:
                self.token_map[name] = symbol(var=False, chunk=True, deps=[])

    def get_dep(self, chunk_name, rec_seen = {}):
        """
        get_dep() : return dependencies list looked up recursivly from token_map{}
        """
        if chunk_name in rec_seen:
            return []

        try:
            deps = self.token_map[chunk_name].deps
        except KeyError:
            raise RuntimeError("chunk_name '%s' not found in token_map" % chunk_name)

        # the chunk_name is included in its dep itself
        uniq_dep = set([chunk_name])
        for d in deps:
            # recursiv call
            uniq_dep.update(self.get_dep(d, uniq_dep))
            uniq_dep.add(d)

        # unordered list of chunk_name
        return list(uniq_dep)

    def add_expansion(self, num, expand_name):
        l = self.expand_memo.get(expand_name)
        if l:
            l.append(num)
        else:
            self.expand_memo[expand_name] = [ num ]

    def find_chunk(self, chunk_name):
        """
        find_chunk() : look into 'lib_source' to find the chunk_name, and its line of start
        """
        # after load_lib() code_lib{} contains parsed lib, See load_lib()
        self.load_lib()

        for fname, p in self.code_lib.items():
            # c is a chunks ref { start: , end: }
            c = p.chunks.get(chunk_name)
            if c:
                # lines is a list of str
                return { 'start' : c['start'] , 'lines' : p.get_chunk(c) }
        return None

    def load_lib(self, force=False):
        """
        load_lib()

            code_lib{} will contain a list of parser instancied with the source code file
            found in the 'lib_source' config parameter

            return int, number of entries in code_lib{} or -1 if not re-run
        """
        # if not forced run only once
        if not force and len(self.code_lib) > 0:
            return -1

        config_location = self.config.get('lib_source')
        if not config_location:
            raise RuntimeError("load_lib(): 'lib_source' not found, no lib available")

        self.code_lib = {}
        n = 0
        for f in glob.glob(config_location):
            parser = self.parser_factory.get_parser(f)
            printerr("location=%s, type=%s" % (f, parser.name))
            parser.parse(f)
            self.code_lib[f] = parser
            n += 1

        return n

    def apply_chunk(self, chunk_name, chunk_of_code):
        where = self.expand_memo.get(chunk_name)
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
            elif t.action == 'depend':
                self.add_dependency(t.what, t.args)

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
                        self.assign(p.var, p.args)
                    elif p.action == 'expand':
                        self.add_expansion(n, p.args)
                    elif p.action == 'depend':
                        # in specific parser? ex: bash
                        printerr('parse:%d:dependencies found %s ??' % (n, line.rstrip()))
                        pass
                else:
                    printerr('parsre error:%d:%s' % (n, line.rstrip()))

        f.close()
        return self.d

    def resolve_dependancies(self):
        self.load_lib()
        var = []
        self.resolved_dep = {}
        missing = []
        for name, symb in self.token_map.items():
            if symb.var:
                var.append(name)
                continue

            if name in self.resolved_dep:
                continue

            if len(symb.deps) == 0:
                self.resolved_dep[name] = []
            else:
                more_dep = self.get_dep(name)
                for tok in more_dep:
                    if tok in self.resolved_dep:
                        continue

                    c = self.find_chunk(tok)
                    if c:
                        self.resolved_dep[tok] = c
                    else:
                        missing.append(tok)
                self.resolved_dep[name]['deps'] = more_dep
                self.resolved_dep[name]['deps'].remove(name)

        for v in var:
            deps = self.token_map[v].deps
            missed = 0
            for d in deps:
                if d not in self.resolved_dep:
                    missed += 1
                    missing.append(d)
            if not missed:
                self.resolved_dep[v] = deps

        if len(missing) > 0:
            raise RuntimeError('missing dependencies: %s' % ', '.join(missing))
    
        # recursive deps are not resolved
        return self.resolved_dep

    def dump_result(self):
        """
        dump_result() : after the main code has been parsed, apply the algorithm to dump all the resulting code:
            resolve_dependancies() will find all the chunks from token_map{} with dependencies
            loop over expand_memo{} will retrieve and merge together all chunk_of_code
            apply_chunk() will replace in the output[]
        """
        self.resolve_dependancies()

        # duplicate lines
        self.output = self.lines[:]

        for tok, places in self.expand_memo.items():
            c = self.resolved_dep.get(tok)
            if isinstance(c, list):
                all_chunk = []
                # sub fetch dependencies
                for d in c:
                    all_chunk.extend(self.resolved_dep.get(d)['lines'])
            else:
                all_chunk = c['lines']
                for d in c.get('deps', []):
                    all_chunk.extend(self.resolved_dep.get(d)['lines'])

            self.apply_chunk(tok, all_chunk)

        # concatenate all lines faltten
        out = ''
        for l in self.output:
            out += flat_line(l)

        return out
