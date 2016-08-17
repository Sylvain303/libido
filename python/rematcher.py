#
# small regexp matcher for simplier syntax
# for parser when you do extensive matching and extracting pattern
#
# Usage:
#
# from rematcher import REMatcher
# l = 'some string'
# m = REMatcher(l)
# if m.match(r'(some)'):
#     part = m.group(1)
#
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

    def all(self):
        return self.rematch.groups()
