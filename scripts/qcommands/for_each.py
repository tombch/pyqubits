import re
from .. import main
from . import verifiers as v


class ForEachCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) != 3:
        raise ForEachCommandError(f"Expected exactly three arguments.")
    else:
        i_arg = command_args[0]
        iter_string = command_args[1]
        for_statements = command_args[2]
        if v.is_letters(i_arg):
            iterable_tuple = v.construct_range_list(iter_string)
            iterable_list = v.construct_float_list(iter_string)
            if iterable_tuple != None:
                if iterable_tuple[0] <= iterable_tuple[1]:
                    iterable_tuple[1] += 1
                else:
                    iterable_tuple[1] -= 1
                iterable = range(*tuple(iterable_tuple))
            elif iterable_list != None:
                iterable = iterable_list
            else:
                raise ForEachCommandError(f"Invalid iterable: {iter_string}")
            if not v.is_code_block(for_statements):
                raise ForEachCommandError("For statement is missing braces.")
            else:
                for_statements = for_statements[1:-1]
                # Iterate a number of times as specified by user
                for i in iterable:       
                    for_statements_i = for_statements
                    reg_pattern = f"[^0-9a-zA-Z]{i_arg}[^0-9a-zA-Z]"
                    dummy_vars_needing_spaces = re.findall(reg_pattern, for_statements_i)
                    for pattern in dummy_vars_needing_spaces:
                        replacement = pattern.replace(i_arg, str(i))
                        for_statements_i = for_statements_i.replace(pattern, replacement)
                    try:
                        env['measurements_dict'][i_arg] = i
                        commands = main.get_commands(for_statements_i)
                        env = main.execute_commands(commands, env)
                        env['measurements_dict'].pop(i_arg)
                    except main.ArgumentParserError as e:
                        raise ForEachCommandError(f"While executing for-each statement, encountered {e.error_class}.\n {e.error_class}:{v.indent_error(str(e.message))}")     
        else:
            raise ForEachCommandError(f"Invalid dummy variable: {i_arg}")
    return env