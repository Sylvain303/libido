import os
import sys
sys.path.append('..')

import libido


def test_readconfig():
    config_file = './libido.conf'

    conf = libido.readconfig(config_file)
    assert isinstance(conf, dict)
    assert conf.get('lib_source')
