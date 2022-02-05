import sys
import re
import copy
import readline
from . import logic_evaluator
from . import gates
from . import qcommands
from . import utils


class CommandParserError(Exception):
    __slots__ = 'message', 'error_class'
    def __init__(self, message, error_class=None):
        self.message = message
        self.error_class = error_class


def regroup(statement_pieces, left_char, right_char, split_char):
    # Re-group expressions/lists after separation caused by splitting the string on a character.
    # split_char is the character used to split the statement, and is needed for reconstructing expressions/lists.
    regrouped_expressions = []
    num_splits = len(statement_pieces)
    i = 0
    open_expr = 0
    current_statement = ""
    while i < num_splits: 
        c = 0
        len_current_split = len(statement_pieces[i])
        while c < len_current_split:
            if left_char != right_char:
                # Opening expression
                if left_char == statement_pieces[i][c]:
                    open_expr += 1
                # Closing expression
                elif right_char == statement_pieces[i][c]:
                    open_expr -= 1
            else:
                # Opening expression
                if left_char == statement_pieces[i][c] and open_expr == 0:
                    open_expr = 1
                # Closing expression
                elif right_char == statement_pieces[i][c] and open_expr == 1:
                    open_expr = 0
            c += 1
        if open_expr == 0:
            regrouped_expressions.append(current_statement + statement_pieces[i])    
            current_statement = ""
        else:
            current_statement += statement_pieces[i] + split_char
        i += 1
    if open_expr > 0:
        raise CommandParserError(f"Incorrect syntax: encountered more '{left_char}' than '{right_char}'.",  error_class='CommandParserError')
    elif open_expr < 0:
        raise CommandParserError(f"Incorrect syntax: encountered more '{right_char}' than '{left_char}'.",  error_class='CommandParserError')
    return regrouped_expressions


def get_commands(statements, env):
    statements = statements.replace('\n', ' ').split(';')
    # After splitting on ; we need to regroup any split subcommands that were contained within { }
    statements = regroup(statements, "{", "}", split_char=";")
    commands = []
    for statement in statements:
        # Split the current statement on empty space
        statement_pieces = statement.split()
        if statement_pieces:
            command_args = regroup(statement_pieces, "{", "}", split_char=" ")
            command_args = regroup(command_args, "[", "]", split_char=" ")
            command_args = regroup(command_args, "(", ")", split_char=" ")
            command_args = regroup(command_args, "`", "`", split_char=" ")
            for i, arg in enumerate(command_args):
                if not utils.is_code_block(arg):
                    logic_strings = re.findall('`.*?`', arg)
                    for x in logic_strings:
                        try:
                            evaluated_x = logic_evaluator.interpret(x[1:-1], user_env=env['measurements_dict'])
                        except logic_evaluator.LogicEvaluatorError as msg:
                            raise CommandParserError(msg, error_class='LogicEvaluatorError')      
                        command_args[i] = arg.replace(x, str(evaluated_x))
            command = {'cmd' : command_args[0], 'args' : command_args[1:]}
            commands.append(command)
    return commands


def execute_commands(commands, env):
    env = copy.deepcopy(env)
    for command in commands:
        keyword_name = command['cmd']
        try:
            keyword = env['keywords_dict'][keyword_name]
            try:
                if keyword['builtin']:
                    # Execute built in command
                    env = keyword['func'](env, command['args'])
                else:
                    # Execute user-defined command
                    env = keyword['func'](env, command['args'], keyword_name, keyword['args'], keyword['body'])
            except keyword['error'] as msg:
                raise CommandParserError(msg, error_class=keyword['error_name'])
        except KeyError:
            raise CommandParserError(f"Unrecognised command: {keyword_name}", error_class='CommandParserError')
    return env


def run_commands(statements, env):
    # Turn statements into commands that can be executed
    commands = get_commands(statements, env)
    # Execute the commands and return the modified environment
    env = execute_commands(commands, env)
    return env


def new_env():
    env = {
        'quit_program' : False,
        'states_dict' : {}, 
        'measurements_dict' : {}, 
        'gates_dict' : gates.gates_dict,
        'keywords_dict' : {
            'new' : {'func' : qcommands.new.command, 'error' : qcommands.new.NewCommandError, 'error_name' : 'NewCommandError', 'builtin' : True}, # type: ignore
            'join' : {'func' : qcommands.join.command, 'error' : qcommands.join.JoinCommandError, 'error_name' : 'JoinCommandError', 'builtin' : True}, # type: ignore
            'rename' : {'func' : qcommands.rename.command, 'error' : qcommands.rename.RenameCommandError, 'error_name' : 'RenameCommandError', 'builtin' : True}, # type: ignore
            'delete' : {'func' : qcommands.delete.command, 'error' : qcommands.delete.DeleteCommandError, 'error_name' : 'DeleteCommandError', 'builtin' : True}, # type: ignore
            'apply' : {'func' : qcommands.apply.command, 'error' : qcommands.apply.ApplyCommandError, 'error_name' : 'ApplyCommandError', 'builtin' : True}, # type: ignore
            'measure' : {'func' : qcommands.measure.command, 'error' : qcommands.measure.MeasureCommandError, 'error_name' : 'MeasureCommandError', 'builtin' : True}, # type: ignore
            'state' : {'func' : qcommands.state.command, 'error' : qcommands.state.StateCommandError, 'error_name' : 'StateCommandError', 'builtin' : True}, # type: ignore
            'circuit' : {'func' : qcommands.circuit.command, 'error' : qcommands.circuit.CircuitCommandError, 'error_name' : 'CircuitCommandError', 'builtin' : True}, # type: ignore
            'prob-dist' : {'func' : qcommands.prob_dist.command, 'error' : qcommands.prob_dist.ProbDistCommandError, 'error_name' : 'ProbDistCommandError', 'builtin' : True}, # type: ignore
            'if-then' : {'func' : qcommands.if_then.command, 'error' : qcommands.if_then.IfThenCommandError, 'error_name' : 'IfThenCommandError', 'builtin' : True}, # type: ignore
            'if-then-else' : {'func' : qcommands.if_then_else.command, 'error' : qcommands.if_then_else.IfThenElseCommandError, 'error_name' : 'IfThenElseCommandError', 'builtin' : True}, # type: ignore
            'for' : {'func' : qcommands.for_.command, 'error' : qcommands.for_.ForCommandError, 'error_name' : 'ForCommandError', 'builtin' : True}, # type: ignore
            'execute' : {'func' : qcommands.execute.command, 'error' : qcommands.execute.ExecuteCommandError, 'error_name' : 'ExecuteCommandError', 'builtin' : True}, # type: ignore
            'list' : {'func' : qcommands.list.command, 'error' : qcommands.list.ListCommandError, 'error_name' : 'ListCommandError', 'builtin' : True}, # type: ignore
            'quit' : {'func' : qcommands.quit.command, 'error' : qcommands.quit.QuitCommandError, 'error_name' : 'QuitCommandError', 'builtin' : True}, # type: ignore
            'help' : {'func' : qcommands.help.command, 'error' : qcommands.help.HelpCommandError, 'error_name' : 'HelpCommandError', 'builtin' : True}, # type: ignore
            'pattern' : {'func' : qcommands.pattern.command, 'error' : qcommands.pattern.PatternCommandError, 'error_name' : 'PatternCommandError', 'builtin' : True}, # type: ignore
            'return' : {'func' : qcommands.return_.command, 'error' : qcommands.return_.ReturnCommandError, 'error_name' : 'ReturnCommandError', 'builtin' : True}, # type: ignore
        },
        'tags_dict' : {
            'new' : {'num_qubits' : ['.nq', '.num-qubits'], 'state_vector' : ['.v', '.vector']},
            'join' : {'name' : ['.n', '.name']},
            'delete' : {'states' : ['.s', '.states'], 'measurements' : ['.m', '.measurements']},
        }
    }
    env['tags'] = [tag for cmd in env['tags_dict'].keys() for tag_name in env['tags_dict'][cmd].keys() for tag in env['tags_dict'][cmd][tag_name]]
    return env


def program():
    env = new_env()
    if sys.argv[1:]:
        for x in sys.argv[1:]:
            try:
                env = run_commands(f"execute {x}", env)
                # Clear environment
                env = new_env()
            except CommandParserError as e:
                print(f"{e.error_class}: {e.message}")                                  
    else:
        print("Welcome to CmdQuantum, a terminal-based quantum computing simulator. \nTo see a list of available commands, enter '##' and then press tab twice.\nEnter 'help' for more information regarding commands.\nTo close the program, enter 'quit'.\n")
        readline.parse_and_bind("tab: complete")
        readline.set_completer_delims("")
        while not env['quit_program']:
            try:
                completer_args = list(env['keywords_dict'].keys()) + env['tags'] 
                completer_args += ['##' + x for x in env['keywords_dict']]
                completer_args += env['states_dict'].keys() 
                completer_args += env['measurements_dict'].keys() 
                completer_args += env['gates_dict'].keys()
                
                def completer(text, state):
                    original_text = " ".join(text.split())
                    for x in "{}[]()":
                        text = text.replace(f"{x}", f" {x} ")
                    text = text.split()
                    completed = text[:-1]
                    to_complete = text[-1]
                    arguments = completer_args
                    options = [i for i in arguments if len(to_complete) > 0 and i.startswith(to_complete)]
                    if state < len(options):
                        if len(completed) > 0:
                            return f"{original_text[:-len(to_complete)]}{options[state]}"
                        else: 
                            return options[state]
                    else:
                        return None

                readline.set_completer(completer)
                statements = input('#~: ')                
                env = run_commands(statements, env)
            except CommandParserError as e:
                print(f"{e.error_class}: {e.message}")
    quit()