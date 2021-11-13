import main
from main import ArgumentParserError
from . import verifiers as v


class ExecuteCommandError(Exception):
    pass


def command(parser, env, command_args):
    file_name = command_args[0]
    extension = ".clqc"
    if file_name.endswith(extension):
        file_name = file_name[:len(extension)+1]
    try:
        with open(f"{file_name}{extension}", 'r') as file:
            script = file.read()
            try:
                commands = main.get_commands(parser, script)
                env = main.execute_commands(parser, commands, env)
            except ArgumentParserError as e:
                raise ExecuteCommandError(f"While executing '{file_name}', encountered {e.error_class}.\n {e.error_class}:{v.indent_error(str(e.message))}")
    except FileNotFoundError:
        raise ExecuteCommandError(f"File not found: {file_name}")
    return env