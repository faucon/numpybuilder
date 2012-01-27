import sage.functions.all as sagefuncs
import operator
import numpy

class BuilderError(Exception):
    pass

function_map = {}
string_map = {
    "I": "1j",
    "-I": "-1j",
}

def function_builder(function_name):
    '''expression builder for function calls'''
    def b(operands, variables, function_map = function_map, string_map = string_map):
        return str(function_name) + "(" + ", ".join([build_numpy_expression(t, variables, function_map, string_map) for t in operands]) + ")"
    return b
    
def operator_builder(operator_string):
    '''expression builder for (python) operators'''
    def b(operands, variables, function_map, string_map):
        return "( " + operator_string.join([build_numpy_expression(t, variables, function_map, string_map) for t in operands]) + ")"
    return b

function_map = {
    sagefuncs.sin: function_builder("numpy.sin"),
    sagefuncs.cos: function_builder("numpy.cos"),
    sagefuncs.exp: function_builder("numpy.exp"),
    operator.pow: function_builder("numpy.lib.scimath.power"), #special sqrt working with complex numbers
    operator.add: operator_builder(" + "),
    operator.sub: operator_builder(" - "),
    operator.mul: operator_builder(" * "),
    operator.div: operator_builder(" / "),
}

def build_numpy_expression(expression, variables, function_map=function_map, string_map=string_map):
    ''' builds a string which can be evalueted to numpy-calculate a sage expression'''
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

def build_numpyfunc(f, variables, debug=False):
    '''returns a function, which evaluates a sage symbolic expression numerically using
    numpy
    
    f is the symbolic expression
    variables is a list of strings: these are the variables which the created function
    will depend on
    
    example:
    >>> y = var('y')
    >>> f = sin(x) + cos(y)
    >>> num_f = build_numpyfunc(f, ['x', 'y'])
    >>> num_f(0,0)
    1
    '''
    expression_string = "def npfunc(" + ",".join(variables) + "):\n"
    expression_string += "    return " + build_numpy_expression(f, variables)
    exec(expression_string)
    if debug:
        print expression_string
    return npfunc
