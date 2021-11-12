import re
import functools
from quantum_state import QuantumState
from . import verifiers as v


class JoinCommandError(Exception):
    pass


def command(env, command_args):
    joint_state_name = None
    states_to_join = []
    states_to_pop = []
    for x in command_args:
        if v.is_tag(x):
            tag, value = x.split('=')
            if tag == '.name':
                if v.is_valid_new_name(value):
                    joint_state_name = value
            else: 
                raise JoinCommandError(f"'{tag}' is not a recognised tag for this command.")
        else:
            if v.is_existing_state(x, env):
                if x not in states_to_pop:
                    states_to_join.append(env['states_dict'][x])
                    states_to_pop.append(x)
                else:
                    raise JoinCommandError(f"Attempted joining of state {x} with itself.") 
            else:
                raise JoinCommandError(f"State '{x}' doesn't exist.")
    # Create joint state by 'multiplying' states together
    joint_state = functools.reduce(QuantumState.__mul__, states_to_join)
    # Remove states that have been joined together from the environment
    for s in states_to_pop:
        env['states_dict'].pop(s)    
    # If a valid name was provided, assign it
    if joint_state_name:
        joint_state.state_name = joint_state_name        
    # Add the joint state to the environment and return the environment
    env['states_dict'][joint_state.state_name] = joint_state
    return env