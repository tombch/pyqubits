class TimerCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) != 1:
        raise TimerCommandError(f"Expected exactly one argument.")
    else:
        decision = command_args[0].upper()
        if decision == "SHOW":
            env['disp_time'] = True 
        elif decision == "HIDE":
            env['disp_time'] = False
        else:
            raise TimerCommandError(f"'{decision}' is an incorrect option for the timer. Accepted values are: show, hide")
    return env