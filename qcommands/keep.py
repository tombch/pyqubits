class KeepCommandError(Exception):
    pass

def command(env, command_args):
    keep_type = command_args[len(command_args)-1]
    objects_to_keep = command_args[0:len(command_args)-1]           
    if keep_type == "state" or keep_type == "states":
        states_to_delete = []
        for s in env['states_dict']:
            if s not in objects_to_keep:
                states_to_delete.append(s)
        for s in states_to_delete:
            del env['states_dict'][s]
    elif keep_type == "var" or keep_type == "vars":
        vars_to_delete = []
        for s in objects_to_keep:
            for v in env['vars_dict']:
                if v.startswith(f'{s}.'):
                    pass
                else:
                    vars_to_delete.append(v)
        for v in vars_to_delete:
            del env['vars_dict'][v]
    else: 
        raise KeepCommandError(f"must specify deletion with either state / states or var / vars")
    return env