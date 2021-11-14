from . import verifiers as v


class ProbabilitiesCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) < 1:
        raise ProbabilitiesCommandError("Expected at least one argument.")
    else:
        for x in command_args:
            if v.is_existing_state(x, env):
                env['states_dict'][x].print_probabilities()
            else:
                raise ProbabilitiesCommandError(f"State '{x}' doesn't exist.")
    return env