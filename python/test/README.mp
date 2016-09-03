# libido python code unittest

uses py.test

## run tests

~~~
cd test/
py.test
~~~

## embed_ipython.py

an external example for embeding ipython in code, not allowing step depug.

## add manual debugger

~~~
pip install --user ipdb

# add anywhere in the code to stop, works with ipython too
import ipdb; ipdb.set_trace()
~~~


## manual run from ipython

~~~
ipython

import test_libido_parser
p = test_libido_parser._create_parser()
p.parse('../../examples/readme_ex0.sh')
print p.dump_result()
~~~
