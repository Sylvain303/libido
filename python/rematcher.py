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
