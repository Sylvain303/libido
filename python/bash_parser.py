#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# vim: set et ts=2 sw=2 sts=2:
#
# libido - python prototype
#
# ouput - Comment / matched function and verbatim blocks / lines of code matched
# can be filtered with: | grep '^[^ #]'
# Usage: python bash_parser.py ../examples/libido/shell_lib.bash | grep '^[^# ]'

import sys
import re
import os

re.UNICODE
re.LOCALE

class REMatcher(object):
    def __init__(self, matchstring):
        self.line = matchstring

    def match(self,regexp):
        self.rematch = re.search(regexp, self.line)
        return bool(self.rematch)

    def group(self,i):
        return self.rematch.group(i)

class Bash_parser():
  def print_chunks(self):
    for name in self.chunks:
      print "%s: start=%d, end=%d" % (
        name, self.chunks[name]['start'], self.chunks[name]['end'])
      for i in xrange(self.chunks[name]['start'], self.chunks[name]['end']+1):
        print " %3d=> %s" % (i, self.lines[i-1].rstrip('\n'))

  def parse(self, filename):
    #open file in reading mode unicode
    f = open(filename, 'rU')
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
    n = 0
    func_name = None
    collect = False
    verbatim = None
    for line in f:
      n += 1
      self.d['line_count'] += 1
      m = REMatcher(line.rstrip('\n'))
      self.lines.append(line)

      if m.match(r'libido:'):
        self.d['libido'] += 1
        if m.match(r'verbatim\(([^)]+)\)'):
          collect = True
          verbatim = m.group(1)
          self.chunks[verbatim] = { 'start' : n+1 }
        elif m.match(r'\}') and collect:
          self.chunks[verbatim]['end'] = n-1
          collect = False
          verbatim = None

      if m.match(r'^\s*#'):
        self.d['comments'] += 1
      elif m.match(r'^\s*$'):
        self.d['empty'] += 1
      elif m.match(r'^(function)?\s*([a-zA-Z][a-zA-Z0-9_]*)\s*\(\)'):
        self.d['function'] += 1
        func_name = m.group(2)
        self.chunks[func_name] = { 'start' : n }
      elif m.match(r'^\}') and func_name:
        self.chunks[func_name]['end'] = n
        func_name = None

    f.close()

    return self.d

def main():
  # verify script number of arguments
  nargv = len(sys.argv)
  if nargv < 1:
    print 'usage: bash_parser.py INPUT'
    sys.exit(1)
    
  filename = sys.argv[1]

  p = Bash_parser()
  d = p.parse(filename)

  # output stats
  out = "# %s " % ( os.path.basename(filename) )
  no_print = []
  out += '('
  for stat in d:
    if stat in no_print:
      continue
    # trunk 2 chars
    out += "%s : %d, " % (stat[0:2], d[stat])
  out = re.sub(r', $', ')', out)

  print out

  # print all matched chunks of code
  p.print_chunks()


if __name__ == '__main__':
  main()
