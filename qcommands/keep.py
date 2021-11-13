class KeepCommandError(Exception):
    pass


def command(env, command_args):
    keep_state_options = ['.s', '.state', '.states']
    keep_measurement_options = ['.m', '.measurement', '.measurements']
    keep_type = command_args[0]
    objects_to_keep = command_args[1:len(command_args)]
    keep_all_states = False
    keep_all_measurements = False
    # If the first argument is *, keep everything
    if keep_type == '*':
        keep_all_states = True
        keep_all_measurements = True
    # If the first arg is state or states, and any other arg is *, keep all states
    elif keep_type in keep_state_options:
        if len(objects_to_keep) > 0:
            for x in objects_to_keep:
                if x == '*':
                    keep_all_states = True
                    break
        else:
            raise KeepCommandError(f"No state(s) provided.")
    # If the first arg is measurement or measurements, and any other arg is *, keep all measurements
    elif keep_type in keep_measurement_options:
        if len(objects_to_keep) > 0:
            for x in objects_to_keep:
                if x == '*':
                    keep_all_measurements = True
                    break
        else:
            raise KeepCommandError(f"No measurement(s) provided.")
    # Otherwise, arguments don't fit the defined format and so an error is thrown
    else: 
        raise KeepCommandError(f"First argument '{keep_type}' does not specify the keep type. Options are: *, {', '.join(keep_state_options)}, {', '.join(keep_measurement_options)}")
    # Keep all states from the environment if instructed
    states_to_delete = []
    if keep_all_states:
        pass
    # Otherwise, keep specified states
    elif keep_type in keep_state_options:
        for s in env['states_dict']:
            if s not in objects_to_keep:
                states_to_delete.append(s)
    for s in states_to_delete:
        del env['states_dict'][s]
    # Keep all measurements from the environment if instructed
    measurements_to_delete = []
    if keep_all_measurements:
        pass
    # Otherwise, keep specified measurements
    elif keep_type in keep_measurement_options:
        for m in env['measurements_dict']:
            keep_m = False
            for s in objects_to_keep:
                if m.startswith(f'{s}.'):
                    keep_m = True
            if not keep_m:
                measurements_to_delete.append(m)
    for m in measurements_to_delete:
        del env['measurements_dict'][m]
    return env