from . import verifiers as v


class MeasureCommandError(Exception):
    pass


def command(env, command_args):
    s = command_args[0]
    qubits = command_args[1:]
    if not v.is_existing_state(s, env):
        raise MeasureCommandError(f"State '{s}' doesn't exist.")
    else:
        s_object = env['states_dict'][s]
        if not qubits:
            raise MeasureCommandError(f"No qubit reference(s) given for state {s}.")
        else:
            for q in qubits:
                if v.is_valid_qubit_of_state(q, s_object):
                    bit = s_object.measurement(int(q))
                    measurement_number = 1
                    for measurement in env['vars_dict']:
                        if measurement.startswith(f'{s}.{q}.m'):
                            measurement_number += 1 
                    env['vars_dict'][f"{s}.{q}.m{measurement_number}"] = bit
                else:
                    raise MeasureCommandError(f"Invalid reference of qubit in state {s}: {q}")
    return env