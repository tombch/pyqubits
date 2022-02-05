class DeleteCommandError(Exception):
    pass


def command(env, command_args):
    delete_state_options = env['tags_dict']['delete']['states']
    delete_measurement_options = env['tags_dict']['delete']['measurements']
    delete_type = command_args[0]
    objects_to_delete = command_args[1:len(command_args)]
    delete_all_states = False
    delete_all_measurements = False
    # If the first argument is *, we will delete everything
    if delete_type == '*':
        delete_all_states = True
        delete_all_measurements = True
    # If the first arg is states, and any other arg is *, delete all states
    elif delete_type in delete_state_options:
        if len(objects_to_delete) > 0:
            for x in objects_to_delete:
                if x == '*':
                    delete_all_states = True
                    break
        else:
            raise DeleteCommandError(f"No state(s) provided.")
    # If the first arg is measurements, and any other arg is *, delete all measurements
    elif delete_type in delete_measurement_options:
        if len(objects_to_delete) > 0:
            for x in objects_to_delete:
                if x == '*':
                    delete_all_measurements = True
                    break
        else:
            raise DeleteCommandError(f"No measurement(s) provided.")
    # Otherwise, arguments don't fit the defined format and so an error is thrown
    else: 
        raise DeleteCommandError(f"First argument '{delete_type}' does not specify the deletion type. Options are: *, {', '.join(delete_state_options)}, {', '.join(delete_measurement_options)}")
    # Remove all states from the environment if instructed
    if delete_all_states:
        objects_to_delete = list(env['states_dict'].keys())
        for s in objects_to_delete:
            del env['states_dict'][s]
    # Otherwise, remove specified states
    elif delete_type in delete_state_options:
        for s in objects_to_delete:
            if s in env['states_dict']:
                del env['states_dict'][s]
    # Remove all measurements from the environment if instructed
    if delete_all_measurements:
        objects_to_delete = list(env['measurements_dict'].keys())
        for v in objects_to_delete:
            del env['measurements_dict'][v]
    # Otherwise, remove specified measurements
    elif delete_type in delete_measurement_options:
        for s in objects_to_delete:
            measurements_to_delete = []
            for v in env['measurements_dict']:
                if v.startswith(f'{s}.'):
                    measurements_to_delete.append(v)
            for v in measurements_to_delete:
                del env['measurements_dict'][v]
    return env