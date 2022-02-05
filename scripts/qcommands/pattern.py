from .. import main
from .. import utils


class PatternCommandError(Exception):
    pass


def func(env, input_args, func_name, func_args, func_body):
    if input_args == None:
        raise PatternCommandError(f"Invalid input arguments: {input_args}")
    if len(input_args) != len(func_args):
        raise PatternCommandError(f"{func_name} expected {len(func_args)} argument(s) but received {len(input_args)}.")
    func_body = " " + func_body + " "
    func_env = main.new_env()
    for input_arg, func_arg in zip(input_args, func_args):
        if input_arg in env['states_dict'].keys():
            func_env['states_dict'][func_arg] = env['states_dict'][input_arg]
        elif input_arg in env['measurements_dict'].keys():
            func_env['measurements_dict'][func_arg] = env['measurements_dict'][input_arg]
    try:
        commands = main.get_commands(func_body, func_env)
        func_env = main.execute_commands(commands, func_env)
        if commands and commands[-1]['cmd'] == 'return':
            env['states_dict'].update(func_env['states_dict'])
            env['measurements_dict'].update(func_env['measurements_dict'])
            env['keywords_dict'].update(func_env['keywords_dict'])
    except main.CommandParserError as e:
        raise PatternCommandError(f"While executing pattern '{func_name}', encountered {e.error_class}.\n {e.error_class}:{utils.indent_error(str(e.message))}")    
    return env


def command(env, command_args):
    if len(command_args) != 3:
        raise PatternCommandError(f"Expected three arguments: pattern name, pattern arguments and pattern body.")
    func_name = command_args[0]
    func_args = command_args[1]
    func_body = command_args[2]
    # Check validity of function name
    if not (utils.is_valid_new_name(func_name) and utils.is_not_builtin(func_name, env)):
        raise PatternCommandError(f"Invalid pattern name: {func_name}")
    # Check validity of function arguments
    args_list = utils.construct_arg_list(func_args)
    if args_list == None:
        raise PatternCommandError(f"Invalid arguments: {func_args}")
    for arg in args_list:
        if arg in env['keywords_dict'].keys():
            raise PatternCommandError(f"Argument '{arg}' is invalid; it matches a keyword.")
    # Check if the function body has braces
    if not utils.is_code_block(func_body):
        raise PatternCommandError("Pattern body is missing braces.")
    # Add user-defined function to env, then return env
    env['keywords_dict'][func_name] = {'func' : func, 'args' : args_list, 'body' : func_body[1:-1], 'error' : PatternCommandError, 'error_name' : f'{func_name[0].upper()}{func_name[1:]}CommandError', 'builtin' : False}
    return env