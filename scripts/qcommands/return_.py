from .. import main

class ReturnCommandError(Exception):
    pass

def command(env, command_args):
    return_args = command_args[0:]
    objects_to_return = []
    for return_arg in return_args:
        objects_to_return.append(return_arg.strip())
    return_env = main.new_env()
    for obj in objects_to_return:
        if obj in env['states_dict'].keys():
            return_env['states_dict'][obj] = env['states_dict'][obj]
        elif obj in env['measurements_dict'].keys():
            return_env['measurements_dict'][obj] = env['measurements_dict'][obj]
        elif obj in env['keywords_dict'].keys():
            return_env['keywords_dict'][obj] = env['keywords_dict'][obj]
        else:
            raise ReturnCommandError(f"Unrecognised return argument: {obj}")
    return return_env