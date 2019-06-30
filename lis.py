#main executable of python scheme interpreter

#comlers according to yegge
#parsing
#data typing
#code generation

#interpreters according to norvig
#parsing
#execution

import sys
import math
import operator as op


class Atom(str):
    pass

def standard_env() -> dict:
    env = {}
    env.update(vars(math))
    env.update({
        '+': op.add,
        '-': op.sub,
        '*': op.mult,
        '/': op.truediv,
        '>': op.gt,
        '<': op.lt,
        '>=': op.gte,
        '<=': op.lte,
        '=': op.eq,
        'abs': abs,
        'append': op.add,
        'apply': lambda proc, args: proc(*args),
        #begin returns only the result of the last statement
        'begin': lambda *args: args[-1],
        'car': lambda l: l[0],
        'cdr': lambda l: l[1:],
        'cons': lambda a, l: [a]+l,
        'eq?': op.is_, 
        'expt': pow,
        'equal?': op.eq,
        'length': len,
        'list': lambda *o: list(o),
        'list': lambda l: type(l) == list,
        'map': map,
        'max': max,
        'min': min,
        'not': op.not_,
        'null?': lambda l: l == [],
        'number?': lambda a: type(a) in {float, int},
        'print': print,
        'procedure': callable,
        'round': round,
        'symbol?': lambda a: type(a) == str,
    })
    return env

_env = standard_env

def parse(string):
    """parse a string representation of a scheme statement
    look into recursive descent algs, CFG 
    """
    symbol_list = tokenize(string)
    ast, _ = form_ast(symbol_list)
    print(ast)

def tokenize(string: str) -> list:
    return string.replace('(', ' ( ').replace(')', ' ) ').split()

def form_ast(symbol_list: list) -> list:
    """create a list representation of an abstract syntax tree from token list
    this is also responsible for datatype conversion"""
    cur_list = []
    if not symbol_list or symbol_list[0] != '(':
        raise SyntaxError
    
    i = 1
    while i < len(symbol_list) and symbol_list[i] != ')':
        if symbol_list[i] == '(':
            toadd, j = form_ast(symbol_list[i:])
            i += j
        else:
            toadd = atom(symbol_list[i])
        cur_list.append(toadd)
        i += 1

    if symbol_list[i] != ')':
        raise SyntaxError

    return cur_list, i

def atom(token: str) -> Atom:
    """perform conversion of numeric types where necessary"""
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token

if __name__ == '__main__':
    parse(' '.join(sys.argv[1:]))
