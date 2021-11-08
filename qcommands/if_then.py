import main
import logic_evaluator

class IfThenCommandError(Exception):
    pass

def command(parser, env, command_args):
    if_condition = command_args[0][1:len(command_args[0])-1]
    then_statements = command_args[1][1:len(command_args[1])-1]
    try:          
        execute_then_statements = logic_evaluator.interpret(if_condition, user_env=env['vars_dict'])
        if execute_then_statements == True:
            commands = main.get_commands(parser, then_statements)
            env = main.execute_commands(parser, commands, env)
    except logic_evaluator.LogicEvaluatorError as msg:
        raise IfThenCommandError(msg)
    return env