import main

class ExecuteCommandError(Exception):
    pass

def command(parser, env, command_args):
    file_name = command_args[0]
    try:
        with open(f"{file_name}.clqc", 'r') as file:
            script = file.read()
            commands = main.get_commands(parser, script)
            env = main.execute_commands(parser, commands, env)
    except FileNotFoundError:
        raise ExecuteCommandError(f"file not found: {file_name}")
    return env