import time
import numpy as np
import argparse
import functools
import json
import gates
from quantum_state import QuantumState

def main():
    # start = time.time()
    # end = time.time()
    # print("Time taken: " + str(end - start) + " seconds")
    print("Welcome to the quantum computing simulator.")
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('-n', '--new', nargs='+', action='append')
    parser.add_argument('-n-0', '--new-zero', nargs='+', action='append')
    parser.add_argument('-n-1', '--new-one', nargs='+', action='append')
    parser.add_argument('-j', '--join', nargs='+', action='append')
    parser.add_argument('-s', '--state', nargs='+', action='append')
    parser.add_argument('-c', '--circuit', nargs='+', action='append')
    parser.add_argument('-h', '--histogram', nargs='+', action='append')
    parser.add_argument('-a', '--apply', nargs=3, metavar=('gate', 'state', 'qubits'))
    parser.add_argument('-m', '--measure', nargs=2, metavar=('state', 'qubit'))
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-q', '--quit', action='store_true')

    states_dict = {}
    while True:
        input_list = input('#~: ').split()
        # print(input_list)
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
        # print(commands)
        args = parser.parse_args(commands)

        if args.new:
            args.new = [x for x_list in args.new for x in x_list]
            for x in args.new:
                states_dict[x] = QuantumState(state_name=x)

        if args.new_zero:
            args.new_zero = [x for x_list in args.new_zero for x in x_list]
            for x in args.new_zero:
                states_dict[x] = QuantumState(state_name=x, preset_state="zero_state")
    
        if args.new_one:
            args.new_one = [x for x_list in args.new_one for x in x_list]
            for x in args.new_one:
                states_dict[x] = QuantumState(state_name=x, preset_state="one_state")

        if args.join:                    
            for state_names in args.join:
                states_list = []
                for x in state_names:
                    states_list.append(states_dict.get(x))
                    states_dict.pop(x) 
                joint_state = functools.reduce(QuantumState.__mul__, states_list)
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
            # Barely functional
            g = gates.gates_dict.get(args.apply[0])
            s = states_dict.get(args.apply[1])
            if not ('[' in args.apply[2] or ']' in args.apply[2] or ',' in args.apply[2]): 
                qubit = int(args.apply[2])
                gates.apply_gate(s, qubit, g, args.apply[0])
                states_dict.update({args.apply[1] : s})
            else:
                qubits = json.loads(args.apply[2])
                if len(qubits) == 1:
                    qubit = int(qubits[0])
                    gates.apply_gate(s, qubit, g, args.apply[0])
                    states_dict.update({args.apply[1] : s})     
                elif len(qubits) == 2:
                    qubits = [int(x) for x in qubits]
                    gates.apply_cgate(s, qubits[0], qubits[1], g, args.apply[0])
                    states_dict.update({args.apply[1] : s}) 

        if args.list:
            print(list(states_dict.keys()))

        if args.quit:
            quit()

if __name__ == '__main__':
    main()