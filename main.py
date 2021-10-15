import time
import numpy as np
import argparse
import functools
import json
import gates
from quantum_state import QuantumState

help_message = """---BEGIN HELP---
COMMAND LIST:
-n, --new
--new s1 s2 s3 ... num-qubits=N
Create multiple new random quantum states, each containing N qubits. 
num-qubits is an optional parameter (default for this parameter is 1). 

-n-0, --new-zero
--new-zero s1 s2 s3 ... num-qubits=N
Create multiple new quantum states, each of the form |0...0>, each containing N qubits.
num-qubits is an optional parameter (default for this parameter is 1).

-n-1, --new-one
--new-one s1 s2 s3 ... num-qubits=N
Create multiple new quantum states, each of the form |1...1>, each containing N qubits.
num-qubits is an optional parameter (default for this parameter is 1).

-j, --join
--join s1 s2 s3 ... name=new_name
Join multiple pre-existing quantum states into one quantum state.
new_name is an optional parameter (default for this parameter is s1xs2xs3x...). 

-s, --state
--state s1 s2 s3 ...
Print the state vectors for multiple quantum states. 
WARNING: with each additional qubit in a state, the number of basis vectors (printed stuff) grows exponentially.

-c, --circuit
--circuit s1 s2 s3 ...
Print the circuit diagrams for multiple quantum states.

-a, --apply
--apply g s {qubit OR [qubit] OR [control, target]}
Apply quantum logic gate g to specified qubit(s) in the state s. 
Each qubit is specified by an integer; printing the circuit diagram for the state can help keep track of which qubit(s) you want to manipulate.
Depending on the gate, one OR two qubits will need specifying. How to format this is displayed above. 
NOTE: the {} are NOT part of the command and are only shown above to indicate the different formatting options for the third parameter.

-m, --measure
--measure s q
Measure qubit q in the quantum state s.

-r, --rename
--rename current_name new_name
Rename a quantum state.

-t, --timer
--timer {on OR off}
Toggle the timer on or off.
NOTE: the {} are NOT part of the command and are only shown above to indicate the different enterable options for the only parameter.

-l, --list
List all currently existing quantum states in the program.

-q, --quit
Quit the program.

CHAINING COMMANDS:
Commands can be chained together in a single line:
command_1 | command_2 | command_3 | command_4 ...
Due to the separating pipes, these statements will be executed from left to right. 
Failure to use pipes means NO guarantee of the order that statements are executed (not a good idea).
---END HELP---"""

class ArgumentParserError(Exception): 
    pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

def get_all_args(parser):
    user_input = input('#~: ')
    user_input = user_input.split('|')
    all_args = []
    for statement in user_input:
        input_list = statement.split()
        commands = []
        i = 0
        while i < len(input_list):
            if '[' in input_list[i]:
                new_list_string = input_list[i]
                for  j in range(i+1, len(input_list)):
                    new_list_string += input_list[j]
                    if ']' in input_list[j]:
                        i = j+1
                        break
                commands.append(new_list_string)
            else:
                commands.append(input_list[i])
            i += 1
        args = parser.parse_args(commands)
        all_args.append(args)
    return all_args

def main():
    print("Welcome to my terminal-based quantum computing simulator. \nEnter --help or -h for more information. To quit the program, enter --quit or -q.")
    parser = ThrowingArgumentParser(allow_abbrev=False, add_help=False)

    parser.add_argument('-n', '--new', nargs='+', action='append')
    parser.add_argument('-n-0', '--new-zero', nargs='+', action='append')
    parser.add_argument('-n-1', '--new-one', nargs='+', action='append')
    parser.add_argument('-j', '--join', nargs='+', action='append')
    parser.add_argument('-s', '--state', nargs='+', action='append')
    parser.add_argument('-c', '--circuit', nargs='+', action='append')
#     parser.add_argument('-p', '--probabilities', nargs='+', action='append')
    parser.add_argument('-a', '--apply', nargs=3)
    parser.add_argument('-m', '--measure', nargs=2)
    parser.add_argument('-r', '--rename', nargs=2)
    parser.add_argument('-t', '--timer', nargs=1)
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-q', '--quit', action='store_true')
    parser.add_argument('-h', '--help', action='store_true')

    states_dict = {}
    num_qubits_tag = 'num-qubits='
    name_tag = 'name='
    args_quit = False
    disp_time = False
    while not args_quit:
        try: 
            all_args = get_all_args(parser)
            start = time.time()
            for args in all_args:
                if args.new:
                    for new_states in args.new:
                        num_qubits = 1
                        if new_states[len(new_states)-1].startswith(num_qubits_tag):
                            num_qubits = int(new_states[len(new_states)-1][len(num_qubits_tag):])
                            new_states = new_states[:len(new_states)-1]
                        for x in new_states:
                            states_dict[x] = QuantumState(num_qubits=num_qubits, state_name=x)                

                if args.new_zero:
                    for new_states in args.new_zero:
                        num_qubits = 1
                        if new_states[len(new_states)-1].startswith(num_qubits_tag):
                            num_qubits = int(new_states[len(new_states)-1][len(num_qubits_tag):])
                            new_states = new_states[:len(new_states)-1]
                        for x in new_states:
                            states_dict[x] = QuantumState(num_qubits=num_qubits, state_name=x, preset_state='zero_state')  

                if args.new_one:
                    for new_states in args.new_one:
                        num_qubits = 1
                        if new_states[len(new_states)-1].startswith(num_qubits_tag):
                            num_qubits = int(new_states[len(new_states)-1][len(num_qubits_tag):])
                            new_states = new_states[:len(new_states)-1]
                        for x in new_states:
                            states_dict[x] = QuantumState(num_qubits=num_qubits, state_name=x, preset_state='one_state')    

                if args.join:                    
                    for state_names in args.join:
                        joint_state_name = ""
                        if state_names[len(state_names)-1].startswith(name_tag):
                            joint_state_name = state_names[len(state_names)-1][len(name_tag):]
                            state_names = state_names[:len(state_names)-1]
                        states_being_joined = []
                        for x in state_names:
                            states_being_joined.append(states_dict.get(x))
                            states_dict.pop(x) 
                        joint_state = functools.reduce(QuantumState.__mul__, states_being_joined)
                        if joint_state_name:
                            joint_state.state_name = joint_state_name
                        states_dict[joint_state.state_name] = joint_state

                if args.state:
                    args.state = [x for x_list in args.state for x in x_list]
                    for x in args.state:
                        states_dict.get(x).print_state()

                if args.circuit:
                    args.circuit = [x for x_list in args.circuit for x in x_list]
                    for x in args.circuit:
                        states_dict.get(x).print_circuit()
                
                if args.apply:
                    gate_name = args.apply[0]
                    s = states_dict.get(args.apply[1])
                    qubit_names = json.loads(args.apply[2])

                    if gate_name in gates.one_arg_gates:
                        gate_func = gates.one_arg_gates.get(gate_name)

                        if isinstance(qubit_names, list) and len(qubit_names) == 1:
                            qubit = int(qubit_names[0])
                            gate_func(s, qubit) 

                        elif isinstance(qubit_names, int):
                            qubit = qubit_names
                            gate_func(s, qubit) 

                    elif gate_name in gates.two_args_gates:
                        gate_func = gates.two_args_gates.get(gate_name)
                        
                        if isinstance(qubit_names, list) and len(qubit_names) == 2:
                            qubits = [int(x) for x in qubit_names]
                            gate_func(s, qubits[0], qubits[1])
                    else: 
                        print("Gate not found.")                

                if args.measure:
                    s = states_dict.get(args.measure[0])
                    qubit = int(args.measure[1])
                    s.measurement(qubit)

                if args.rename: 
                    s = states_dict.get(args.rename[0])
                    states_dict.pop(args.rename[0])
                    states_dict.update({args.rename[1] : s})

                if args.list:
                    print(list(states_dict.keys()))
                
                if args.quit:
                    args_quit = True
                
                if args.timer:
                    decision = args.timer[0].upper()
                    if decision == "ON":
                        disp_time = True 
                    elif decision == "OFF":
                        disp_time = False
                
                if args.help:
                    print(help_message)

            end = time.time()
            if disp_time:
                print("Time taken: " + str(end - start) + " seconds")
        except ArgumentParserError:
            print("Invalid command.")
        
        except AttributeError: 
            print("State not found.")

        except KeyError: 
            print("State(s) not found.")
        
    quit()


if __name__ == '__main__':
    main()
# if args.new_zero:
#     for new_states in args.new_zero:
#         try: 
#             num_qubits = int(new_states[len(new_states)-1])
#         except ValueError:
#             num_qubits = 1
#         for x in new_states:
#             states_dict[x] = QuantumState(num_qubits=num_qubits, state_name=x, preset_state='zero_state')    