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
    symbol['True'] : True,
    symbol['False'] : False
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
                        raise LogicEvaluatorError(f'unrecognised or incomparable object: {tokens[i]}')
                i += 1                
            else:
                i += 1
                break
    return expression, i

def evaluate(expr):
    if isinstance(expr, bool):
        return expr
    elif isinstance(expr, int):
        return expr
    elif isinstance(expr, list):
        if (env[symbol['and']] in expr) and len(expr) == 3:
            return env[symbol['and']](evaluate(expr[0]), evaluate(expr[2]))
        elif (env[symbol['or']] in expr) and len(expr) == 3:
            return env[symbol['or']](evaluate(expr[0]), evaluate(expr[2]))
        elif (env[symbol['not']] in expr) and len(expr) == 2:
            return env[symbol['not']](evaluate(expr[1]))
        elif (env[symbol['eq']] in expr) and len(expr) == 3:
            return env[symbol['eq']](evaluate(expr[0]), evaluate(expr[2]))
        elif (env[symbol['ne']] in expr) and len(expr) == 3:
            return env[symbol['ne']](evaluate(expr[0]), evaluate(expr[2]))
        elif (env[symbol['lt']] in expr) and len(expr) == 3:
            return env[symbol['lt']](evaluate(expr[0]), evaluate(expr[2]))
        elif (env[symbol['gt']] in expr) and len(expr) == 3:
            return env[symbol['gt']](evaluate(expr[0]), evaluate(expr[2]))
        elif (env[symbol['leq']] in expr) and len(expr) == 3:
            return env[symbol['leq']](evaluate(expr[0]), evaluate(expr[2]))
        elif (env[symbol['geq']] in expr) and len(expr) == 3:
            return env[symbol['geq']](evaluate(expr[0]), evaluate(expr[2]))
        elif len(expr) == 1:
            return evaluate(expr[0]) 
        else:
            raise LogicEvaluatorError('incorrect syntax')

def interpret(user_input, user_env=None):
    if user_env is not None:
        env.update(user_env)
    try:
        condition = evaluate(get_expression(get_tokens(user_input))[0])
        return condition
    except LogicEvaluatorError as msg:
        print(f'logic error: {msg}')
        return None

def main():
    while True:
        try: 
            user_input = input('> ')
            print(interpret(user_input))
        except LogicEvaluatorError as msg:
            print(f"error: {msg}")

if __name__ == '__main__':
    main()