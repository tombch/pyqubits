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
    "too many commands" : "more than one command (should be separated by pipes)",
    "state not found" : "state not found",
    "gate not found" : "gate not found",
    "invalid qubit ref" : "invalid reference of qubit(s)",
    "incorrect type for q" : "incorrect type for qubit ref",
    "incorrect input for gate" : "incorrect input for gate"
}