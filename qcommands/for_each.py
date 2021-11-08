import main
import re

class ForEachCommandError(Exception):
    pass

def command(parser, env, command_args):
    i_arg = command_args[0]
    iterable_arg = command_args[1]
    statements = command_args[2]
    iterable_arg = iterable_arg[1:len(iterable_arg)-1].split(',')
    iterable_arg = [int(x) for x in iterable_arg]
    if iterable_arg[0] <= iterable_arg[1]:
        iterable_arg[1] += 1
    else:
        iterable_arg[1] -= 1
    iterable = range(*tuple(iterable_arg))
    # iterate a number of times as specified by user
    for i in iterable:       
        statements_i = statements
        need_spaces = re.findall('[^0-9a-zA-Z]i[^0-9a-zA-Z]', statements_i)
        for pattern in need_spaces:
            replacement = pattern.replace(i_arg, str(i))
            statements_i = statements_i.replace(pattern, replacement)
        statements_i = statements_i[1:len(statements_i)-1]
        commands = main.get_commands(parser, statements_i)
        # Execute the current command(s), and return env
        env = main.execute_commands(parser, commands, env)
    return env