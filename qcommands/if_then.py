import main
import logic_evaluator
from . import verifiers as v


class IfThenCommandError(Exception):
    pass


def command(parser, env, command_args):
    if_condition = v.remove_braces(command_args[0])
    then_statements = v.remove_braces(command_args[1])
    if if_condition == None:
        raise IfThenCommandError("If condition is missing braces.")
    elif then_statements == None:
        raise IfThenCommandError("Then statement is missing braces.")
    else:
        try:          
            execute_then_statements = logic_evaluator.interpret(if_condition, user_env=env['vars_dict'])
            if execute_then_statements == True:
                commands = main.get_commands(parser, then_statements)
                env = main.execute_commands(parser, commands, env)
            elif execute_then_statements == False:
                pass
            else:
                raise IfThenCommandError("If condition did not evaluate to either True or False.")
        except logic_evaluator.LogicEvaluatorError as msg:
            raise IfThenCommandError(msg)
    return env