class QuitCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) != 0:
        raise QuitCommandError(f"Expected no arguments.")
    else:
        env['quit_program'] = True
    return env