import re
from .. import main
from .. import utils


class ForCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) != 3:
        raise ForCommandError(f"Expected exactly three arguments.")
    else:
        i_arg = command_args[0]
        iter_string = command_args[1]
        for_statements = command_args[2]
        if utils.is_letters(i_arg):
            iterable_tuple = utils.construct_range_list(iter_string)
            iterable_list = utils.construct_list(iter_string)
            if iterable_tuple != None:
                if iterable_tuple[0] <= iterable_tuple[1]:
                    iterable_tuple[1] += 1
                else:
                    iterable_tuple[1] -= 1
                iterable = range(*tuple(iterable_tuple))
            elif iterable_list != None:
                iterable = iterable_list
            else:
                raise ForCommandError(f"Invalid iterable: {iter_string}")
            if not utils.is_code_block(for_statements):
                raise ForCommandError("For statement is missing braces.")
            else:
                for_statements = for_statements[1:-1]
                # Iterate a number of times as specified by user
                for i in iterable:       
                    for_statements_i = for_statements
                    reg_pattern = f"[^0-9a-zA-Z]{i_arg}[^0-9a-zA-Z]"
                    dummy_vars_needing_spaces = re.findall(reg_pattern, for_statements_i)
                    for pattern in dummy_vars_needing_spaces:
                        if not ((pattern.strip() in env['keywords_dict'].keys()) or (pattern.strip() in env['tags'])):
                            replacement = pattern.replace(i_arg, str(i))
                            for_statements_i = for_statements_i.replace(pattern, replacement)
                    try:
                        env['measurements_dict'][i] = i
                        env = main.run_commands(for_statements_i, env)
                        env['measurements_dict'].pop(i)
                    except main.CommandParserError as e:
                        raise ForCommandError(f"While executing for-each statement, encountered {e.error_class}.\n {e.error_class}:{utils.indent_error(str(e.message))}")     
        else:
            raise ForCommandError(f"Invalid dummy variable: {i_arg}")
    return env