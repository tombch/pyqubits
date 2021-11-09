import re
import functools
from quantum_state import QuantumState


class JoinCommandError(Exception):
    pass


def command(env, command_args):
    name_tag = '.name='
    states_being_joined = []
    states_to_pop = []
    joint_state_name = None
    for s in command_args:
        if '=' in s:
            if s.startswith(name_tag):
                tag_value = s[len(name_tag):]
                # If the joint name contains an illegal character, declare an error
                illegal_chars = re.search("[^0-9a-zA-Z]", tag_value)
                if illegal_chars:
                    raise JoinCommandError(f"Invalid character(s) in joint state name: {tag_value[illegal_chars.span()[0]]}")
                else:
                    joint_state_name = tag_value
            else:
                # We assume a faulty tag assignment and raise appropriate error
                raise JoinCommandError(f"'{s.split('=')[0]}' is not a recognised tag for this command.")
        elif s in env['states_dict'] and s not in states_to_pop:
            states_being_joined.append(env['states_dict'][s])
            states_to_pop.append(s)
        elif s in states_to_pop:
            raise JoinCommandError(f"Attempted joining of state {s} with itself.")  
        else:
            raise JoinCommandError(f"State '{s}' doesn't exist.")
    # Remove states that are being joined together from the environment
    for s in states_to_pop:
        env['states_dict'].pop(s)                    
    # Create joint state by 'multiplying' states together
    joint_state = functools.reduce(QuantumState.__mul__, states_being_joined)
    # If a valid name was provided, assign it
    if joint_state_name:
        joint_state.state_name = joint_state_name
    # Add the joint state to the environment and return the environment
    env['states_dict'][joint_state.state_name] = joint_state
    return env