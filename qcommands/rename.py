import re
from . import verifiers as v


class RenameCommandError(Exception):
    pass


def command(env, command_args):
    s = command_args[0]
    new_s = command_args[1]
    if not v.is_existing_state(s, env):
        raise RenameCommandError(f"State '{s}' doesn't exist.")
    else:
        if not v.is_valid_new_name(new_s):
            raise RenameCommandError(f"Invalid state name: {new_s}")
        else:
            # Get reference to the actual object referenced by its current name
            s_object = env['states_dict'][s]
            # Change the name of the object to the new state_name
            s_object.state_name = new_s
            # Remove the old reference to the object from the states_dict
            env['states_dict'].pop(s)
            # Update environment with the new reference to the object, and return the environment
            env['states_dict'][new_s] = s_object
    return env