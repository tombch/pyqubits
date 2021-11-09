import functools
from quantum_state import QuantumState

class JoinCommandError(Exception):
    pass

def command(env, command_args):
    name_tag = 'name='
    states_being_joined = []
    states_to_pop = []
    joint_state_name = ""
    for s in command_args:
        if s.startswith(name_tag):
            joint_state_name = s[len(name_tag):]
        elif s in env['states_dict'] and s not in states_to_pop:
            states_being_joined.append(env['states_dict'][s])
            states_to_pop.append(s)
        elif s in states_to_pop:
            raise JoinCommandError(f"attempted joining of state {s} with itself")  
        else:
            raise JoinCommandError(f"invalid parameter assignment or state that doesn't exist: {s}")
    for s in states_to_pop:
        env['states_dict'].pop(s)                                 
    joint_state = functools.reduce(QuantumState.__mul__, states_being_joined)
    if joint_state_name:
        joint_state.state_name = joint_state_name
    env['states_dict'][joint_state.state_name] = joint_state
    return env