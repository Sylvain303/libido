#!/usr/bin/python -
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4:
#
# libido - python prototype
#
# Parser for libido embeded syntax, it uses subparser and parser_factory.
#
# Libido syntax is line oriented. Parsing is done line by line. A libido
# statement is introduced by a libido marker (open_marker), followed by some
# libido code. Libido syntax can be embedded in foreign parser for delimiting
# blocs or for describring dependencies or naming exported_chucks. The line is
# analyzed by tokenize().
#
# How this parser works:
#
# libido_parser stores token encountered during parsing in token_map{} both
# chunk_name with their dependency if any, and var_name assignment which are
# also empty chunk dependant of other chunks.
#
# The config gives external information to retrieve chunks in a lib_source
# repository. The repository must have a local copy available.
#

from __future__ import print_function
import sys
import re
import glob
from collections import namedtuple

# local lib
from rematcher import REMatcher
from helper import printerr, flat_line

re.UNICODE
re.LOCALE

symbol = namedtuple('symbol', 'tsym deps')

class libido_parser():
    def __init__(self, config, parser_factory):
        self.config = config
        # config is libido section of a ConfigParser object, as well as a simple dict
        # (avoid libido open_marker match in this code itself)
        self.open_marker = config.get('open_marker', 'libido' + ':')

        # parser_factory creates itself libido_parser
        self.parser_factory = parser_factory
        self.reset_parser()

    def reset_parser(self):
        # token_map{} store by chunk names, with dependency as array
        self.token_map = {}
        # expand_memo{} store where expansion will occur.
        # keys are chunk_names pointing to list(int) index (starting at 1) in lines[] or output[]
        self.expand_memo = {}
        # input lines after parse()
        self.lines = []
        # copy of lines[] after dump_result() with expanded chunks (not flatten)
        # TODO: should it be reseted here?
        self.output = []
        self.code_lib = {}
        self.chunks_resolved = {}
        self.chunks_dep = {}
        # store a list(string) chunk_name if some are parsed
        self.exported_chucks = None
        self.parsed_filename = None

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

        # libido# expand token_name
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

        # closing brass of the verbatim statement above
        # libido# }
        # -> { action: verbatim, args: None, open=False, close=True }
        if m.match(r'\s*\}\s*$'):
            libido_token = namedtuple('libido_token', 'action args open close')
            return libido_token('verbatim', None, False, True)

        # libido# export(item, item2, ...)
        # -> { action: export, args: [item, item2, ...] }
        if m.match(r'export\s*\(([^)]+)\)'):
            args = [a.strip() for a in m.group(1).split(',')]
            libido_token = namedtuple('libido_token', 'action args')
            return libido_token('export', args)

        # no match, no libido token recognized
        return None

    def assign(self, chunk_name, deps):
        """
        assign() : wraps token_map{} assignment, use it for assigning token and
        dependencies.
        """
        self.token_map[chunk_name] = symbol(tsym='var', deps=deps)

    def add_dependency(self, top_func, deps):
        """
        add_dependency() : add or append dependency to a token.
        Which means that if top_func is expanded, it will also expand once, all
        related chunks in deps.  See apply_chunk()

        top_func: string, this token depends on deps. All are chunk_names.
        deps: list, other chunk_name which are needed by top_func.

        Modified: 
          token_map{}
        """
        if top_func in self.token_map:
            self.token_map[top_func].deps.extend(deps)
        else:
            # not an assign (ie: no line num)
            self.token_map[top_func] = symbol(tsym='chunk', deps=deps)
        # add all deps symbols without dependency
        for name in deps:
            if name not in self.token_map:
                self.token_map[name] = symbol(tsym='chunk', deps=[])

    def get_dep(self, chunk_name, rec_seen = None, not_me=False):
        """
        get_dep() : return a list which are the dependencies looked up recursivly from token_map{}

        return: list(string), can be empty []
        chunk_name: string, the token to look for.
        rec_seen: dict, do not use, it is a recursiv collector (self initialized)
        not_me: bool, remove chunk_name from the resulting list, present by default.
        """
        if rec_seen is None:
            rec_seen = {}

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

        # return an unordered list of chunk_name
        if not_me:
            return list(uniq_dep - set([chunk_name]))
        else:
            return list(uniq_dep)

    def add_expansion(self, num, expand_name):
        """
        add_expansion() : store an expansion request at the given line

        num: int, line number in lines[num-1] of the requested expansion.
        expand_name: string, the chunk_name to look for.

        Modified: expand_memo{}
        """
        l = self.expand_memo.get(expand_name)
        if l:
            l.append(num)
        else:
            self.expand_memo[expand_name] = [ num ]

    def find_chunk(self, chunk_name):
        """
        find_chunk() : look into 'lib_source' to find chunk_name. Returns a dict
        containing its starts line, so it can be ordered, and the parsed code.

        return: dict, or None
        chunk_name: string
        """
        # after load_lib() code_lib{} contains parsed lib, See load_lib()
        # TODO: don't call load_lib() here, ensure it is called before.
        self.load_lib()

        for fname, p in self.code_lib.items():
            if p.chunks.has_key(chunk_name):
                # lines is a list of str
                # TODO: try to use OrderedDict to be free of ordering
                return {
                         'start' : p.chunks[chunk_name]['start'],
                         'lines' : p.get_chunk(chunk_name),
                       }
        return None

    def load_lib(self, force=False, input_list_to_parse=None):
        """
        load_lib() : load internal lib of code associated with libido.conf. The
        code is cached, use force=True to reload.

        return: int, number of entries in code_lib{} or -1 if not re-run
        force: bool, force reloading
        input_list_to_parse: None or list(string), filenames to parse as our lib. Alaways force=True.

        Modified:
          code_lib{}: is reseted and will contain a list of parser instancied with the source code file
          found in the 'lib_source' config parameter.
        """
        if input_list_to_parse:
          force = True
        else:
          input_list_to_parse = []

        # if not forced run only once
        if not force and len(self.code_lib) > 0:
            # use cached parser
            return -1

        if len(input_list_to_parse) == 0:
          # by default, we read the list of file in our lib from the config.
          # It can be forced to a specific list of filename. Only those filenames will by parsed ignoring
          # config_location.
          config_location = self.config.get('lib_source')
          if not config_location:
              raise RuntimeError("load_lib(): 'lib_source' not found, no lib available")
          input_list_to_parse.extend(glob.glob(config_location))

        # reset
        self.code_lib = {}
        n = 0
        # loop over local files in config_location
        for f in input_list_to_parse:
            code_parser = self.parser_factory.get_parser(f)
            printerr("location=%s, type=%s" % (f, code_parser.name))
            code_parser.parse(f)
            self.code_lib[f] = code_parser
            n += 1

        return n

    def apply_chunk(self, chunk_name, chunk_of_code):
        """
        apply_chunk(): called during token expansion, replace the line in the
        output with the given chunk_of_code. The current line which is a libido
        statement it conserved above the expanded code.

        chunk_name: string, the reference token in expand_memo{}
        chunk_of_code: string, or list(string)

        Modified:
            output[] : some are replaced with chunk_of_code as string => list(string)
        """
        where = self.expand_memo.get(chunk_name)
        for n in where:
            old_l = self.output[n-1]
            self.output[n-1] = [old_l, chunk_of_code ]

    def analyze_line(self, parser, matcher):
        """
        analyze_line() : parse a single line of libido code and collect info
        Called from inside languages parser only. See bash_parser.parse()

        parser: parser_object (ex: Bash_parser)
        matcher: REMatcher object

        Note: parser must provide the following methods:
        verbatim_start() verbatim_end() add_dependency()
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
        """
        parse() : parses an input file name, and fill the token_map{} and
        expand_memo{}. This kind of input, it intended for expansion (expand) or
        for holding lib_source with dependencies (depend).

        return: dict, parsing statistic for unittests

        filename: string
        """
        self.reset_parser()

        #open file in reading mode unicode
        f = open(filename, 'rU')
        self.parsed_filename = filename
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
                        # depend in libido_parser is not associated with
                        # a syntax. We ignore it. See: analyze_line()
                        #printerr('parse:%d:dependencies found %s ??' % (n, line.rstrip()))
                        pass
                    elif p.action == 'export':
                        # create it
                        if not self.exported_chucks:
                            self.exported_chucks = []

                        for e in p.args:
                            # no duplicate
                            if e not in self.exported_chucks:
                                self.exported_chucks.append(e)
                            else:
                                printerr("export: duplicate export '%s'" % (e))
                    else:
                        printerr("parser error: don't know how to handle action: %s" % p.action)
                else:
                    printerr('parse error:%d:%s' % (n, line.rstrip()))

        f.close()
        return self.d

    def resolve_dependancies(self, auto_parse_input=False):
        """
        resolve_dependancies() : with a parsed libido file, look into token_map{} in order to resolve all dependencies.

        return: dict, ref to resolved_dep{} for unittests
        raise: RuntimeError
        auto_parse_input: bool, by default load our lib, and we do not look for content in the file parsed itself. If
                          True, ignores our lib and use the parsed_filename instead.

        Modified:
          resolved_dep{}: reseted, maps chunk_name => list(string) OR dict(deps:, lines:, start:)
                          All dependencies are resolved, including chunk_name without dependencies which will have a
                          single dependency on itself.
          missing[]: list(string) unfound chunk_name which must be empty or an exception is raised.
        """
        if auto_parse_input == False:
            self.load_lib()
        else:
            self.load_lib(input_list_to_parse=[self.parsed_filename])

        var = []
        self.resolved_dep = {}
        self.missing = []
        for name, symb in self.token_map.items():
            if symb.tsym == 'var':
                var.append(name)
                continue

            if name in self.resolved_dep:
                continue

            # recursivly resolves this chunk_name
            self.sub_dep_resolve(name)

        for v in var:
            deps = self.token_map[v].deps
            missed = 0
            for d in deps:
                if d not in self.resolved_dep:
                    missed += 1
                    self.missing.append(d)
            if not missed:
                # expand all deps once
                expand_deps = set(deps)
                for d in deps:
                    expand_deps.update(self.get_dep(d))
                self.resolved_dep[v] = list(expand_deps)

        if len(self.missing) > 0:
            raise RuntimeError('missing dependencies: %s' % ', '.join(self.missing))

        # returned for debuging purpose
        return self.resolved_dep

    def sub_dep_resolve(self, chunk_name, seen = None):
        """
        sub_dep_resolve() : recursivly resolve all deps for chunk_name into resolved_dep{} add missing deps in missing[]

        chunk_name: string to look for
        seen: an internal recursive set(), don't use it, it is passed recursivly by the method.

        Modified:
          resolved_dep{}: token with dependencies now have an extra key 'deps' => list(string)
          missing[]: may have more missing chunk_name
        """
        if seen is None:
            seen = set()
        if chunk_name in seen:
            return

        seen.add(chunk_name)
        more_dep = self.get_dep(chunk_name)
        for tok in more_dep:
            if tok in self.resolved_dep:
                continue

            c = self.find_chunk(tok)
            if c:
                # c is a dict(start:, lines:) built by find_chunk()
                self.resolved_dep[tok] = c
            else:
                self.missing.append(tok)

            # resolve sub deps recursivly
            for sub in self.get_dep(tok, not_me=True):
                self.sub_dep_resolve(sub, seen)

        self.resolved_dep[chunk_name]['deps'] = more_dep

    def order_chunk(self, list_deps):
        """
        order_chunk() : order records in list_deps based on their 'start'
        postion.

        return: list(dict(start:)) a copy of list_deps (list_deps unchanged)
        list_deps: list(string), which must be key pointing in resolved_dep{}
        """
        # duplicate list_deps[]
        copy_deps = list_deps[:]
        # TODO: DRY this key sorting with bash_parser.get_chunk_keys()
        copy_deps.sort(lambda a, b:
                cmp(self.resolved_dep[a]['start'], self.resolved_dep[b]['start']))
        return copy_deps

    def dump_result(self):
        """
        dump_result() : after the main code has been parsed, apply the algorithm to dump all the resulting code:
            - resolve_dependancies() will find all the chunks from token_map{} with dependencies.
            - loop over expand_memo{} will retrieve and merge together all chunk_of_code recursivly.
            - apply_chunk() will replace in the output[]
        return: string, the generated code fatten
        Modified:
            token_map{} is filled with resolved dependencies
            output[] contains expanded lines of code, not flatten
        """
        self.resolve_dependancies()

        # duplicate input lines
        self.output = self.lines[:]

        # prevent multiple expansion
        # TODO: could OderedDict also achive that better?
        self.chunk_expanded = set()

        # look for all places in the code where to expand some code, and perform expansion in output[] via apply_chunk()
        for tok in self.expand_memo.keys():
            all_chunk = self.get_resolved_dep(tok)
            if all_chunk:
                self.apply_chunk(tok, all_chunk)

        # concatenate all lines flatten
        out = ''
        for l in self.output:
            out += flat_line(l)

        return out

    def get_resolved_dep(self, chunk_name):
        
        c = self.resolved_dep.get(chunk_name)
        all_chunk = []
        # c can be a list (tsym=var) or a dict (tsym=chunk)
        # TODO: make it the same object remove isinstance() testing
        if isinstance(c, list):
            # deps (list of recursive deps) are expanded by resolve_dependancies()
            deps = self.order_chunk(c)
            # line expansion will happen in the next loop
            all_chunk.append('# expanded from: %s => %s' % (chunk_name, ','.join(c)))
        else:
            if chunk_name in self.chunk_expanded:
                return None
            # add all deps + itself
            deps = c.get('deps', [])
            deps = self.order_chunk(deps)

        # fetch sub dependencies if any
        for d in deps:
            if d in self.chunk_expanded:
                return None
            # will raise an exception if d is not in resolved_dep{}
            all_chunk.extend(self.resolved_dep[d]['lines'])
            # done for this chunk
            self.chunk_expanded.add(d)

        return all_chunk
