from . import verifiers as v


class StateCommandError(Exception):
    pass


def command(env, command_args):
    for x in command_args:
        if v.is_existing_state(x, env):
            env['states_dict'][x].print_state()
        else:
            raise StateCommandError(f"State '{x}' doesn't exist.")
    return env