import re

class RenameCommandError(Exception):
    pass

def command(env, command_args):
    s = command_args[0]
    new_s = command_args[1]
    if s not in env['states_dict']:
        raise RenameCommandError(f"{error_message['state not found']}: {s}")                                   
    illegal_chars = re.search("[^0-9a-zA-Z]", new_s)
    if illegal_chars:
        raise RenameCommandError(f"invalid character(s) in state name: {new_s[illegal_chars.span()[0]]}")
    s_object = env['states_dict'][s]
    s_object.state_name = new_s
    env['states_dict'].pop(s)
    env['states_dict'].update({new_s : s_object})
    return env