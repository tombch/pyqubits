from . import verifiers as v


class CircuitCommandError(Exception):
    pass


def command(env, command_args):
    for x in command_args:
        if v.is_existing_state(x, env):
            env['states_dict'][x].print_circuit()
        else:
            raise CircuitCommandError(f"State '{x}' doesn't exist.")
    return env