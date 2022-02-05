from .. import main
from .. import utils


class ExecuteCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) < 1:
        raise ExecuteCommandError(f"Expected at least one argument.")
    else:
        extension = ".cq"
        for file_name in command_args:
            if file_name.endswith(extension):
                file_name = file_name[:-len(extension)]
            try:
                with open(f"{file_name}{extension}", 'r') as file:
                    script = file.read()
                    try:
                        env = main.run_commands(script, env)
                    except main.CommandParserError as e:
                        raise ExecuteCommandError(f"While executing '{file_name}', encountered {e.error_class}.\n {e.error_class}:{utils.indent_error(str(e.message))}")
            except FileNotFoundError:
                raise ExecuteCommandError(f"File not found: {file_name}{extension}")
            print(f"Executed: {file_name}{extension}")
    return env