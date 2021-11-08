from messages import error_message
import json
import gates

class ApplyCommandError(Exception):
    pass

def check_qubits_apply_gate(s, required_num_qubits, qubit_refs, gate_name):
    if required_num_qubits == 1:
        gate_func = gates.one_arg_gates.get(gate_name)
    elif required_num_qubits == 2:
        gate_func = gates.two_arg_gates.get(gate_name)
    final_qubits = []
    for qs in qubit_refs:
        current_qubits = []
        try:
            qs = json.loads(qs)
            if isinstance(qs, list) and required_num_qubits == len(qs):
                int_qs = [int(x) for x in qs]
                current_qubits.append(int_qs) 
            elif isinstance(qs, int) and required_num_qubits == 1:
                int_qs = qs
                current_qubits.append(int_qs)
            else:
                raise ApplyCommandError(f"{error_message['incorrect input for gate']} {gate_name}: {qs}")
        except (json.decoder.JSONDecodeError, TypeError, ValueError):
            # TypeError example: [1,[2]]
            # ValueError example: [1, "hello"]
            raise ApplyCommandError(f"{error_message['invalid qubit ref']}: {qs}")
        for curr_q in current_qubits:
            out_of_bounds = False
            if isinstance(curr_q, int):
                if not (0 <= curr_q <= s.num_qubits):
                    out_of_bounds = True 
            elif isinstance(curr_q, list):
                for x in curr_q:
                    if not (0 <= x <= s.num_qubits):
                        out_of_bounds = True
            if not out_of_bounds:
                final_qubits.append(curr_q)
            else:
                raise ApplyCommandError(f"qubit reference(s) out of bounds: {curr_q}")
    for qs in final_qubits:
        qs_list = []
        if isinstance(qs, int):
            qs_list.append(qs)
        else: 
            for q in qs:
                qs_list.append(q)
        try: 
            gate_func(s, *qs_list)
        except gates.GateError as msg:
            raise ApplyCommandError(msg)

def command(env, command_args):
    gate_name = command_args[0]
    s = command_args[1]
    qubit_refs = command_args[2:]
    if s not in env['states_dict']:
        raise ApplyCommandError(f"{error_message['state not found']}: {s}")
    else: 
        s = env['states_dict'][s]
    if not qubit_refs:
        raise ApplyCommandError(f"{error_message['no qubit ref']}")
    if gate_name in gates.one_arg_gates:
        check_qubits_apply_gate(s, 1, qubit_refs, gate_name)                       
    elif gate_name in gates.two_arg_gates:
        check_qubits_apply_gate(s, 2, qubit_refs, gate_name)
    else: 
        raise ApplyCommandError(f"{error_message['gate not found']}: {gate_name}")
    return env 