from .. import logic_evaluator
from .. import main
from . import verifiers as v


class IfThenCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) != 2:
        raise IfThenCommandError(f"Expected exactly two arguments.")
    else:
        if_condition = command_args[0]
        then_statements = command_args[1]
        if not v.is_code_block(if_condition):
            raise IfThenCommandError("If condition is missing braces.")
        elif not v.is_code_block(then_statements):
            raise IfThenCommandError("Then statement is missing braces.")
        else:
            if_condition = if_condition[1:-1]
            then_statements = then_statements[1:-1]
            try:          
                execute_then_statements = logic_evaluator.interpret(if_condition, user_env=env['measurements_dict'])
            except logic_evaluator.LogicEvaluatorError as msg:
                raise IfThenCommandError(f"While executing if-then statement, encountered LogicEvaluatorError.\n LogicEvaluatorError:{v.indent_error(str(msg))}")
            try:
                if execute_then_statements == True:
                    commands = main.get_commands(then_statements)
                    env = main.execute_commands(commands, env)
                elif execute_then_statements == False:
                    pass
                else:
                    raise IfThenCommandError("If condition did not evaluate to either True or False.")
            except main.ArgumentParserError as e:
                raise IfThenCommandError(f"While executing if-then statement, encountered {e.error_class}.\n {e.error_class}:{v.indent_error(str(e.message))}")
    return env