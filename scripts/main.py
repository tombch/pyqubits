import readline
import sys
import time
import re
import copy
from . import logic_evaluator
from . import gates
from . import qcommands
from scripts.qcommands import verifiers as v


class ArgumentParserError(Exception):
    __slots__ = 'message', 'error_class'
    def __init__(self, message, error_class=None):
        self.message = message
        self.error_class = error_class


def regroup(split_statement, left_char, right_char, split_char):
    # Re-group expressions/lists after separation caused by splitting the string on a character.
    # split_char is the character used to split the statement, and is needed for reconstructing expressions/lists.
    regrouped_expressions = []
    num_splits = len(split_statement)
    i = 0
    open_expr = 0
    current_statement = ""
    while i < num_splits: 
        c = 0
        len_current_split = len(split_statement[i])
        while c < len_current_split:            
            # opening expression
            if left_char == split_statement[i][c]:
                open_expr += 1
            # closing expression
            elif right_char == split_statement[i][c]:
                open_expr -= 1
            c += 1
        if open_expr == 0:
            regrouped_expressions.append(current_statement + split_statement[i])    
            current_statement = ""
        else:
            current_statement += split_statement[i] + split_char
        i += 1
    if open_expr > 0:
        raise ArgumentParserError(f"Incorrect syntax: encountered more '{left_char}' than '{right_char}'.",  error_class='ArgumentParserError')
    elif open_expr < 0:
        raise ArgumentParserError(f"Incorrect syntax: encountered more '{right_char}' than '{left_char}'.",  error_class='ArgumentParserError')
    return regrouped_expressions


def get_commands(statements, env):
    statements = statements.replace('\n', ' ')
    for x in "{}[]()":
        statements = statements.replace(f"{x}", f" {x} ")
    statements = statements.split(';')
    # After splitting on ; we need to regroup any split subcommands
    # These subcommands are contained within { }
    statements = regroup(statements, "{", "}", split_char=";")
    commands = []
    for statement in statements:
        # Split the current statement on empty space
        split_statement = statement.split()
        # Avoiding empty lists
        if split_statement:
            command_args = regroup(split_statement, "{", "}", split_char=" ")
            command_args = regroup(command_args, "[", "]", split_char=" ")
            command_args = regroup(command_args, "(", ")", split_char=" ")
            command_args = regroup(command_args, "<", ">", split_char=" ")
            for i in range(len(command_args)):
                if not v.is_code_block(command_args[i]):
                    logic_strings = re.findall('<.*?>', command_args[i])
                    for x in logic_strings:
                        try:
                            evaluated_x = logic_evaluator.interpret(x[1:len(x)-1], user_env=env['measurements_dict'])
                        except logic_evaluator.LogicEvaluatorError as msg:
                            raise ArgumentParserError(msg, error_class='LogicEvaluatorError')      
                        command_args[i] = command_args[i].replace(x, str(evaluated_x))
            command = {}
            for k in env['keywords_dict'].keys():
                if command_args[0] == k or (env['keywords_dict'][k]['builtin'] and command_args[0] == env['keywords_dict'][k]['shortcut']):
                    command = {'cmd' : k, 'args' : command_args[1:]}
                    break
            if not command:
                raise ArgumentParserError(f"Unrecognised command: {command_args[0]}", error_class='ArgumentParserError')
            # Now we check for other keywords in the command
            if command['cmd'] == 'pattern':
                for k in env['keywords_dict'].keys(): 
                    # Given this is the first argument of the pattern command, we ignore user patterns here as they could be a redefinition.
                    if env['keywords_dict'][k]['builtin']:
                        if command_args[1] == k or command_args[1] == env['keywords_dict'][k]['shortcut']:
                            raise ArgumentParserError(f"Command {command_args[1]} cannot be an argument of command {command_args[0]} (must be separated by ';').", error_class='ArgumentParserError')
                if len(command_args) > 2:
                    # Beyond the first argument, anything (including user defined patterns) that is picked up will raise an error. 
                    for i in range(2, len(command_args)):
                        for k in env['keywords_dict'].keys():
                            if command_args[1] == k or (env['keywords_dict'][k]['builtin'] and command_args[1] == env['keywords_dict'][k]['shortcut']):
                                raise ArgumentParserError(f"Command {command_args[i]} cannot be an argument of command {command_args[0]} (must be separated by ';').", error_class='ArgumentParserError')       
            else:
                for i in range(1, len(command_args)):
                    for k in env['keywords_dict'].keys(): 
                        if command_args[i] == k or (env['keywords_dict'][k]['builtin'] and command_args[i] == env['keywords_dict'][k]['shortcut']):
                            raise ArgumentParserError(f"Command {command_args[i]} cannot be an argument of command {command_args[0]} (must be separated by ';').", error_class='ArgumentParserError')  
            commands.append(command)
    return commands


def execute_commands(commands, env):
    env = copy.deepcopy(env)
    for command in commands:
        try:
            keyword = command['cmd']
            if env['keywords_dict'][keyword]['builtin']:
                env = env['keywords_dict'][keyword]['func'](env, command['args'])
            else:
                # User defined pattern
                env = env['keywords_dict'][keyword]['func'](env, command['args'], keyword, env['keywords_dict'][keyword]['args'], env['keywords_dict'][keyword]['body'], env['keywords_dict'][keyword]['return'])
        except env['keywords_dict'][keyword]['error'] as msg:
            raise ArgumentParserError(msg, error_class=env['keywords_dict'][keyword]['error_name'])
    return env


def run_commands(statements, env):
    # Turn statements into commands that can be executed
    commands = get_commands(statements, env)
    # Execute the commands and return the modified environment
    env = execute_commands(commands, env)
    return env


def new_env():
    env = {}
    env['states_dict'] = {}
    env['measurements_dict'] = {}
    env['gates_dict'] = gates.gates_dict
    env['keywords_dict'] = {
        'new' : {'shortcut' : '\\n', 'func' : qcommands.new.command, 'error' : qcommands.new.NewCommandError, 'error_name' : 'NewCommandError', 'builtin' : True},
        'join' : {'shortcut' : '\\j', 'func' : qcommands.join.command, 'error' : qcommands.join.JoinCommandError, 'error_name' : 'JoinCommandError', 'builtin' : True},
        'rename' : {'shortcut' : '\\r', 'func' : qcommands.rename.command, 'error' : qcommands.rename.RenameCommandError, 'error_name' : 'RenameCommandError', 'builtin' : True},
        'delete' : {'shortcut' : '\\d', 'func' : qcommands.delete.command, 'error' : qcommands.delete.DeleteCommandError, 'error_name' : 'DeleteCommandError', 'builtin' : True},
        'keep' : {'shortcut' : '\\k', 'func' : qcommands.keep.command, 'error' : qcommands.keep.KeepCommandError, 'error_name' : 'KeepCommandError', 'builtin' : True},
        'apply' : {'shortcut' : '\\a', 'func' : qcommands.apply.command, 'error' : qcommands.apply.ApplyCommandError, 'error_name' : 'ApplyCommandError', 'builtin' : True},
        'measure' : {'shortcut' : '\\m', 'func' : qcommands.measure.command, 'error' : qcommands.measure.MeasureCommandError, 'error_name' : 'MeasureCommandError', 'builtin' : True},
        'state' : {'shortcut' : '\\s', 'func' : qcommands.state.command, 'error' : qcommands.state.StateCommandError, 'error_name' : 'StateCommandError', 'builtin' : True},
        'circuit' : {'shortcut' : '\\c', 'func' : qcommands.circuit.command, 'error' : qcommands.circuit.CircuitCommandError, 'error_name' : 'CircuitCommandError', 'builtin' : True},
        'prob-dist' : {'shortcut' : '\\pd', 'func' : qcommands.prob_dist.command, 'error' : qcommands.prob_dist.ProbDistCommandError, 'error_name' : 'ProbDistCommandError', 'builtin' : True},
        'if-then' : {'shortcut' : '\\it', 'func' : qcommands.if_then.command, 'error' : qcommands.if_then.IfThenCommandError, 'error_name' : 'IfThenCommandError', 'builtin' : True},
        'if-then-else' : {'shortcut' : '\\ite', 'func' : qcommands.if_then_else.command, 'error' : qcommands.if_then_else.IfThenElseCommandError, 'error_name' : 'IfThenElseCommandError', 'builtin' : True},
        'for' : {'shortcut' : '\\f', 'func' : qcommands.for_.command, 'error' : qcommands.for_.ForCommandError, 'error_name' : 'ForCommandError', 'builtin' : True},
        'while' : {'shortcut' : '\\w', 'func' : qcommands.while_.command, 'error' : qcommands.while_.WhileCommandError, 'error_name' : 'WhileCommandError', 'builtin' : True},
        'execute' : {'shortcut' : '\\e', 'func' : qcommands.execute.command, 'error' : qcommands.execute.ExecuteCommandError, 'error_name' : 'ExecuteCommandError', 'builtin' : True},
        'timer' : {'shortcut' : '\\t', 'func' : qcommands.timer.command, 'error' : qcommands.timer.TimerCommandError, 'error_name' : 'TimerCommandError', 'builtin' : True},
        'list' : {'shortcut' : '\\l', 'func' : qcommands.list.command, 'error' : qcommands.list.ListCommandError, 'error_name' : 'ListCommandError', 'builtin' : True},
        'quit' : {'shortcut' : '\\q', 'func' : qcommands.quit.command, 'error' : qcommands.quit.QuitCommandError, 'error_name' : 'QuitCommandError', 'builtin' : True},
        'help' : {'shortcut' : '\\h', 'func' : qcommands.help.command, 'error' : qcommands.help.HelpCommandError, 'error_name' : 'HelpCommandError', 'builtin' : True},
        'pattern' : {'shortcut' : '\\p', 'func' : qcommands.pattern.command, 'error' : qcommands.pattern.PatternCommandError, 'error_name' : 'PatternCommandError', 'builtin' : True},
    }
    env['tags_dict'] = {
        'new' : {'num_qubits' : ['.nq', '.num-qubits'], 'state_vector' : ['.v', '.vector']},
        'join' : {'name' : ['.n', '.name']},
        'keep_delete' : {'states' : ['.s', '.states'], 'measurements' : ['.m', '.measurements']},
    }
    # List comprehensions are just nested for loops to get the shortcuts and tags out of the dictionaries and store them in lists. 
    # These lists are for ease of use and make it so there is only one point where each tag and shortcut is defined.
    env['shortcuts'] = [env['keywords_dict'][k]['shortcut'] for k in env['keywords_dict'].keys() if env['keywords_dict'][k]['shortcut'] != None]
    env['tags'] = [tag for cmd in env['tags_dict'].keys() for tag_name in env['tags_dict'][cmd].keys() for tag in env['tags_dict'][cmd][tag_name]]
    env['disp_time'] = False
    env['quit_program'] = False
    return env


def program():
    env = new_env()
    if sys.argv[1:]:
        for x in sys.argv[1:]:
            try:
                start = time.time()
                env = run_commands(f"execute {x}", env)
                end = time.time()
                if env['disp_time']:
                    print("Time taken: " + str(end - start) + " seconds")
                # Clear environment
                env = new_env()
            except ArgumentParserError as e:
                print(f"{e.error_class}: {e.message}")                                  
    else:
        print("Welcome to CmdQuantum, a terminal-based quantum computing simulator. \nTo see a list of available commands, enter '##' and then press tab twice.\nEnter 'help' or '\\h' for more information regarding commands.\nTo quit the program, enter 'quit' or '\\q'.\n")
        readline.parse_and_bind("tab: complete")
        readline.set_completer_delims("")
        while not env['quit_program']:
            try:      
                completer_args = list(env['keywords_dict'].keys()) + env['shortcuts'] + env['tags'] 
                completer_args += ['##' + x for x in env['keywords_dict']] + ['##' + x for x in env['shortcuts']]
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
                start = time.time()
                env = run_commands(statements, env)
                end = time.time()
                if env['disp_time']:
                    print("Time taken: " + str(end - start) + " seconds")
            except ArgumentParserError as e:
                print(f"{e.error_class}: {e.message}")
    quit()