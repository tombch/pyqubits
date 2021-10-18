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

def get_command(parser, statement):
    # Split the current statement by spaces (multiple adjacent spaces are considered one split)
    split_statement = statement.split()
    num_splits = len(split_statement)
    command_args = []
    i = 0
    while i < num_splits:
        # We might have encountered a list
        if '[' in split_statement[i]:
            # arr will store the squeezed list
            arr = split_statement[i]
            # If the list ends in the same piece of the split statement, we end here
            if ']' in split_statement[i]:
                pass
            # Otherwise, search the rest of the statment splits, concatenating until arr end 
            else:
                for  j in range(i+1, num_splits):
                    arr += split_statement[j]
                    if ']' in split_statement[j]:
                        i = j
                        break               
            try:
                # If the arr we have found is actually a list, append to command args
                if isinstance(json.loads(arr), list):
                    command_args.append(arr)
            except json.decoder.JSONDecodeError:
                # If not, declare invalid
                raise ArgumentParserError(f"incorrect list syntax or invalid type(s) in list: {arr}")
        elif ']' in split_statement[i]:
            raise ArgumentParserError(f"encountered ']' before '[': {split_statement[i]}")
        else:
            command_args.append(split_statement[i])
        i += 1
    command = parser.parse_args(command_args)
    return command

def main():
    print("Welcome to my terminal-based quantum computing simulator. \nEnter --help or -h for more information. To quit the program, enter --quit or -q.")
    parser = ThrowingArgumentParser(allow_abbrev=False, add_help=False)
    g = parser.add_mutually_exclusive_group()
    g.add_argument('-n', '--new', nargs='+', action='append')
    g.add_argument('-n-0', '--new-zero', nargs='+', action='append')
    g.add_argument('-n-1', '--new-one', nargs='+', action='append')
    g.add_argument('-j', '--join', nargs='+', action='append')
    g.add_argument('-s', '--state', nargs='+', action='append')
    g.add_argument('-c', '--circuit', nargs='+', action='append')
    g.add_argument('-p', '--probs', nargs='+', action='append')
    g.add_argument('-a', '--apply', nargs='+', action='append')
    g.add_argument('-m', '--measure', nargs=2, action='append')
    g.add_argument('-r', '--rename', nargs=2, action='append')
    g.add_argument('-t', '--timer', nargs=1, action='append')
    g.add_argument('-l', '--list', action='store_true')
    g.add_argument('-q', '--quit', action='store_true')
    g.add_argument('-h', '--help', action='store_true')

    states_dict = {}
    command_quit = False
    disp_time = False
    while not command_quit:
        try:
            start = time.time()
            # Take user input and separate statements by splitting on pipes
            statements = input('#~: ').split('|')
            successful_executes = 0
            for statement in statements:
                # Parse the current statement and return a command that can be acted on
                command = get_command(parser, statement)
                if command.new:
                    num_qubits_tag = 'num-qubits='
                    preset_state_tag = 'preset-state='
                    if len(command.new) != 1:
                        raise ArgumentParserError(error_message['too many commands'])
                    else:
                        command_args = command.new[0]
                        new_states = []
                        num_qubits = 1
                        preset_state = None
                        for s in command_args:
                            if s.startswith(num_qubits_tag):
                                num_qubits = int(s[len(num_qubits_tag):])                           
                            elif s.startswith(preset_state_tag):
                                preset_state = str(s[len(preset_state_tag):])
                            elif '[' in s or ']' in s:
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
                        if gate_name in gates.one_arg_gates:
                            gate_func = gates.one_arg_gates.get(gate_name)
                            qubits = []
                            for q in qubit_refs:
                                current_qubits = []
                                try:
                                    q = json.loads(q)
                                    if isinstance(q, list):
                                        [current_qubits.append(int(x)) for x in q] 
                                    elif isinstance(q, int):
                                        current_qubits.append(q)
                                    else:
                                        ArgumentParserError(f"{error_message['incorrect type for q']}: {q}")
                                except (json.decoder.JSONDecodeError, TypeError, ValueError):
                                    # TypeError example: [1,[2]]
                                    # ValueError example: [1, "hello"]
                                    raise ArgumentParserError(f"{error_message['invalid qubit ref']}: {q}")
                                for curr_q in current_qubits:
                                    if (0 <= curr_q <= s.num_qubits):
                                        qubits.append(curr_q)
                                    else:
                                        raise ArgumentParserError(f"qubit reference out of bounds: {curr_q}")
                            for q in qubits:
                                gate_func(s, q)
                        elif gate_name in gates.two_args_gates:
                            gate_func = gates.two_args_gates.get(gate_name)
                            qubit_pairs = []
                            for qubits in qubit_refs:
                                # currently only one pair in here at a time, as nested lists are rejected
                                current_qubits = []
                                try:
                                    qubits = json.loads(qubits)
                                    if isinstance(qubits, list) and len(qubits) == 2:
                                        # if len(qubits) == 2:
                                        qubits = [int(x) for x in qubits]
                                        current_qubits.append(qubits)
                                        # else:
                                        #     raise ArgumentParserError(f"{error_message['incorrect input for gate']} {gate_name}: {qubits}")
                                            # for x in qubits:
                                            #     if isinstance(x, list): 
                                            #         if len(x) == 2:
                                            #             x = [int(y) for y in x]
                                            #             current_qubits.append(x)
                                            #         else:
                                            #             raise ArgumentParserError(f"{error_message['incorrect num of q']}: {qubits}")
                                            #     else:
                                            #         raise ArgumentParserError(f"{error_message['incorrect type for q']}: {qubits}")
                                    else:
                                        raise ArgumentParserError(f"{error_message['incorrect input for gate']} {gate_name}: {qubits}")
                                except (json.decoder.JSONDecodeError, TypeError, ValueError):
                                    raise ArgumentParserError(f"{error_message['invalid qubit ref']}: {qubits}")
                                for curr_qs in current_qubits:
                                    if (0 <= curr_qs[0] <= s.num_qubits) and (0 <= curr_qs[1] <= s.num_qubits):
                                        qubit_pairs.append(curr_qs)
                                    else:
                                        raise ArgumentParserError(f"qubit reference(s) out of bounds: {curr_qs}")
                            for qs in qubit_pairs:
                                gate_func(s, qs[0], qs[1])
                        else: 
                            raise ArgumentParserError(f"{error_message['gate not found']}: {gate_name}")             

                if command.measure:
                    if len(command.measure) != 1:
                        raise ArgumentParserError(error_message['too many commands'])
                    else:
                        command_args = command.measure[0]
                        s = states_dict.get(command_args[0])
                        qubit = int(command_args[1])
                        s.measurement(qubit)

                if command.rename:
                    if len(command.rename) != 1:
                        raise ArgumentParserError(error_message['too many commands'])
                    s = states_dict.get(command.rename[0])
                    states_dict.pop(command.rename[0])
                    states_dict.update({command.rename[1] : s})

                if command.list:
                    print(list(states_dict.keys()))
                
                if command.quit:
                    command_quit = True
                
                if command.timer:
                    decision = command.timer[0].upper()
                    if decision == "ON":
                        disp_time = True 
                    elif decision == "OFF":
                        disp_time = False
                
                if command.help:
                    print(help_message)
                
                successful_executes += 1
            end = time.time()
            if disp_time:
                print("Time taken: " + str(end - start) + " seconds")

        except ArgumentParserError as e:
            print(f"ERROR: {e}")
            print(f"commands successfully executed: {successful_executes}")
      
        # except AttributeError: 
        #     print("State not found.")

        except KeyError: 
            print("State(s) not found.")
        
    quit()


if __name__ == '__main__':
    main()  