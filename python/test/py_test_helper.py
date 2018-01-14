import re

def file_match(pattern, filename):
    """
    file_match() : search regexp pattern in file content, stop at first match
    """
    content = open(filename,'r').readlines()
    return string_match(pattern, content)

def string_match(pattern, content):
    """
    string_match() : search regexp pattern in content, stop at first match
    """
    if not isinstance(content, list):
        content = content.split('\n')

    reg = re.compile(pattern)

    for i, line in enumerate(content):
        if reg.search(line):
            return True

    return False
