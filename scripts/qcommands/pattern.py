import re
from .. import main
from .. import utils


class PatternCommandError(Exception):
    pass


# TODO: Make better
def func(env, input_args, func_name, func_args, func_body, return_args):
    if input_args == None:
        raise PatternCommandError(f"Invalid input arguments: {input_args}")
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
                raise PatternCommandError(f"While executing pattern '{func_name}', encountered {e.error_class}.\n {e.error_class}:{utils.indent_error(str(e.message))}")    
            inputs_to_return = []
            for i in range(len(func_args)):
                for j in range(len(return_args)):
                    if func_args[i].strip() == return_args[j].strip():
                        inputs_to_return.append(input_args[i])          
            for x in inputs_to_return:
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
        if utils.is_valid_new_name(func_name) and utils.is_not_builtin(func_name, env):
            args_list = utils.construct_arg_list(func_args)
            if args_list:
                for arg in args_list:
                    if arg in env['keywords_dict'].keys():
                        raise PatternCommandError(f"Argument '{arg}' is invalid; it matches a keyword.")
                if utils.is_code_block(func_body):
                    if not (return_command and return_command[0] != 'return'):
                        return_args = return_command[1:]
                    else:
                        raise PatternCommandError(f"Expected 'return' but received: {return_command[0]}")
                else:
                    raise PatternCommandError("Pattern body is missing braces.")
            else:
                raise PatternCommandError(f"Invalid arguments: {func_args}")
        else:
            raise PatternCommandError(f"Invalid pattern name: {func_name}")
    env['keywords_dict'][func_name] = {'shortcut' : None, 'func' : func, 'args' : args_list, 'body' : func_body[1:-1], 'return' : return_args, 'error' : PatternCommandError, 'error_name' : f'{func_name[0].upper()}{func_name[1:]}CommandError', 'builtin' : False}
    return env