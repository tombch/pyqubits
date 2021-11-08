from messages import error_message

class DeleteCommandError(Exception):
    pass

def command(env, command_args):
    delete_type = command_args[len(command_args)-1]
    objects_to_delete = command_args[0:len(command_args)-1]
    if delete_type == "state" or delete_type == "states":
        if len(objects_to_delete) == 0:
            objects_to_delete = list(env['states_dict'].keys())
            for s in objects_to_delete:
                del env['states_dict'][s]
        else:
            for s in objects_to_delete:
                if s not in env['states_dict']:
                    raise DeleteCommandError(f"{error_message['state not found']}: {s}")
                else:
                    del env['states_dict'][s]
    elif delete_type == "var" or delete_type == "vars":
        if len(objects_to_delete) == 0:
            objects_to_delete = list(env['vars_dict'].keys())
            for v in objects_to_delete:
                del env['vars_dict'][v]
        else:
            for s in objects_to_delete:
                vars_to_delete = []
                for v in env['vars_dict']:
                    if v.startswith(f'{s}.'):
                        vars_to_delete.append(v)
                for v in vars_to_delete:
                    del env['vars_dict'][v]
    else: 
        raise DeleteCommandError(f"must specify deletion with either state / states or var / vars")
    return env