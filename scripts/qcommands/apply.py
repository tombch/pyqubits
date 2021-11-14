from .. import gates
from . import verifiers as v


class ApplyCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) < 3:
        raise ApplyCommandError(f"Expected at least three arguments.")
    else:
        g = command_args[0]
        s = command_args[1]
        qubits = command_args[2:]        
        if not v.is_existing_gate(g, env):
            raise ApplyCommandError(f"Gate '{g}' doesn't exist.")
        else:
            if not v.is_existing_state(s, env):
                raise ApplyCommandError(f"State '{s}' doesn't exist.")
            else:
                s_object = env['states_dict'][s]
                g_num_args = env['gates_dict'][g]['nargs']
                g_func = env['gates_dict'][g]['func']
                if g_num_args > s_object.num_qubits:
                     raise ApplyCommandError(f"Gate {g} requires {g_num_args} qubits. State {s} only contains {s_object.num_qubits} qubit(s).")
                elif g_num_args > 1:
                    for q_list in qubits:
                        q_list_object = v.construct_int_list(q_list)
                        if q_list_object == None or not v.is_valid_qubit_list_of_state(q_list_object, s_object):
                            raise ApplyCommandError(f"Invalid reference of qubits in state {s}: {q_list}. Must be a list of qubit references with no duplicates.")
                        elif len(q_list_object) != g_num_args:
                            raise ApplyCommandError(f"When applying {g} to state {s}: expected {g_num_args} qubits for {g} but received {len(q_list_object)}.")
                        else:
                            g_func(s_object, *q_list_object)
                else:
                    for q in qubits:
                        if not v.is_valid_qubit_of_state(q, s_object):
                            raise ApplyCommandError(f"Invalid reference of qubit in state {s}: {q}. Must be an integer > 0 and within the number of qubits in {s}.")
                        else:
                            g_func(s_object, int(q))
    return env