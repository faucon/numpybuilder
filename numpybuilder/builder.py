import sage.functions.all as sagefuncs
import operator
import numpy

class BuilderError(Exception):
    r"""
    This Exception is thrown, when an unknown symbolic expression is encountered while
    building a numpy expression
    """
    pass

function_map = {}
string_map = {
    "I": "1j",
    "-I": "-1j",
}

def function_builder(function_name):
    r"""
    expression builder for function calls
    """
    def b(operands, variables, function_map = function_map, string_map = string_map):
        return str(function_name) + "(" + ", ".join([build_numpy_expression(t, variables, function_map, string_map) for t in operands]) + ")"
    return b
    
def operator_builder(operator_string):
    r"""
    expression builder for (python) operators
    """
    def b(operands, variables, function_map, string_map):
        return "( " + operator_string.join([build_numpy_expression(t, variables, function_map, string_map) for t in operands]) + ")"
    return b

function_map = {
    sagefuncs.abs_symbolic: function_builder("numpy.abs"),
    sagefuncs.arccos: function_builder("numpy.lib.scimath.arccos"),
    sagefuncs.arccosh: function_builder("numpy.arccosh"),
    sagefuncs.arcsin: function_builder("numpy.lib.scimath.arcsin"),
    sagefuncs.arcsinh: function_builder("numpy.arcsinh"),
    sagefuncs.arctan: function_builder("numpy.arctan"),
    sagefuncs.arctanh: function_builder("numpy.lib.scimath.arctanh"),
    sagefuncs.cos: function_builder("numpy.cos"),
    sagefuncs.exp: function_builder("numpy.exp"),
    sagefuncs.ln: function_builder("numpy.lib.scimath.log"),
    sagefuncs.sin: function_builder("numpy.sin"),
    sagefuncs.sqrt: function_builder("numpy.lib.scimath.sqrt"),

    operator.pow: function_builder("numpy.lib.scimath.power"), #special sqrt working with complex numbers
    operator.add: operator_builder(" + "),
    operator.sub: operator_builder(" - "),
    operator.mul: operator_builder(" * "),
    operator.div: operator_builder(" / "),
}

def build_numpy_expression(expression, variables, function_map=function_map, string_map=string_map):
    r"""
    builds a string which can be evalueted to numpy-calculate a sage expression
    """
    if function_map.has_key(expression.operator()):
        return function_map[expression.operator()](expression.operands(), variables, function_map, string_map)
    if string_map.has_key(str(expression)):
        return string_map[str(expression)]
    #if not found, just return string or number
    #if we can evaluate it numerically, just do it, otherwise return string of it
    try:
        return str(expression.n())
    except:
        if str(expression) in variables:
            return str(expression)
        else:
            raise BuilderError("unknown symbolic expression: " + str(expression))

def build_numpyfunc(f, variables):
    r"""
    returns a function, which evaluates a sage symbolic expression numerically using
    numpy
   
    INPUT:

    - ``f`` -- the symbolic expression to build a numpy-function from
    - ``variables`` -- list of strings: these are the variables which the created function
    will depend on, it will depend on this in the given order, the symbolic expression
    should not contain variables not listed here
   
    OUTPUT:
    
    A function, which expects a x variables (x = len(variables) from input), where these
    variables could be numpy-arrays

    EXAMPLES:

    lets create a numpy-function::

        sage: from sage.numpybuilder import build_numpyfunc
        sage: y = var('y')
        sage: f = sin(x) + cos(y)
        sage: num_f = build_numpyfunc(f, ['x', 'y'])
        sage: num_f(0,0)
        1.0

    and you can process numpy arrays::

        sage: import numpy as np
        sage: xs, ys = np.meshgrid(np.linspace(0,2*n(pi)), np.linspace(0,2*n(pi)))
        sage: num_f(xs, ys)
        array([[ 1...
        sage: num_f(xs,ys).shape
        (50, 50)


    TESTS:
    some other supported functions::

        sage: f = log(x, 4)
        sage: num_f = build_numpyfunc(f, ['x'])
        sage: num_f(5) - n(f(x=5))
        0.0
        sage: f = abs(x) + e^x + sqrt(x)
        sage: num_f = build_numpyfunc(f, ['x'])
        sage: num_f(3.4) - n(f(x=3.4))
        0.0
        sage: f = arccos(x) + arccosh(x) + arcsin(x) + arcsinh(x) + arctan(x) + arctanh(x)
        sage: num_f = build_numpyfunc(f, ['x']) #does not raise an exception should be enough for now

    if it doesn't know something (either a variable or a symbolic function) an error is
    thrown::

        sage: f = x + y
        sage: num_f = build_numpyfunc(f, ['x']) #you don't tell it, that y should be a variable 
        Traceback (most recent call last):
        ...
        BuilderError: unknown symbolic expression: y

    or if you use unsupported operators::

        sage: f = (x==y)
        sage: num_f = build_numpyfunc(f, ['x', 'y'])
        Traceback (most recent call last):
        ...
        BuilderError: unknown symbolic expression: x == y
        
    """
    expression_string = "def npfunc(" + ",".join(variables) + "):\n"
    expression_string += "    return " + build_numpy_expression(f, variables)
    exec(expression_string)
    return npfunc
