import operator

class LogicEvaluatorError(Exception):
    pass

env = {
    'and' : {'symbol' : '/\\', 'value': operator.__and__, 'nargs' : 2},
    'or' : {'symbol' : '\\/', 'value' : operator.__or__, 'nargs' : 2},
    'eq' : {'symbol' : '==', 'value' : operator.__eq__, 'nargs' : 2},
    'ne' : {'symbol' : '!=', 'value' : operator.__ne__, 'nargs' : 2},
    'lt' : {'symbol' : '<', 'value' : operator.__lt__, 'nargs' : 2},
    'gt' : {'symbol' : '>', 'value' : operator.__gt__, 'nargs' : 2},
    'leq' : {'symbol' : '<=', 'value' : operator.__le__, 'nargs' : 2},
    'geq' : {'symbol' : '>=', 'value' : operator.__ge__, 'nargs' : 2},
    'add' : {'symbol' : '+', 'value' : operator.__add__, 'nargs' : 2},
    'subtract' : {'symbol' : '-', 'value' : operator.__sub__, 'nargs' : 2},
    'multiply' : {'symbol' : '*', 'value' : operator.__mul__, 'nargs' : 2},
    'divide' : {'symbol' : '//', 'value' : operator.__truediv__, 'nargs' : 2},
    'power' : {'symbol' : '^', 'value' : operator.__pow__, 'nargs' : 2},
    'not' : {'symbol' : '~', 'value' : operator.__not__, 'nargs' : 1},
    'neg' : {'symbol' : '-', 'value' : operator.__neg__, 'nargs' : 1},
    'T' : {'symbol' : 'T', 'value' : True, 'nargs' : 0},
    'F' : {'symbol' : 'F', 'value' : False, 'nargs' : 0},
}

def get_tokens(user_input):
    if user_input.count('(') != user_input.count(')'):
        raise LogicEvaluatorError('incorrect syntax')
    user_input = user_input.replace(' ', '')
    for k in env.keys():
        user_input = user_input.replace(env[k]['symbol'], f" {env[k]['symbol']} ")        
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
                in_env = False
                for k in env.keys():
                    if tokens[i] == env[k]['symbol']:
                        expression.append(tokens[i])
                        in_env = True
                        break
                if not in_env:
                    try:
                        env[tokens[i]] = {'symbol' : tokens[i], 'value' : int(tokens[i]), 'nargs' : 0}
                        expression.append(tokens[i])
                    except ValueError:
                        try: 
                            env[tokens[i]] = {'symbol' : tokens[i], 'value' : float(tokens[i]), 'nargs' : 0}
                            expression.append(tokens[i])
                        except ValueError:
                            env[tokens[i]] = {'symbol' : tokens[i], 'value' : str(tokens[i]), 'nargs' : 0}
                            expression.append(tokens[i])
                i += 1                
            else:
                i += 1
                break
    return expression, i

def evaluate(expr, accept_type_errors=False):
    try:
        if not isinstance(expr, list):
            for k in env.keys():
                if expr == env[k]['symbol']:
                    return env[k]['value']
        else:
            if len(expr) == 1:
                return evaluate(expr[0])
            elif len(expr) == 2:
                for k in env.keys():
                    if expr[0] == env[k]['symbol'] and env[k]['nargs'] == 1:
                        return env[k]['value'](evaluate(expr[1]))
            elif len(expr) == 3:
                for k in env.keys():
                    if expr[1] == env[k]['symbol'] and env[k]['nargs'] == 2:
                        return env[k]['value'](evaluate(expr[0]), evaluate(expr[2]))    
    except TypeError as e:
        if not accept_type_errors:
            raise LogicEvaluatorError('Attempted impossible comparison')
        else:
            return None
    raise LogicEvaluatorError('Incorrect syntax')

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
            print(f"LogicEvaluatorError: {msg}")

if __name__ == '__main__':
    main()