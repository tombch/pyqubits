from .. import utils


class MeasureCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) < 2:
        raise MeasureCommandError("Expected at least two arguments.")
    s = command_args[0]
    qubit = command_args[1]
    name = command_args[2:]
    if not utils.is_existing_state(s, env):
        raise MeasureCommandError(f"State '{s}' doesn't exist.")
    s_object = env['states_dict'][s]
    if not utils.is_valid_qubit_of_state(qubit, s_object):
        raise MeasureCommandError(f"Invalid reference of qubit in state {s}: {qubit}")
    bit = s_object.measurement(int(qubit))
    if name:
        if len(name) != 1:
            raise MeasureCommandError(f"Expected at most one name but received {len(name)} names.")
        # Take name out of the list
        name = name[0]
        if not (utils.is_valid_new_name(name) and utils.is_not_builtin(name, env)):
            raise MeasureCommandError(f"Invalid measurement name: {name}")
    else:
        # Default naming system
        measurement_number = 1
        for measurement in env['measurements_dict']:
            if measurement.startswith(f'{s}.{qubit}.m'):
                measurement_number += 1 
        name = f"{s}.{qubit}.m{measurement_number}"
    env['measurements_dict'][name] = bit
    return env