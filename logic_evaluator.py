import operator

class LogicEvaluatorError(Exception):
    pass

symbol = {
    'and' : '/\\',
    'or' : '\\/',
    'not' : '^',
    'eq' : '==',
    'ne' : '!=',
    'lt' : '<',
    'gt' : '>',
    'leq' : '<=',
    'geq' : '>=',
    'add' : '+',
    'subtract' : '-',
    'multiply' : '*',
    'divide' : '//',
    'True' : 'T',
    'False' : 'F' 
}

env = {
    symbol['and'] : operator.__and__,
    symbol['or'] : operator.__or__,
    symbol['not'] : operator.__not__,
    symbol['eq'] : operator.__eq__,
    symbol['ne'] : operator.__ne__,
    symbol['lt'] : operator.__lt__,
    symbol['gt'] : operator.__gt__,
    symbol['leq'] : operator.__le__,
    symbol['geq'] : operator.__ge__,
    symbol['add'] : operator.__add__,
    symbol['subtract'] : operator.__sub__,
    symbol['multiply'] : operator.__mul__,
    symbol['divide'] : operator.__truediv__,
    symbol['True'] : True,
    symbol['False'] : False
}

two_arg_operators = {
    symbol['and'] : operator.__and__,
    symbol['or'] : operator.__or__,
    symbol['eq'] : operator.__eq__,
    symbol['ne'] : operator.__ne__,
    symbol['lt'] : operator.__lt__,
    symbol['gt'] : operator.__gt__,
    symbol['leq'] : operator.__le__,
    symbol['geq'] : operator.__ge__,
    symbol['add'] : operator.__add__,
    symbol['subtract'] : operator.__sub__,
    symbol['multiply'] : operator.__mul__,
    symbol['divide'] : operator.__truediv__,    
}

def get_tokens(user_input):
    if user_input.count('(') != user_input.count(')'):
        raise LogicEvaluatorError('incorrect syntax')
    for k in symbol.keys():
        user_input = user_input.replace(symbol[k], f" {symbol[k]} ")        
    user_input = user_input.replace('(', ' ( ')
    user_input = user_input.replace(')', ' ) ')
    tokens = user_input.split()
    return tokens

def get_expression(tokens):
    num_tokens = len(tokens)
    i = 0
    expression = []
    if num_tokens == 0:
        raise LogicEvaluatorError('unexpected end of expression')
    if tokens[0] == ')':
        raise LogicEvaluatorError('incorrect syntax')
    else:
        while i < num_tokens:
            if tokens[i] == '(':
                sub_expression, sub_i = get_expression(tokens[i+1:])
                i += sub_i + 1
                expression.append(sub_expression)
            elif tokens[i] != ')':
                if tokens[i] in env:
                    expression.append(env[tokens[i]])
                else:
                    try:
                        expression.append(int(tokens[i]))
                    except ValueError:
                        try: 
                            expression.append(float(tokens[i]))
                        except ValueError:
                            expression.append(str(tokens[i]))
                i += 1                
            else:
                i += 1
                break
    return expression, i

def evaluate(expr, accept_type_errors=False):
    try:
        if isinstance(expr, bool) or isinstance(expr, int) or isinstance(expr, float) or isinstance(expr, str):
            return expr
        elif isinstance(expr, list):
            if len(expr) == 1:
                return evaluate(expr[0])
            elif len(expr) == 2:
                if expr[0] == operator.__not__:
                    return operator.__not__(evaluate(expr[1]))
                elif expr[0] == operator.__sub__:
                    # edge case where __sub__ has to be replaced with __neg__
                    return operator.__neg__(evaluate(expr[1]))
            elif len(expr) == 3:
                for k in two_arg_operators.keys():
                    if expr[1] == two_arg_operators[k]:
                        return two_arg_operators[k](evaluate(expr[0]), evaluate(expr[2]))    
    except TypeError:
        if not accept_type_errors:
            raise LogicEvaluatorError('types cannot be compared')
        else:
            return None
    raise LogicEvaluatorError('incorrect syntax')

def interpret(user_input, user_env=None, accept_type_errors=False):
    if user_env is not None:
        env.update(user_env)
    condition = evaluate(get_expression(get_tokens(user_input))[0], accept_type_errors)
    return condition

def main():
    while True:
        try: 
            user_input = input('> ')
            print(interpret(user_input))
        except LogicEvaluatorError as msg:
            print(f"error: {msg}")

if __name__ == '__main__':
    main()