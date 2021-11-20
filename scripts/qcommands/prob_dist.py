from . import verifiers as v


class ProbDistCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) < 1:
        raise ProbDistCommandError("Expected at least one argument.")
    else:
        for x in command_args:
            if v.is_existing_state(x, env):
                env['states_dict'][x].print_prob_dist()
            else:
                raise ProbDistCommandError(f"State '{x}' doesn't exist.")
    return env