import re
from quantum_state import QuantumState

class NewCommandError(Exception):
    pass

def command(env, command_args):
    num_qubits_tag = ['nq=', 'qubits=']
    preset_state_tag = ['s=', 'state=']
    new_states = []
    num_qubits = 1
    preset_state = None
    for s in command_args:
        if s in env['states_dict']:
            del env['states_dict'][s]
            vars_to_delete = []
            for v in env['vars_dict']:
                if v.startswith(f'{s}.'):
                    vars_to_delete.append(v)
            for v in vars_to_delete:
                del env['vars_dict'][v]
        illegal_chars = re.search("[^0-9a-zA-Z]", s)
        if s.startswith(num_qubits_tag[0]) or s.startswith(num_qubits_tag[1]):
            if s.startswith(num_qubits_tag[0]): 
                num_qubits = int(s[len(num_qubits_tag[0]):])
            else:
                num_qubits = int(s[len(num_qubits_tag[1]):])
        elif s.startswith(preset_state_tag[0]) or s.startswith(preset_state_tag[1]):
            if s.startswith(preset_state_tag[0]):
                preset_state = str(s[len(preset_state_tag[0]):])
            else:
                preset_state = str(s[len(preset_state_tag[1]):])
        elif illegal_chars:
            raise NewCommandError(f"invalid character(s) in state name: {s[illegal_chars.span()[0]]}")
        else:
            new_states.append(s)
    for s in new_states:
        env['states_dict'][s] = QuantumState(num_qubits=num_qubits, state_name=s, preset_state=preset_state)
    return env