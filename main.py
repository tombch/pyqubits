import readline
import sys
import time
import re
import copy
import logic_evaluator
import gates
import qcommands
from qcommands import verifiers as v
from quantum_state import QuantumState


class ArgumentParserError(Exception):
    __slots = 'message', 'error_class'
    def __init__(self, message, error_class=None):
        self.message = message
        self.error_class = error_class


def regroup(split_statement, left_char, right_char, split_char=""):
    '''
    Re-group expressions/lists after separation caused by splitting the string on split_char.
    split_char must be specified when calling regroup, otherwise expressions/lists may be reconstructed incorrectly.
    '''
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
        raise ArgumentParserError(f"Incorrect syntax: missing '{right_char}' to close expression.",  error_class='ArgumentParserError')
    elif open_expr < 0:
        raise ArgumentParserError(f"Incorrect syntax: missing '{left_char}' to close expression.",  error_class='ArgumentParserError')
    return regrouped_expressions


def get_commands(statements):
    keywords = ['new', 'join', 'rename', 'delete', 'keep', 'state', 'circuit', 'probs', 'apply', 'measure', 'timer', 'if-then', 'if-then-else', 'for-each', 'execute', 'list', 'quit', 'help'] 
    statements = statements.replace('\n', ' ')
    statements = statements.replace("{", " { ")
    statements = statements.replace("}", " } ")
    statements = statements.replace("[", " [ ")
    statements = statements.replace("]", " ] ")
    statements = statements.replace("(", " ( ")
    statements = statements.replace(")", " ) ")
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
                            evaluated_x = logic_evaluator.interpret(x[1:len(x)-1], accept_type_errors=True)
                        except logic_evaluator.LogicEvaluatorError as msg:
                            raise ArgumentParserError(msg, error_class='LogicEvaluatorError')      
                        if evaluated_x != None and not isinstance(evaluated_x, str):
                            command_args[i] = command_args[i].replace(x, str(evaluated_x))
            command = {}
            for i in range(len(keywords)):
                if command_args[0] == keywords[i]:
                    command = {'cmd' : keywords[i], 'args' : command_args[1:]}
                    break
            if not command:
                raise ArgumentParserError(f"Unrecognised command: {command_args[0]}", error_class='ArgumentParserError')
            for i in range(1, len(command_args)):
                if command_args[i] in keywords:
                    raise ArgumentParserError(f"Command {command_args[i]} cannot be an argument of command {command_args[0]} (must be separated by ';').", error_class='ArgumentParserError')
            commands.append(command)
    return commands


def execute_commands(commands, env):
    keywords = {
        'new' : {'func' : qcommands.new.command, 'error' : qcommands.new.NewCommandError, 'error_name' : 'NewCommandError'},
        'join' : {'func' : qcommands.join.command, 'error' : qcommands.join.JoinCommandError, 'error_name' : 'JoinCommandError'},
        'rename' : {'func' : qcommands.rename.command, 'error' : qcommands.rename.RenameCommandError, 'error_name' : 'RenameCommandError'},
        'delete' : {'func' : qcommands.delete.command, 'error' : qcommands.delete.DeleteCommandError, 'error_name' : 'DeleteCommandError'},
        'keep' : {'func' : qcommands.keep.command, 'error' : qcommands.keep.KeepCommandError, 'error_name' : 'KeepCommandError'},
        'apply' : {'func' : qcommands.apply.command, 'error' : qcommands.apply.ApplyCommandError, 'error_name' : 'ApplyCommandError'},
        'measure' : {'func' : qcommands.measure.command, 'error' : qcommands.measure.MeasureCommandError, 'error_name' : 'MeasureCommandError'},
        'state' : {'func' : qcommands.state.command, 'error' : qcommands.state.StateCommandError, 'error_name' : 'StateCommandError'},
        'circuit' : {'func' : qcommands.circuit.command, 'error' : qcommands.circuit.CircuitCommandError, 'error_name' : 'CircuitCommandError'},
        'probs' : {'func' : qcommands.probs.command, 'error' : qcommands.probs.ProbabilitiesCommandError, 'error_name' : 'ProbabilitiesCommandError'},
        'if-then' : {'func' : qcommands.if_then.command, 'error' : qcommands.if_then.IfThenCommandError, 'error_name' : 'IfThenCommandError'},
        'if-then-else' : {'func' : qcommands.if_then_else.command, 'error' : qcommands.if_then_else.IfThenElseCommandError, 'error_name' : 'IfThenElseCommandError'},
        'for-each' : {'func' : qcommands.for_each.command, 'error' : qcommands.for_each.ForEachCommandError, 'error_name' : 'ForEachCommandError'},
        'execute' : {'func' : qcommands.execute.command, 'error' : qcommands.execute.ExecuteCommandError, 'error_name' : 'ExecuteCommandError'},
        'timer' : {'func' : qcommands.timer.command, 'error' : qcommands.timer.TimerCommandError, 'error_name' : 'TimerCommandError'},
        'list' : {'func' : qcommands.list.command, 'error' : qcommands.list.ListCommandError, 'error_name' : 'ListCommandError'},
        'quit' : {'func' : qcommands.quit.command, 'error' : qcommands.quit.QuitCommandError, 'error_name' : 'QuitCommandError'},
        'help' : {'func' : qcommands.help.command, 'error' : qcommands.help.HelpCommandError, 'error_name' : 'HelpCommandError'},
    }
    env = copy.deepcopy(env)
    for command in commands:
        try:
            env = keywords[command['cmd']]['func'](env, command['args'])
        except keywords[command['cmd']]['error'] as msg:
            raise ArgumentParserError(msg, error_class=keywords[k]['error_name'])
    return env


def program():
    env = {}
    env['states_dict'] = {}
    env['measurements_dict'] = {}
    env['gates_dict'] = gates.gates_dict
    env['disp_time'] = False
    env['quit_program'] = False
    if sys.argv[1:]:
        for x in sys.argv[1:]:
            try:
                start = time.time()
                commands = get_commands(f"execute {x}")
                env = execute_commands(commands, env)
                end = time.time()
                if env['disp_time']:
                    print("Time taken: " + str(end - start) + " seconds")
                # Clear environment
                env = {}
                env['states_dict'] = {}
                env['measurements_dict'] = {}
                env['gates_dict'] = gates.gates_dict
                env['disp_time'] = False
                env['quit_program'] = False
            except ArgumentParserError as e:
                print(f"{e.error_class}: {e.message}")                                  
    else:
        print("Welcome to QCmd, a terminal-based quantum computing simulator. \nTo see a list of available commands, enter '-' and then press tab twice.\nEnter 'help' or '-h' for more information regarding commands.\nTo quit the program, enter 'quit' or '-q'.\n")
        readline.parse_and_bind("tab: complete")
        old_delims = readline.get_completer_delims()
        readline.set_completer_delims(old_delims.replace('-', ''))
        while not env['quit_program']:
            try:      
                def completer(text, state):
                    arguments = ['new', 'join', 'rename', 'delete', 'keep', 'state', 'circuit', 'probs', 'apply', 'measure', 'timer', 'if-then', 'if-then-else', 'for-each', 'execute', 'list', 'quit', 'help',
                                '--new', '--join', '--rename', '--delete', '--keep', '--state', '--circuit', '--probs', '--apply', '--measure', '--timer', '--if-then', '--if-then-else', '--for-each', '--execute', '--list', '--quit', '--help',
                                '.qs=', '.qubits=', '.p=', '.preset=', '.name=', '.s', '.state', '.states', '.m', '.measurement', '.measurements',
                                '-n', '-j', '-r', '-d', '-k', '-a', '-m', '-s', '-c', '-p', '-i-t', '-i-t-e', '-f-e', '-e', '-t', '-l', '-q', '-h']
                    arguments += env['states_dict'].keys()
                    arguments += env['measurements_dict'].keys()
                    arguments += env['gates_dict'].keys()
                    options = [i for i in arguments if len(text) > 0 and i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None
                readline.set_completer(completer)
                statements = input('#~: ')
                start = time.time()
                # Parse the current statement(s) and return command(s) that can be acted on
                commands = get_commands(statements)
                # Execute the current command(s), and return env
                env = execute_commands(commands, env)
                end = time.time()
                if env['disp_time']:
                    print("Time taken: " + str(end - start) + " seconds")
            except ArgumentParserError as e:
                print(f"{e.error_class}: {e.message}")
    quit()