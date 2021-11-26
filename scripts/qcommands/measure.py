from .. import utils


class MeasureCommandError(Exception):
    pass


def command(env, command_args):
    # TODO: .m1, .m2, .m3 etc tags for naming measurements
    # .m1=name creates q.m1.name
    if len(command_args) < 2:
        raise MeasureCommandError("Expected at least two arguments.")
    else:
        s = command_args[0]
        qubits = command_args[1:]
        if not utils.is_existing_state(s, env):
            raise MeasureCommandError(f"State '{s}' doesn't exist.")
        else:
            s_object = env['states_dict'][s]
            if not qubits:
                raise MeasureCommandError(f"No qubit reference(s) given for state {s}.")
            else:
                for q in qubits:
                    if utils.is_valid_qubit_of_state(q, s_object):
                        bit = s_object.measurement(int(q))
                        measurement_number = 1
                        for measurement in env['measurements_dict']:
                            if measurement.startswith(f'{s}.{q}.m'):
                                measurement_number += 1 
                        env['measurements_dict'][f"{s}.{q}.m{measurement_number}"] = bit
                    else:
                        raise MeasureCommandError(f"Invalid reference of qubit in state {s}: {q}")
    return env