import time
import numpy as np
import argparse
import functools
import json
import gates
from quantum_state import QuantumState
from messages import help_message, error_message

class ArgumentParserError(Exception): 
    pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

# def regroup(split_statement, command_args, left_char, right_char, must_be_list=False, must_be_expr=False):
#     i = 0
#     num_splits = len(split_statement)
#     if must_be_expr:
#         separator = " "
#     else:
#         separator = ""
#     while i < num_splits:
#         # We might have encountered a list or expr
#         if left_char in split_statement[i]:
#             # arr will store the squeezed list/expr
#             arr = split_statement[i]
#             # If the list/expr ends in the same piece of the split statement, we end here
#             if right_char in split_statement[i]:
#                 pass
#             # Otherwise, search the rest of the statment splits, concatenating until arr end 
#             else:
#                 for  j in range(i+1, num_splits):
#                     arr += separator + split_statement[j]
#                     if right_char in split_statement[j]:
#                         i = j
#                         break               
#             if must_be_list:
#                 try:
#                     # If the arr we have found is actually a list, append to command args
#                     if isinstance(json.loads(arr), list):
#                         command_args.append(arr)
#                 except json.decoder.JSONDecodeError:
#                     # If not, declare invalid
#                     raise ArgumentParserError(f"incorrect list syntax or invalid type(s) in list: {arr}")
#             else:
#                 command_args.append(arr)
#         elif right_char in split_statement[i]:
#             raise ArgumentParserError(f"encountered {right_char} before {left_char}: {split_statement[i]}")
#         else:
#             command_args.append(split_statement[i])
#         i += 1
#     print(command_args)
#     return command_args

def regroup(split_statement, left_char, right_char, split_char=""):
    '''
    regroup expressions/lists.
    important to specify split_char, otherwise regrouped expressions/lists will not be reconstructed correctly.
    '''
    regrouped_expressions = []
    num_splits = len(split_statement)
    i = 0
    open_expr = False
    current_statement = ""
    while i < num_splits:    
        c = 0
        len_current_split = len(split_statement[i])
        while c < len_current_split:
            # opening expression
            if open_expr == False and left_char == split_statement[i][c]:
                open_expr = True

            # closing expression
            elif open_expr == True and right_char == split_statement[i][c]:
                open_expr = False

            # error
            elif open_expr == True and left_char == split_statement[i][c]:
                pass

            # error
            elif open_expr == False and right_char == split_statement[i][c]:
                pass 
            c += 1
        if not open_expr:
            regrouped_expressions.append(current_statement + split_statement[i])    
            current_statement = ""
        else:
            current_statement += split_statement[i] + split_char
        i += 1
    # error
    if open_expr:
        pass
    return regrouped_expressions

def get_command(parser, statement):
    # Split the current statement on empty space
    split_statement = statement.split()
    command_args = regroup(split_statement, "{", "}", split_char=" ")
    command_args = regroup(command_args, "[", "]", split_char="")
    command = parser.parse_args(command_args)
    return command

def execute_command(parser, command, states_dict, vars_dict, disp_time, command_quit):
    if command.new:
        num_qubits_tag = ['nq=', 'num_qubits=']
        preset_state_tag = ['ps=', 'preset_state=']
        if len(command.new) != 1:
            raise ArgumentParserError(error_message['too many commands'])
        else:
            command_args = command.new[0]
            new_states = []
            num_qubits = 1
            preset_state = None
            for s in command_args:
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
                elif '[' in s or ']' in s or '=' in s or '-' in s:
                    raise ArgumentParserError(f"{error_message['invalid new name']}: {s}")
                else:
                    new_states.append(s)
            for s in new_states:
                states_dict[s] = QuantumState(num_qubits=num_qubits, state_name=s, preset_state=preset_state)                

    if command.join:
        name_tag = 'name='
        if len(command.join) != 1:
            raise ArgumentParserError(error_message['too many commands'])
        else:
            command_args = command.join[0]
            states_being_joined = []
            states_to_pop = []
            joint_state_name = ""
            for s in command_args:
                if s.startswith(name_tag):
                    joint_state_name = s[len(name_tag):]
                elif s in states_dict:
                    states_being_joined.append(states_dict[s])
                    states_to_pop.append(s)
                else:
                    raise ArgumentParserError(f"invalid parameter assignment or state that doesn't exist: {s}")
            for s in states_to_pop:
                states_dict.pop(s)                               
            joint_state = functools.reduce(QuantumState.__mul__, states_being_joined)
            if joint_state_name:
                joint_state.state_name = joint_state_name
            states_dict[joint_state.state_name] = joint_state

    if command.state:
        if len(command.state) != 1:
            raise ArgumentParserError(error_message['too many commands'])
        else:
            for x in command.state[0]:
                if not x in states_dict:
                    raise ArgumentParserError(f"{error_message['state not found']}: {x}")
                else:
                    states_dict[x].print_state()
            
    if command.circuit:
        if len(command.circuit) != 1:
            raise ArgumentParserError(error_message['too many commands'])
        else:
            for x in command.circuit[0]:
                if not x in states_dict:
                    raise ArgumentParserError(f"{error_message['state not found']}: {x}")
                else:
                    states_dict[x].print_circuit()
            
    if command.probs:
        if len(command.probs) != 1:
            raise ArgumentParserError(error_message['too many commands'])
        else:
            for x in command.probs[0]:
                if not x in states_dict:
                    raise ArgumentParserError(f"{error_message['state not found']}: {x}")
                else:
                    states_dict[x].print_probabilities()

    if command.apply:
        def check_qubits_apply_gate(s, required_num_qubits, qubit_refs, gate_name, qubit_dict):
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
            qubit_dict_keys = [x for x in qubit_dict]
            for qs in final_qubits:
                qs_dict = {}
                if isinstance(qs, int):
                    qs_dict[qubit_dict_keys[0]] = qs
                else: 
                    for i in range(len(qs)):
                        qs_dict[qubit_dict_keys[i]] = qs[i]
                gate_func(s, **qs_dict)
        if len(command.apply) != 1:
            raise ArgumentParserError(error_message['too many commands'])
        else:
            command_args = command.apply[0]
            gate_name = command_args[0]
            s = command_args[1]
            qubit_refs = command_args[2:]
            if s not in states_dict:
                raise ArgumentParserError(f"{error_message['state not found']}: {s}")
            else: 
                s = states_dict[s]
            if not qubit_refs:
                raise ArgumentParserError(f"{error_message['no qubit ref']}")
            if gate_name in gates.one_arg_gates:
                qubit_dict = {'qubit' : None}
                check_qubits_apply_gate(s, 1, qubit_refs, gate_name, qubit_dict)                       
            elif gate_name in gates.two_arg_gates:
                qubit_dict = {'control' : None, 'target' : None}
                check_qubits_apply_gate(s, 2, qubit_refs, gate_name, qubit_dict)
            else: 
                raise ArgumentParserError(f"{error_message['gate not found']}: {gate_name}")             

    if command.measure:
        make_vars_tag = ['mv', 'make_vars']
        if len(command.measure) != 1:
            raise ArgumentParserError(error_message['too many commands'])
        else:
            command_args = command.measure[0]
            s = command_args[0]
            args = command_args[1:]
            qubit_refs = []
            make_var = False
            for a in args:
                if a.startswith(make_vars_tag[0]) or a.startswith(make_vars_tag[1]):
                    make_vars = True
                else:
                    qubit_refs.append(a)

            if s not in states_dict:
                raise ArgumentParserError(f"{error_message['state not found']}: {s}")
            else:
                s = states_dict[s]
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
                vars_dict[f"{s.state_name}.{q}"] = bit

    if command.rename:
        if len(command.rename) != 1:
            raise ArgumentParserError(error_message['too many commands'])
        else:
            command_args = command.rename[0]
            s = command_args[0]
            new_s = command_args[1]
            if s not in states_dict:
                raise ArgumentParserError(f"{error_message['state not found']}: {s}")                   
            else: 
                s = states_dict[s]
            states_dict.pop(command_args[0])
            s.state_name = command_args[1]
            states_dict.update({command_args[1] : s})

    if command.timer:
        if len(command.timer) != 1:
            raise ArgumentParserError(error_message['too many commands'])
        else:
            command_args = command.timer[0]
            decision = command_args[0].upper()
            if decision == "ON":
                disp_time = True 
            elif decision == "OFF":
                disp_time = False
            else:
                raise ArgumentParserError(f"incorrect option for timer: {decision}")

    if command.list:
        print(f"states: {list(states_dict.keys())}")
        print(f"variables: {list(vars_dict.keys())}")

    if command.quit:
        command_quit = True
                    
    if command.help:
        print(help_message)

    if command.if_then:
        if len(command.if_then) != 1:
            raise ArgumentParserError(error_message['too many commands'])
        else:
            command_args = command.if_then[0]
            if_condition = command_args[0][1:len(command_args[0])-1]
            then_statements = command_args[1][1:len(command_args[1])-1]
            
            execute_then_statements = False
            if_condition = if_condition.split('==')
            if_condition = [x.strip() for x in if_condition]
            if len(if_condition) != 2:
                # error
                pass
            else:
                left_hs = if_condition[0]
                right_hs = if_condition[1]
                # vars_dict.get(left_hs) was a bad idea. 0 evaluates to false so if our bit is zero, that condition would fail...
                if left_hs in vars_dict: 
                    left_hs = vars_dict[left_hs]
                elif isinstance(json.loads(left_hs), int):
                    left_hs = int(left_hs)
                else:
                    # error 
                    pass
                if right_hs in vars_dict:
                    right_hs = vars_dict[right_hs]
                elif isinstance(json.loads(right_hs), int):
                    right_hs = int(right_hs)
                else:
                    # error 
                    pass
                
                if left_hs == right_hs:
                    execute_then_statements = True

            if execute_then_statements:
                then_statements = then_statements.split('|')
                then_statements = regroup(then_statements, "{", "}", split_char="|")
                for then_statement in then_statements:
                    # Parse the current statement and return a command that can be acted on
                    then_command = get_command(parser, then_statement)
                    # Execute the command, and return states_dict, disp_time and command_quit
                    states_dict, vars_dict, disp_time, command_quit = execute_command(parser, then_command, states_dict, vars_dict, disp_time, command_quit)
    
    return states_dict, vars_dict, disp_time, command_quit

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

    states_dict = {}
    vars_dict = {}
    disp_time = False
    command_quit = False
    while not command_quit:
        try:      
            # Take user input and separate statements by splitting on pipes
            statements = input('#~: ')
            start = time.time()
            statements = statements.split('|')
            statements = regroup(statements, "{", "}", split_char="|")
            successful_executes = 0
            for statement in statements:
                # Parse the current statement and return a command that can be acted on
                command = get_command(parser, statement)
                # Execute the command, and return states_dict, disp_time and command_quit
                states_dict, vars_dict, disp_time, command_quit = execute_command(parser, command, states_dict, vars_dict, disp_time, command_quit)
                successful_executes += 1
            end = time.time()
            if disp_time:
                print("Time taken: " + str(end - start) + " seconds")

        except ArgumentParserError as e:
            print(f"ERROR: {e}")
            print(f"commands successfully executed: {successful_executes}")
              
    quit()

if __name__ == '__main__':
    main()  