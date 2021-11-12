class TimerCommandError(Exception):
    pass


def command(env, command_args):
    decision = command_args[0].upper()
    if decision == "ON":
        env['disp_time'] = True 
    elif decision == "OFF":
        env['disp_time'] = False
    else:
        raise TimerCommandError(f"'{decision}' is an incorrect option for the timer. Accepted values are: on, off")
    return env