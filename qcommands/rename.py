import re

class RenameCommandError(Exception):
    pass

def command(env, command_args):
    s = command_args[0]
    new_s = command_args[1]
    # If s is not a defined state, throw an error
    if s not in env['states_dict']:
        raise RenameCommandError(f"State '{s}' doesn't exist.")                                   
    # If the proposed new name contains illegal chars, throw an error
    illegal_chars = re.search("[^0-9a-zA-Z]", new_s)
    if illegal_chars:
        raise RenameCommandError(f"Invalid character(s) in new state name for {s}: {new_s[illegal_chars.span()[0]]}")
    # Get reference to the actual object referenced by its current name
    s_object = env['states_dict'][s]
    # Change the name of the object to the new state_name
    s_object.state_name = new_s
    # Remove the old reference to the object from the states_dict
    env['states_dict'].pop(s)
    # Update environment with the new reference to the object, and return the environment
    env['states_dict'].update({new_s : s_object})
    return env