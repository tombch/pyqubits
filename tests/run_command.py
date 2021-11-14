from scripts import main
from scripts import gates


def run_command(statements):
    env = {}
    env['states_dict'] = {}
    env['measurements_dict'] = {}
    env['gates_dict'] = gates.gates_dict
    env['disp_time'] = False
    env['quit_program'] = False
    commands = main.get_commands(statements)
    env = main.execute_commands(commands, env)
    return env