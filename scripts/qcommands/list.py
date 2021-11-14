class ListCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) != 0:
        raise ListCommandError(f"Expected no arguments.")
    else:
        print(f"states: {list(env['states_dict'].keys())}")
        print(f"measurements: {list(env['measurements_dict'].keys())}")
    return env