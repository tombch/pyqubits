import re
from .. import main
from . import verifiers as v


class PatternCommandError(Exception):
    pass


# TODO: Make better
def func(env, input_args, func_name, func_args, func_body, return_args):
    if input_args == None:
        raise PatternCommandError(f"Invalid input arguments: {input_args_str}")
    else:
        if len(input_args) != len(func_args):
            raise PatternCommandError(f"{func_name} expected {len(func_args)} argument(s) but received {len(input_args)}.")
        else:
            for i in range(len(input_args)):       
                reg_pattern = f"[^0-9a-zA-Z]{func_args[i]}[^0-9a-zA-Z]"
                args_needing_spaces = re.findall(reg_pattern, func_body)
                for pattern in args_needing_spaces:
                    if not ((pattern.strip() in env['keywords_dict'].keys()) or (pattern.strip() in env['shortcuts']) or (pattern.strip() in env['tags'])):
                        replacement = pattern.replace(func_args[i], input_args[i])
                        func_body = func_body.replace(pattern, replacement)
            func_env = main.new_env()
            for i in range(len(input_args)):
                if input_args[i] in env['states_dict'].keys():
                    func_env['states_dict'][input_args[i]] = env['states_dict'][input_args[i]]
                elif input_args[i] in env['measurements_dict'].keys():
                    func_env['measurements_dict'][input_args[i]] = env['measurements_dict'][input_args[i]]
            try:
                func_env = main.run_commands(func_body, func_env)
            except main.ArgumentParserError as e:
                raise PatternCommandError(f"While executing pattern '{func_name}', encountered {e.error_class}.\n {e.error_class}:{v.indent_error(str(e.message))}")    
            for i in range(len(func_args)):
                for j in range(len(return_args)):
                    if func_args[i].strip() == return_args[j].strip():
                        return_args[j] = input_args[i]          
            for x in return_args:
                if x in func_env['states_dict'].keys():
                    env['states_dict'][x] = func_env['states_dict'][x]
                elif x in func_env['measurements_dict'].keys():
                    env['measurements_dict'][x] = func_env['measurements_dict'][x]
                else:
                    raise PatternCommandError(f"Unrecognised output argument: {x}")                   
    return env


def command(env, command_args):
    if len(command_args) < 3:
        raise PatternCommandError(f"Expected at least three arguments: pattern name, pattern arguments and pattern body.")
    else:
        func_name = command_args[0]
        func_args = command_args[1]
        func_body = command_args[2]
        return_command = command_args[3:]
        if v.is_letters(func_name):
            args_list = v.construct_arg_list(func_args)
            if args_list == None:
                raise PatternCommandError(f"Invalid arguments: {func_args}")
            for arg in args_list:
                if arg in env['keywords_dict'].keys():
                    raise PatternCommandError(f"Argument '{arg}' is invalid; it matches a keyword.")
            if not v.is_code_block(func_body):
                raise PatternCommandError("Pattern body is missing braces.")
            else:
                if return_command and return_command[0] != 'return':
                    raise PatternCommandError(f"Expected 'return' but received: {return_command[0]}")
                else:
                    return_args = return_command[1:]
                env['keywords_dict'][func_name] = {'shortcut' : None, 'func' : func, 'args' : args_list, 'body' : func_body[1:-1], 'return' : return_args, 'error' : PatternCommandError, 'error_name' : f'{func_name[0].upper()}{func_name[1:]}CommandError', 'builtin' : False}
        else:
            raise PatternCommandError(f"Invalid pattern name: {func_name}")
    return env