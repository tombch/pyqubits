from messages import error_message

class ProbabilitiesCommandError(Exception):
    pass

def command(env, command_args):
    for x in command_args:
        if not x in env['states_dict']:
            raise ProbabilitiesCommandError(f"{error_message['state not found']}: {x}")
        else:
            env['states_dict'][x].print_probabilities()
    return env