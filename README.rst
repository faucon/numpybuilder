Numpybuilder
============

Installation
-------------

Just move the directory "numpybuilder" to 

/your/path/to/sage/devel/sage/build/sage/

Usage
------
in sage do:
  >>> from sage.numpybuilder import build_numpyfunc
  >>> f = x^2 + cos(x) #or some other function
  >>> numerical_f = build_numpyfunc(f, ['x'])

see docstring for further information
