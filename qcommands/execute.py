import main
from main import ArgumentParserError


class ExecuteCommandError(Exception):
    pass


def command(parser, env, command_args):
    file_name = command_args[0]
    try:
        with open(f"{file_name}.clqc", 'r') as file:
            script = file.read()
            try:
                commands = main.get_commands(parser, script)
                env = main.execute_commands(parser, commands, env)
            except ArgumentParserError as e:
                raise ExecuteCommandError(f"While executing '{file_name}', encountered {e.error_class}: {e.message}")
    except FileNotFoundError:
        raise ExecuteCommandError(f"File not found: {file_name}")
    return env