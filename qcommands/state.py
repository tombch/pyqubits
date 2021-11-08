from messages import error_message

class StateCommandError(Exception):
    pass

def command(env, command_args):
    for x in command_args:
        if not x in env['states_dict']:
            raise StateCommandError(f"{error_message['state not found']}: {x}")
        else:
            env['states_dict'][x].print_state()
    return env