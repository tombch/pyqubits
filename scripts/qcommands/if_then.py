from .. import logic_evaluator
from .. import main
from .. import utils


class IfThenCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) != 2:
        raise IfThenCommandError(f"Expected exactly two arguments.")
    else:
        if_condition = command_args[0]
        then_statements = command_args[1]
        if not utils.is_code_block(then_statements):
            raise IfThenCommandError("Then statement is missing braces.")
        else:
            then_statements = then_statements[1:-1]
            try:
                if if_condition == "True":
                    env = main.run_commands(then_statements, env)
                elif if_condition == "False":
                    pass
                else:
                    raise IfThenCommandError(f"If condition '{if_condition}' could not be evaluated as either True or False.")
            except main.CommandParserError as e:
                raise IfThenCommandError(f"While executing if-then statement, encountered {e.error_class}.\n {e.error_class}:{utils.indent_error(str(e.message))}")
    return env