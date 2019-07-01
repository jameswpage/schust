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

class Env(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def __getitem__(self, key):
        return super().__getitem__(key)

    def find(self, var):
        return self if (var in self) else self.outer.find(var)

class Procedure(object):
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))

def standard_env() -> dict:
    env = Env()
    env.update(vars(math))
    env.update({
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.truediv,
        '>': op.gt,
        '<': op.lt,
        '>=': op.ge,
        '<=': op.le,
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

_env = standard_env()

def pne(string):
    """parse and evaluate"""
    ast = parse(string)
    return eval(ast)

def parse(string):
    """parse a string representation of a scheme statement
    look into recursive descent algs, CFG 
    """
    symbol_list = tokenize(string)
    ast, _ = form_ast(symbol_list)
    return ast


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

Number = (float, int)
Symbol = str
Atom = (Number, Symbol)
Exp = (list, Atom)

def atom(token: str) -> Atom:
    """perform conversion of numeric types where necessary"""
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)

def eval(x: Exp, env=_env) -> Exp:
    """evaluate an abstract syntax tree and return an expression (atom or list)"""
    if isinstance(x, Symbol):
        return env.find(x)[x]
    elif isinstance(x, Number) or x == []:
        return x
    elif x[0] == 'if':
        _, test, out1, out2 = x
        return eval(out1, env) if eval(test, env) else eval(out2, env)
    elif x[0] == 'define':
        _, var, val = x
        env[var] = eval(val, env)
    elif x[0] == 'quote':
        _, exp = x
        return exp
    elif x[0] == 'lambda':
        _, parms, body = x
        return Procedure(parms, body, env)
    elif x[0] == 'set!':
        _, var, val = x
        env.find(var)[var] = eval(val, env)
    else:
        proc = eval(x[0], env)
        args = [eval(exp, env) for exp in x[1:]]
        return proc(*args)

def scheme_formatter(toprint: Exp) -> str:
    """format expression as scheme string"""
    if isinstance(toprint, list):
        return '(' + ' '.join(str(val) for val in toprint) + ')'
    else:
        return toprint

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(pne(' '.join(sys.argv[1:])))
    else:
        while True:
            toeval = input('> ')
            if toeval == 'exit':
                break
            if not toeval:
                continue
            try:
                res = pne(toeval)
                if res is not None:
                    print(scheme_formatter(res))
            except SyntaxError as e:
                print(e)       
