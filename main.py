import readline
import sys
import time
import argparse
import re
import copy
import logic_evaluator
import gates
import qcommands
from qcommands import verifiers as v
from quantum_state import QuantumState
from messages import help_message, error_message


class ArgumentParserError(Exception):
    __slots = 'message', 'error_class'
    def __init__(self, message, error_class=None):
        self.message = message
        self.error_class = error_class


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)


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


def get_commands(parser, statements):
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
        try:
            command = parser.parse_args(command_args)
        except Exception as e: # TODO - change this exception handling
            e_message = str(e) # Very hacky, argparse probably needs to go
            e_message= e_message[0].upper() + e_message[1:]
            raise ArgumentParserError(e_message, error_class='ArgumentParserError')
        commands.append(command)
    return commands


def is_single_command(command_obj):
    if len(command_obj) != 1:
        raise ArgumentParserError("Argument cannot be used twice in one command (should be separated by ';')", error_class='ArgumentParserError')
    else:
        return True


def execute_commands(parser, commands, env):
    env = copy.deepcopy(env)
    for command in commands:
        if command.new and is_single_command(command.new):
            try:
                env = qcommands.new.command(env, command.new[0])
            except qcommands.new.NewCommandError as msg:
                raise ArgumentParserError(msg, error_class='NewCommandError')

        if command.join and is_single_command(command.join):           
            try:
                env = qcommands.join.command(env, command.join[0])
            except qcommands.join.JoinCommandError as msg:
                raise ArgumentParserError(msg, error_class='JoinCommandError')          

        if command.rename and is_single_command(command.rename):
            try:
                env = qcommands.rename.command(env, command.rename[0])
            except qcommands.rename.RenameCommandError as msg:
                raise ArgumentParserError(msg, error_class='RenameCommandError')  

        if command.delete and is_single_command(command.delete):
            try:
                env = qcommands.delete.command(env, command.delete[0])
            except qcommands.delete.DeleteCommandError as msg:
                raise ArgumentParserError(msg, error_class='DeleteCommandError')

        if command.keep and is_single_command(command.keep):
            try:
                env = qcommands.keep.command(env, command.keep[0])
            except qcommands.keep.KeepCommandError as msg:
                raise ArgumentParserError(msg, error_class='KeepCommandError')

        if command.apply and is_single_command(command.apply):
            try:
                env = qcommands.apply.command(env, command.apply[0])
            except qcommands.apply.ApplyCommandError as msg:
                raise ArgumentParserError(msg, error_class='ApplyCommandError')          

        if command.measure and is_single_command(command.measure):
            try:
                env = qcommands.measure.command(env, command.measure[0])
            except qcommands.measure.MeasureCommandError as msg:
                raise ArgumentParserError(msg, error_class='MeasureCommandError')  

        if command.state and is_single_command(command.state):
            try:
                env = qcommands.state.command(env, command.state[0])
            except qcommands.state.StateCommandError as msg:
                raise ArgumentParserError(msg, error_class='StateCommandError')
                
        if command.circuit and is_single_command(command.circuit):
            try:
                env = qcommands.circuit.command(env, command.circuit[0])
            except qcommands.circuit.CircuitCommandError as msg:
                raise ArgumentParserError(msg, error_class='CircuitCommandError')
                
        if command.probs and is_single_command(command.probs):
            try:
                env = qcommands.probs.command(env, command.probs[0])
            except qcommands.probs.ProbabilitiesCommandError as msg:
                raise ArgumentParserError(msg, error_class='ProbabilitiesCommandError')

        if command.if_then and is_single_command(command.if_then):
            try:
                env = qcommands.if_then.command(parser, env, command.if_then[0])
            except qcommands.if_then.IfThenCommandError as msg:
                raise ArgumentParserError(msg, error_class='IfThenCommandError') 

        if command.if_then_else and is_single_command(command.if_then_else):
            try:
                env = qcommands.if_then_else.command(parser, env, command.if_then_else[0])
            except qcommands.if_then_else.IfThenElseCommandError as msg:
                raise ArgumentParserError(msg, error_class='IfThenElseCommandError')

        if command.for_each and is_single_command(command.for_each):
            try:
                env = qcommands.for_each.command(parser, env, command.for_each[0])
            except qcommands.for_each.ForEachCommandError as msg:
                raise ArgumentParserError(msg, error_class='ForEachCommandError')

        if command.execute and is_single_command(command.execute):
            try:
                env = qcommands.execute.command(parser, env, command.execute[0])
            except qcommands.execute.ExecuteCommandError as msg:
                raise ArgumentParserError(msg, error_class='ExecuteCommandError')

        if command.timer and is_single_command(command.timer):
            try:
                env = qcommands.timer.command(env, command.timer[0])
            except qcommands.timer.TimerCommandError as msg:
                raise ArgumentParserError(msg, error_class='TimerCommandError') 

        if command.list:
            print(f"states: {list(env['states_dict'].keys())}")
            print(f"measurements: {list(env['measurements_dict'].keys())}")

        if command.quit:
            env['quit_program'] = True
                        
        if command.help:
            print(help_message)

    return env


def main():
    parser = ThrowingArgumentParser(allow_abbrev=False, add_help=False)
    g = parser.add_mutually_exclusive_group()
    g.add_argument('-n', '--new', nargs='+', action='append')
    g.add_argument('-j', '--join', nargs='+', action='append')
    g.add_argument('-r', '--rename', nargs='+', action='append')
    g.add_argument('-d', '--delete', nargs='+', action='append') # TODO
    g.add_argument('-k', '--keep', nargs='+', action='append') # TODO
    g.add_argument('-a', '--apply', nargs='+', action='append')
    g.add_argument('-m', '--measure', nargs='+', action='append')
    g.add_argument('-s', '--state', nargs='+', action='append')
    g.add_argument('-c', '--circuit', nargs='+', action='append')
    g.add_argument('-p', '--probs', nargs='+', action='append')
    g.add_argument('-i-t', '--if-then', nargs='+', action='append')
    g.add_argument('-i-t-e', '--if-then-else', nargs='+', action='append')
    g.add_argument('-f-e', '--for-each', nargs='+', action='append')
    g.add_argument('-e', '--execute', nargs=1, action='append') # TODO
    g.add_argument('-t', '--timer', nargs='+', action='append')
    g.add_argument('-l', '--list', action='store_true') # TODO
    g.add_argument('-q', '--quit', action='store_true') # TODO
    g.add_argument('-h', '--help', action='store_true') # TODO

    env = {}
    env['states_dict'] = {}
    env['measurements_dict'] = {}
    env['gates_dict'] = gates.gates_dict
    env['disp_time'] = False
    env['quit_program'] = False

    if sys.argv[1:]:
        for x in sys.argv[1:]:
            try:
                commands = get_commands(parser, f"--execute {x}")
                env = execute_commands(parser, commands, env)
            except ArgumentParserError as e:
                print(f"{e.error_class}: {e.message}")         
    else:
        print("Welcome to QCmd, a terminal-based quantum computing simulator. \nEnter --help or -h for more information. To quit the program, enter --quit or -q.\n")
        readline.parse_and_bind("tab: complete")
        old_delims = readline.get_completer_delims()
        readline.set_completer_delims(old_delims.replace('-', ''))
        while not env['quit_program']:
            try:      
                def completer(text, state):
                    arguments = ['--new', '--join', '--rename', '--delete', '--keep', '--state', '--circuit', '--probs', 
                                '--apply', '--measure', '--timer', '--if-then', '--if-then-else', '--for-each', '--execute', '--list', '--quit', '--help', 
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
                commands = get_commands(parser, statements)
                # Execute the current command(s), and return env
                env = execute_commands(parser, commands, env)
                end = time.time()
                if env['disp_time']:
                    print("Time taken: " + str(end - start) + " seconds")
            except ArgumentParserError as e:
                print(f"{e.error_class}: {e.message}")

    quit()


if __name__ == '__main__':
    main()
