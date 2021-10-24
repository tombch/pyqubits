# Command-line quantum computing simulator
## Introduction
A python program for quantum computing simulations.

### Example: Quantum Teleportation

![example](/images/example.PNG)

## Requirements
See `requirements.txt`.

## Executing Commands
This program has various commands that can be used to simulate quantum circuits. These commands can be entered either line-by-line:
```
#~: command_1
#~: command_2
#~: command_3
...
```

 or on a single line (where they are executed from left to right), via the use of pipes:
```
#~: command1 | command2 | command3 | ...
``` 
The pipes are necessary for executing multiple commands on a single line.

## Command List
### `-n`, `--new`
```
--new s1 s2 s3 ... num_qubits=N state=PRESET_STATE
```
Create multiple new random quantum states, each containing `N` qubits. 
* `nq`, `num_qubits` - an optional parameter (default for this parameter is `1`).
* `s`, `state` - an optional parameter for specifying a preset state (not specifying this parameter means a random state will be created).
    * `state=zero` - used to create multiple new quantum states of the form `|0...0>`, with number of qubits determined by `num_qubits`.
    * `state=one` - used to create multiple new quantum states of the form `|1...1>`, with number of qubits determined by `num_qubits`.

### `-j`, `--join`
```
--join s1 s2 s3 ... name=NEW_NAME
```
Join multiple pre-existing quantum states into one quantum state.
* `name` - an optional parameter (default for this parameter is `s1xs2xs3x`...). 

### `-s`, `--state`
```
--state s1 s2 s3 ...
```
Print the state vectors for multiple quantum states. 

**WARNING**: with each additional qubit in a state, the number of basis vectors grows exponentially, so print carefully.

### `-c`, `--circuit`
```
--circuit s1 s2 s3 ...
```
Print the circuit diagrams for multiple quantum states.

### `-p`, `--probs`
```
--probs s1 s2 s3 ...
```
Print histograms displaying measurement probabilities for multiple quantum states.

### `-a`, `--apply`
```
--apply g s qubit1 qubit2 qubit3 ...
--apply g s [qubit1, qubit2, ...] [qubit1, qubit2, ...] ...
```
Apply quantum logic gate `g` to specified qubit(s) in the state `s`. 
Each qubit is specified by an integer; printing the circuit diagram for the state can help keep track of which qubit(s) you want to manipulate.

A gate may act on one or more qubits:
* If a gate acts on only one qubit, then the qubit argument is an integer. Passing multiple integers in the form `qubit1 qubit2 ...` corresponds to the gate being applied to `qubit1` and then `qubit2` and so on.
* If a gate acts on at least two qubits, then qubit arguments must be passed in an array of integers. Multiple arrays being passed means multiple applications of the gate to (potentially) different sets of qubits.

### `-m`, `--measure`
```
--measure s q1 q2 q3 ... make_vars
```
Measure multiple qubits in the quantum state s.
* `mv`, `make_vars` - an optional setting that when included in the command, saves the measurements into variables with the naming convention `s.q1`, `s.q2`, `s.q3`, etc. These variables store the latest measurement for their qubit, and additional measurements on said qubit will cause the previous measurement to be overwritten.

### `-r`, `--rename`
```
--rename current_name new_name
```
Rename a quantum state.

### `-t`, `--timer`
```
--timer on/off
```
Show/hide the timer by specifying as either `on` or `off`.

### `-l`, `--list`
List all currently existing quantum states and variables in the program.

### `-q`, `--quit`
Quit the program.

### `-h`, `--help`
Print the documentation of each command.

### `i-t`, `--if-then`
```
--if-then {condition} {command}
--if-then {condition1} {--if-then {condition2} {...}}
```
If `condition` is true, then execute `command`. These commands can consequently be nested as shown above.