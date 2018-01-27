import re
import os

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

def write_tmp(string_of_code):
    """
    write_tmp(): create a temporary file handling the code in the string
                 auto remove a #!shebang indent level if any, if input is multiline.
    return : the filename generated
    """
    from tempfile import NamedTemporaryFile
    code = []
    s = None
    for i, l in enumerate(string_of_code.split("\n")):
        if len(code) == 0:
            m = re.search(r'^(\s*)#!/bin/bash', l)
            if m:
                # we found the indent
                s = re.compile('^' + m.group(1))

            if l == "":
                # remove first emply lines
                continue

        # no more empty line, we add the code
        if s:
            l = s.sub('', l)
        code.append(l)


    tmp = NamedTemporaryFile(delete=False)
    tmp.write("\n".join(code))
    tmp.close()
    return tmp.name

def remove_file(fname):
    try:
        os.remove(fname)
    except OSError:
        pass
