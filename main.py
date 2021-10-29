import time
import numpy as np
import argparse
import functools
import json
import re
import copy
import cProfile, pstats, io
import logic_evaluator
import gates
from quantum_state import QuantumState
from messages import help_message, error_message


class ArgumentParserError(Exception):
    __slots = 'message'
    def __init__(self, message):
        self.message = message

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

def regroup(split_statement, left_char, right_char, split_char=""):
    '''
    regroup expressions/lists after separation caused by splitting the string on split_char
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
        raise ArgumentParserError(f"incorrect syntax: missing '{right_char}'")  
    elif open_expr < 0:
        raise ArgumentParserError(f"incorrect syntax: missing '{left_char}'")
    return regrouped_expressions

def get_commands(parser, statements):
    statements = statements.replace('\n', ' ')
    statements = statements.replace("{", " { ")
    statements = statements.replace("}", " } ")
    statements = statements.replace("[", " [ ")
    statements = statements.replace("]", " ] ")
    statements = statements.split(';')
    statements = regroup(statements, "{", "}", split_char=";")
    commands = []
    for statement in statements:
        # Split the current statement on empty space
        split_statement = statement.split()
        command_args = regroup(split_statement, "{", "}", split_char=" ")
        command_args = regroup(command_args, "[", "]", split_char=" ")
        command_args = regroup(command_args, "(", ")", split_char=" ")
        command = parser.parse_args(command_args)
        commands.append(command)
    return commands

def single_command(command_obj):
    if len(command_obj) != 1:
        raise ArgumentParserError(error_message['too many commands'])
    else:
        return True

def execute_commands(parser, commands, env):
    env = copy.deepcopy(env)
    for command in commands:
        if command.new and single_command(command.new):
            num_qubits_tag = ['nq=', 'qubits=']
            preset_state_tag = ['s=', 'state=']
            command_args = command.new[0]
            new_states = []
            num_qubits = 1
            preset_state = None
            for s in command_args:
                illegal_chars = re.search("[^0-9a-zA-Z]", s)
                if s.startswith(num_qubits_tag[0]) or s.startswith(num_qubits_tag[1]):
                    if s.startswith(num_qubits_tag[0]): 
                        num_qubits = int(s[len(num_qubits_tag[0]):])
                    else:
                        num_qubits = int(s[len(num_qubits_tag[1]):])
                elif s.startswith(preset_state_tag[0]) or s.startswith(preset_state_tag[1]):
                    if s.startswith(preset_state_tag[0]):
                        preset_state = str(s[len(preset_state_tag[0]):])
                    else:
                        preset_state = str(s[len(preset_state_tag[1]):])
                elif illegal_chars:
                    raise ArgumentParserError(f"invalid character(s) in state name: {s[illegal_chars.span()[0]]}")
                else:
                    new_states.append(s)
            for s in new_states:
                env['states_dict'][s] = QuantumState(num_qubits=num_qubits, state_name=s, preset_state=preset_state)                

        if command.join and single_command(command.join):           
            name_tag = 'name='
            command_args = command.join[0]
            states_being_joined = []
            states_to_pop = []
            joint_state_name = ""
            for s in command_args:
                if s.startswith(name_tag):
                    joint_state_name = s[len(name_tag):]
                elif s in env['states_dict']:
                    states_being_joined.append(env['states_dict'][s])
                    states_to_pop.append(s)
                else:
                    raise ArgumentParserError(f"invalid parameter assignment or state that doesn't exist: {s}")
            for s in states_to_pop:
                env['states_dict'].pop(s)                               
            joint_state = functools.reduce(QuantumState.__mul__, states_being_joined)
            if joint_state_name:
                joint_state.state_name = joint_state_name
            env['states_dict'][joint_state.state_name] = joint_state

        if command.state and single_command(command.state):
            for x in command.state[0]:
                if not x in env['states_dict']:
                    raise ArgumentParserError(f"{error_message['state not found']}: {x}")
                else:
                    env['states_dict'][x].print_state()
                
        if command.circuit and single_command(command.circuit):
            for x in command.circuit[0]:
                if not x in env['states_dict']:
                    raise ArgumentParserError(f"{error_message['state not found']}: {x}")
                else:
                    env['states_dict'][x].print_circuit()
                
        if command.probs and single_command(command.probs):
            for x in command.probs[0]:
                if not x in env['states_dict']:
                    raise ArgumentParserError(f"{error_message['state not found']}: {x}")
                else:
                    env['states_dict'][x].print_probabilities()

        if command.apply and single_command(command.apply):
            def check_qubits_apply_gate(s, required_num_qubits, qubit_refs, gate_name):
                if required_num_qubits == 1:
                    gate_func = gates.one_arg_gates.get(gate_name)
                elif required_num_qubits == 2:
                    gate_func = gates.two_arg_gates.get(gate_name)
                final_qubits = []
                for qs in qubit_refs:
                    current_qubits = []
                    try:
                        qs = json.loads(qs)
                        if isinstance(qs, list) and required_num_qubits == len(qs):
                            int_qs = [int(x) for x in qs]
                            current_qubits.append(int_qs) 
                        elif isinstance(qs, int) and required_num_qubits == 1:
                            int_qs = qs
                            current_qubits.append(int_qs)
                        else:
                            raise ArgumentParserError(f"{error_message['incorrect input for gate']} {gate_name}: {qs}")
                    except (json.decoder.JSONDecodeError, TypeError, ValueError):
                        # TypeError example: [1,[2]]
                        # ValueError example: [1, "hello"]
                        raise ArgumentParserError(f"{error_message['invalid qubit ref']}: {qs}")
                    for curr_q in current_qubits:
                        out_of_bounds = False
                        if isinstance(curr_q, int):
                            if not (0 <= curr_q <= s.num_qubits):
                                out_of_bounds = True 
                        elif isinstance(curr_q, list):
                            for x in curr_q:
                                if not (0 <= x <= s.num_qubits):
                                    out_of_bounds = True
                        if not out_of_bounds:
                            final_qubits.append(curr_q)
                        else:
                            raise ArgumentParserError(f"qubit reference(s) out of bounds: {curr_q}")
                for qs in final_qubits:
                    qs_list = []
                    if isinstance(qs, int):
                        qs_list.append(qs)
                    else: 
                        for q in qs:
                            qs_list.append(q)
                    gate_func(s, *qs_list)
            command_args = command.apply[0]
            gate_name = command_args[0]
            s = command_args[1]
            qubit_refs = command_args[2:]
            if s not in env['states_dict']:
                raise ArgumentParserError(f"{error_message['state not found']}: {s}")
            else: 
                s = env['states_dict'][s]
            if not qubit_refs:
                raise ArgumentParserError(f"{error_message['no qubit ref']}")
            if gate_name in gates.one_arg_gates:
                check_qubits_apply_gate(s, 1, qubit_refs, gate_name)                       
            elif gate_name in gates.two_arg_gates:
                check_qubits_apply_gate(s, 2, qubit_refs, gate_name)
            else: 
                raise ArgumentParserError(f"{error_message['gate not found']}: {gate_name}")             

        if command.measure and single_command(command.measure):
            make_vars_tag = ['vars', 'variables']
            command_args = command.measure[0]
            s = command_args[0]
            args = command_args[1:]
            qubit_refs = []
            make_vars = False
            for a in args:
                if a.startswith(make_vars_tag[0]) or a.startswith(make_vars_tag[1]):
                    make_vars = True
                else:
                    qubit_refs.append(a)
            if s not in env['states_dict']:
                raise ArgumentParserError(f"{error_message['state not found']}: {s}")
            else:
                s = env['states_dict'][s]
            if not qubit_refs:
                raise ArgumentParserError(f"{error_message['no qubit ref']}")
            final_qubits = []
            for q in qubit_refs:
                try:
                    q = json.loads(q)
                    q = int(q)
                except (json.decoder.JSONDecodeError, TypeError, ValueError):
                    raise ArgumentParserError(f"{error_message['invalid qubit ref']}: {q}")
                if not (0 <= q <= s.num_qubits):
                    raise ArgumentParserError(f"qubit reference(s) out of bounds: {q}")        
                else:
                    final_qubits.append(q)
            for q in final_qubits:
                bit = s.measurement(int(q))
                if make_vars:
                    env['vars_dict'][f"{s.state_name}.{q}"] = bit

        if command.rename and single_command(command.rename):
            command_args = command.rename[0]
            s = command_args[0]
            new_s = command_args[1]
            if s not in env['states_dict']:
                raise ArgumentParserError(f"{error_message['state not found']}: {s}")                                   
            illegal_chars = re.search("[^0-9a-zA-Z]", new_s)
            if illegal_chars:
                raise ArgumentParserError(f"invalid character(s) in state name: {new_s[illegal_chars.span()[0]]}")
            s_object = env['states_dict'][s]
            s_object.state_name = new_s
            env['states_dict'].pop(s)
            env['states_dict'].update({new_s : s_object})

        if command.timer and single_command(command.timer):
            command_args = command.timer[0]
            decision = command_args[0].upper()
            if decision == "ON":
                env['disp_time'] = True 
            elif decision == "OFF":
                env['disp_time'] = False
            else:
                raise ArgumentParserError(f"incorrect option for timer: {decision}")

        if command.list:
            print(f"states: {list(env['states_dict'].keys())}")
            print(f"variables: {list(env['vars_dict'].keys())}")

        if command.quit:
            env['quit_program'] = True
                        
        if command.help:
            print(help_message)

        if command.if_then and single_command(command.if_then):
            command_args = command.if_then[0]
            if_condition = command_args[0][1:len(command_args[0])-1]
            then_statements = command_args[1][1:len(command_args[1])-1]
            execute_then_statements = logic_evaluator.interpret(if_condition, user_env=env['vars_dict'])
            if execute_then_statements == True:
                commands = get_commands(parser, then_statements)
                env = execute_commands(parser, commands, env)

        if command.if_then_else and single_command(command.if_then_else):
            command_args = command.if_then_else[0]
            if_condition = command_args[0][1:len(command_args[0])-1]
            then_statements = command_args[1][1:len(command_args[1])-1]
            else_statements = command_args[2][1:len(command_args[2])-1]
            execute_then_statements = logic_evaluator.interpret(if_condition, user_env=env['vars_dict'])
            if execute_then_statements == True:
                commands = get_commands(parser, then_statements)
                env = execute_commands(parser, commands, env)
            elif execute_then_statements == False:
                commands = get_commands(parser, else_statements)
                env = execute_commands(parser, commands, env)

        if command.for_each and single_command(command.for_each):
            command_args = command.for_each[0]
            i_arg = command_args[0]
            iterable_arg = command_args[1]
            statements = command_args[2]
            iterable_arg = iterable_arg[1:len(iterable_arg)-1].split(',')
            iterable_arg = [int(x) for x in iterable_arg]
            if iterable_arg[0] <= iterable_arg[1]:
                iterable_arg[1] += 1
            else:
                iterable_arg[1] -= 1
            iterable = range(*tuple(iterable_arg))
            # iterate a number of times as specified by user
            for i in iterable:
                statements_i = statements.replace(f' {i_arg}}}', f' {i} ')
                statements_i = statements.replace(f' {i_arg} ', f' {i} ')
                statements_i = statements_i[1:len(command_args[2])-1]
                commands = get_commands(parser, statements_i)
                # Execute the current command(s), and return env
                env = execute_commands(parser, commands, env)

        if command.execute and single_command(command.execute):
            command_args = command.execute[0]
            file_name = command_args[0]
            try:
                with open(f"{file_name}.clqc", 'r') as file:
                    script = file.read()
                    commands = get_commands(parser, script)
                    env = execute_commands(parser, commands, env)
            except FileNotFoundError:
                raise ArgumentParserError(f"file not found: {file_name}")

    return env

def main():
    print("Welcome to my terminal-based quantum computing simulator. \nEnter --help or -h for more information. To quit the program, enter --quit or -q.\n")
    parser = ThrowingArgumentParser(allow_abbrev=False, add_help=False)
    g = parser.add_mutually_exclusive_group()
    g.add_argument('-n', '--new', nargs='+', action='append')
    g.add_argument('-j', '--join', nargs='+', action='append')
    g.add_argument('-s', '--state', nargs='+', action='append')
    g.add_argument('-c', '--circuit', nargs='+', action='append')
    g.add_argument('-p', '--probs', nargs='+', action='append')
    g.add_argument('-a', '--apply', nargs='+', action='append')
    g.add_argument('-m', '--measure', nargs='+', action='append')
    g.add_argument('-r', '--rename', nargs=2, action='append')
    g.add_argument('-t', '--timer', nargs=1, action='append')
    g.add_argument('-l', '--list', action='store_true')
    g.add_argument('-q', '--quit', action='store_true')
    g.add_argument('-h', '--help', action='store_true')
    g.add_argument('-i-t', '--if-then', nargs=2, action='append')
    g.add_argument('-i-t-e', '--if-then-else', nargs=3, action='append')
    g.add_argument('-f-e', '--for-each', nargs=3, action='append')
    g.add_argument('-e', '--execute', nargs=1, action='append')
    env = {}
    env['states_dict'] = {}
    env['vars_dict'] = {}
    env['disp_time'] = False
    env['quit_program'] = False
    while not env['quit_program']:
        try:      
            statements = input('#~: ')
            start = time.time()
            # pr = cProfile.Profile()
            # pr.enable()
            # Parse the current statement(s) and return command(s) that can be acted on
            commands = get_commands(parser, statements)
            # Execute the current command(s), and return env
            env = execute_commands(parser, commands, env)
            # pr.disable()
            # s = io.StringIO()
            # ps = pstats.Stats(pr, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
            # ps.print_stats()
            # print(s.getvalue())
            end = time.time()
            if env['disp_time']:
                print("Time taken: " + str(end - start) + " seconds")
        except ArgumentParserError as e:
            print(f"ERROR: {e.message}")

    quit()

if __name__ == '__main__':
    main()