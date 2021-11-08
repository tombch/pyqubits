import json
from messages import error_message

class MeasureCommandError(Exception):
    pass

def command(env, command_args):
    s = command_args[0]
    qubit_refs = command_args[1:]
    if s not in env['states_dict']:
        raise MeasureCommandError(f"{error_message['state not found']}: {s}")
    else:
        s = env['states_dict'][s]
    if not qubit_refs:
        raise MeasureCommandError(f"{error_message['no qubit ref']}")
    final_qubits = []
    for q in qubit_refs:
        try:
            q = json.loads(q)
            q = int(q)
        except (json.decoder.JSONDecodeError, TypeError, ValueError):
            raise MeasureCommandError(f"{error_message['invalid qubit ref']}: {q}")
        if not (0 <= q <= s.num_qubits):
            raise MeasureCommandError(f"qubit reference(s) out of bounds: {q}")        
        else:
            final_qubits.append(q)
    for q in final_qubits:
        bit = s.measurement(int(q))
        measurement_number = 1
        for v in env['vars_dict']:
            if v.startswith(f'{s}.{q}.m'):
                measurement_number += 1 
        env['vars_dict'][f"{s.state_name}.{q}.m{measurement_number}"] = bit
    return env