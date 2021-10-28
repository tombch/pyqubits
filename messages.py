help_message = """---BEGIN HELP---
COMMAND LIST:
-n, --new
--new s1 s2 s3 ... num_qubits=N preset_state=PRESET_STATE
Create multiple new random quantum states, each containing N qubits. 
nq, num_qubits - an optional parameter (default for this parameter is 1).
ps, preset_state - an optional parameter (not specifying this parameter means a random qubit state will be created).
More on preset_state choices: 
state0 - used to create multiple new quantum states of the form |0...0>, with number of qubits determined by num_qubits.
state1 - used to create multiple new quantum states of the form |1...1>, with number of qubits determined by num_qubits.

-j, --join
--join s1 s2 s3 ... name=NEW_NAME
Join multiple pre-existing quantum states into one quantum state.
name - an optional parameter (default for this parameter is s1xs2xs3x...). 

-s, --state
--state s1 s2 s3 ...
Print the state vectors for multiple quantum states. 
WARNING: with each additional qubit in a state, the number of basis vectors (printed stuff) grows exponentially.

-c, --circuit
--circuit s1 s2 s3 ...
Print the circuit diagrams for multiple quantum states.

-p, --probs
--probs s1 s2 s3 ...
Print histograms displaying measurement probabilities for multiple quantum states.

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
With the use of pipes, multiple commands can be executed in a single line:
command_1 | command_2 | command_3 | command_4 ...
Due to the separating pipes, these statements will be executed from left to right. 
The pipes are necessary for executing multiple commands on a single line.
---END HELP---"""

error_message = {
    "invalid new name" : "invalid new name",
    "too many commands" : "argument cannot be used twice in one command (should be separated by ';')",
    "state not found" : "state not found",
    "gate not found" : "gate not found",
    "invalid qubit ref" : "invalid reference of qubit(s)",
    "incorrect input for gate" : "incorrect input for gate",
    "no qubit ref" : "no qubit reference(s) given"
}