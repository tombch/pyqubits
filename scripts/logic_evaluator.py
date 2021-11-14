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
    'mod' : {'symbol' : '%', 'value' : operator.__mod__, 'nargs' : 2},
    'not' : {'symbol' : '~', 'value' : operator.__not__, 'nargs' : 1},
    'negate' : {'symbol' : '-', 'value' : operator.__neg__, 'nargs' : 1},
    'T' : {'symbol' : 'T', 'value' : True, 'nargs' : 0},
    'F' : {'symbol' : 'F', 'value' : False, 'nargs' : 0},
}


def get_tokens(user_input):
    for k in env.keys():
        if env[k]['nargs'] > 0:
            user_input = user_input.replace(env[k]['symbol'], f" {env[k]['symbol']} ")        
    user_input = user_input.replace('(', ' ( ')
    user_input = user_input.replace(')', ' ) ')
    tokens = user_input.split()
    return tokens


def get_expression(tokens, sub_expr_count=0):
    i = 0
    expression = []
    if len(tokens) == 0:
        raise LogicEvaluatorError("Syntax error: Expression ended before closing '('")            
    if tokens[0] == ')' and sub_expr_count == 0:
        raise LogicEvaluatorError("Syntax error: Encountered closing ')' without opening '('")
    elif tokens[0] == ')' and sub_expr_count > 0:
        raise LogicEvaluatorError("Syntax error: Encountered closing ')' instantly after opening '('")
    while i < len(tokens):
        if tokens[i] == ')' and sub_expr_count > 0:
            sub_expr_count -= 1
            return expression, i, sub_expr_count
        elif tokens[i] == '(':
            sub_expr_count += 1
            sub_expression, sub_i, sub_expr_count = get_expression(tokens[i+1:], sub_expr_count=sub_expr_count)
            i += sub_i + 1
            expression.append(sub_expression)
        elif tokens[i] != '(' and tokens[i] != ')':
            in_env = False
            for k in env.keys():
                if tokens[i] == env[k]['symbol']:
                    expression.append(k)
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
                        raise LogicEvaluatorError(f"Unrecognised value: {tokens[i]}")
                        # env[tokens[i]] = {'symbol' : tokens[i], 'value' : str(tokens[i]), 'nargs' : 0}
                        # expression.append(tokens[i])
        i += 1    
    if tokens.count('(') < tokens.count(')'):
        raise LogicEvaluatorError("Syntax error: Missing opening '('")
    elif tokens.count('(') > tokens.count(')'):
        raise LogicEvaluatorError("Syntax error: Missing closing ')'")
    return expression, i, sub_expr_count


def evaluate(expr, accept_type_errors=False):
    try:
        if not isinstance(expr, list):
            if env[expr]['nargs'] == 0:
                return env[expr]['value']
            else:
                raise LogicEvaluatorError(f'Impossible use of operator: {env[expr]["symbol"]}')
        else:
            if len(expr) == 1:
                return evaluate(expr[0])
            elif len(expr) == 2:
                if expr[0] == 'subtract':
                    # edge case where two different operations share the same symbol
                    expr[0] = 'negate'             
                if env[expr[0]]['nargs'] == 0:
                    raise LogicEvaluatorError(f'Impossible use of value: {env[expr[0]]["symbol"]}') 
                elif env[expr[0]]['nargs'] == 1:
                    return env[expr[0]]['value'](evaluate(expr[1]))
                elif env[expr[0]]['nargs'] == 2:
                    raise LogicEvaluatorError(f'Impossible use of operator: {env[expr[0]]["symbol"]}')
            elif len(expr) == 3:
                if env[expr[1]]['nargs'] == 0:
                    raise LogicEvaluatorError(f'Impossible use of value: {env[expr[1]]["symbol"]}') 
                elif env[expr[1]]['nargs'] == 1:
                    raise LogicEvaluatorError(f'Impossible use of operator: {env[expr[1]]["symbol"]}') 
                elif env[expr[1]]['nargs'] == 2:
                    return env[expr[1]]['value'](evaluate(expr[0]), evaluate(expr[2]))
            else:
                raise LogicEvaluatorError(f'Ambiguous or invalid expression: {" ".join([env[k]["symbol"] for k in expr])}')
    except TypeError:
        if not accept_type_errors:
            raise LogicEvaluatorError('Attempted impossible comparison')
        else:
            return None
    except ZeroDivisionError:
        raise LogicEvaluatorError('Attempted division by zero')


def interpret(user_input, user_env=None, accept_type_errors=False):
    if user_env is not None:
        for k in user_env.keys():
            env.update({k : {'symbol' : k, 'value' : user_env[k], 'nargs' : 0}})   
    condition = evaluate(get_expression(get_tokens(user_input))[0], accept_type_errors)
    return condition


# def main():
#     while True:
#         try: 
#             user_input = input('> ')
#             print(interpret(user_input))
#         except LogicEvaluatorError as msg:
#             print(f"LogicEvaluatorError: {msg}")


# if __name__ == '__main__':
#     main()