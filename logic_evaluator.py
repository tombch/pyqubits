import operator

class LogicEvaluatorError(Exception):
    pass

symbol = {
    'and' : '/\\',
    'or' : '\\/',
    'not' : '¬',
    'True' : 'T',
    'False' : 'F'
}

env = {
    symbol['and'] : operator.__and__,
    symbol['or'] : operator.__or__,
    symbol['not'] : operator.__not__,
    symbol['True'] : True,
    symbol['False'] : False
}

def get_tokens(user_input):
    user_input = user_input.replace(symbol['and'], f" {symbol['and']} ")
    user_input = user_input.replace(symbol['or'], f" {symbol['or']} ")
    user_input = user_input.replace(symbol['not'], f" {symbol['not']} ")
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
                expression.append(env[tokens[i]])
                i += 1                
            else:
                i += 1
                break
    return expression, i

def evaluate(expr):
    if isinstance(expr, bool):
        return expr
    elif isinstance(expr, list):
        if (env[symbol['and']] in expr) and len(expr) == 3:
            return env[symbol['and']](evaluate(expr[0]), evaluate(expr[2]))
        elif (env[symbol['or']] in expr) and len(expr) == 3:
            return env[symbol['or']](evaluate(expr[0]), evaluate(expr[2]))
        elif (env[symbol['not']] in expr) and len(expr) == 2:
            return env[symbol['not']](evaluate(expr[1]))
        elif len(expr) == 1:
            return evaluate(expr[0]) 
        else:
            raise LogicEvaluatorError('ambiguous expression (needs parentheses)')
    
def main():
    while True:
        try: 
            user_input = input('> ')
            print(evaluate(get_expression(get_tokens(user_input))[0]))
        except LogicEvaluatorError as msg:
            print(f"error: {msg}")

if __name__ == '__main__':
    main()