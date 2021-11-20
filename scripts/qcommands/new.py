import re
from .. import quantum_state
from . import verifiers as v


class NewCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) < 1:
        raise NewCommandError("Expected at least one argument.")
    else:
        num_qubits = 1
        preset_state = None
        new_states = []
        for x in command_args:
            if v.is_tag(x):
                tag, value = x.split('=')
                if tag in env['tags_dict']['new']['num_qubits']:
                    if v.is_valid_num_qubits(value):
                        num_qubits = int(value)
                    else:
                        raise NewCommandError(f"'{value}' cannot be assigned to the {tag} tag. Accepted values are: integers > 0")
                elif tag in env['tags_dict']['new']['state_vector']:
                    if v.is_valid_preset_state(value):
                        preset_state = value
                    else:
                        raise NewCommandError(f"'{value}' cannot be assigned to the {tag} tag. Accepted values are: zero, one")
                else: 
                    raise NewCommandError(f"'{tag}' is not a recognised tag for this command.")
            else:
                if v.is_valid_new_name(x):
                    new_states.append(x)
                else:
                    raise NewCommandError(f"Invalid state name: {x}. Names cannot be just digits and must only use the characters _, 0-9, a-z, and A-Z.")
        for s in new_states:
            env['states_dict'][s] = quantum_state.QuantumState(num_qubits=num_qubits, state_name=s, preset_state=preset_state)
    return env