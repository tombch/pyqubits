# Command-line quantum computing simulator
## Introduction \& Requirements
A python program for quantum computing simulations.

For dependencies see `requirements.txt`. Once necessary requirements are installed, enter `python main.py` to run the program.


## Things you can do

### Create a Bell State
```
Welcome to my terminal-based quantum computing simulator.
Enter --help or -h for more information. To quit the program, enter --quit or -q.

#~: --new q num_qubits=2 state=zero
#~: --state q
State vector for q [0]:
q = (1+0j) |00>
#~: --apply H q 1 | --apply CNOT q [1, 2]
#~: --rename q bellstate
#~: --circuit bellstate | --state bellstate | --probs bellstate
Circuit diagram for bellstate:
 1   2
 |   |      [0]
 H   |
 |   |      [1]
 O---X
 |   |      [2]
State vector for bellstate [2]:
bellstate = (0.7071067811865475+0j) |00>
          + (0.7071067811865475+0j) |11>
Probabilities for bellstate [2]:
 00     0.5     =========================
 01     0.0
 10     0.0
 11     0.5     =========================
#~:
```

### Quantum Teleportation
```
Welcome to my terminal-based quantum computing simulator.
Enter --help or -h for more information. To quit the program, enter --quit or -q.

#~: --timer on | --new q | --new bellstate num_qubits=2 state=zero | --apply H bellstate 1 | --apply CNOT bellstate [1,2] | --state q bellstate | --join q bellstate name=qb | --apply CNOT qb [1,2] | --apply H qb 1 | --measure qb 1 2 make_vars | --if-then {qb.2 == 1} {--apply X qb 3} | --if-then {qb.1 == 1} {--apply Z qb 3} | --circuit qb | --state qb
State vector for q [0]:
q = (-0.4774612308992416+0.2899719001617376j) |0>
  + (0.5693502316014901-0.6031478955282047j) |1>
State vector for bellstate [2]:
bellstate = (0.7071067811865475+0j) |00>
          + (0.7071067811865475+0j) |11>
Circuit diagram for qb:
 1   2   3
 |   |   |      [0]
 |   H   |
 |   |   |      [1]
 |   O---X
 |   |   |      [2]
 O---X   |
 |   |   |      [3]
 H   |   |
 |   |   |      [4]
 M===|===|===0
 |   |   |      [5]
 |   M===|===1
 |   |   |      [6]
 |   |   X
 |   |   |      [7]
State vector for qb [7]:
qb = (-0.4774612308992416+0.2899719001617375j) |010>
   + (0.56935023160149-0.6031478955282046j) |011>
Time taken: 0.030252456665039062 seconds
```

## How to use

### Executing Commands
This program has various commands that can be used to simulate quantum circuits. These commands can either be entered and executed line-by-line:
```
#~: command_1
#~: command_2
#~: command_3
...
```

 or on a single line, where upon pressing enter, they are executed from left to right (via the use of pipes):
```
#~: command1 | command2 | command3 | ...
``` 
The pipes are necessary for executing multiple commands on a single line. For details on the available commands, see further below.

### Conditions
Work in progress.

## Command List
### `-n`, `--new`
```
--new s1 s2 s3 ... num_qubits=N state=PRESET_STATE
```
Create multiple new random quantum states, each containing `N` qubits. 
The names `s1`, `s2`, `s3`, etc of the created quantum states can only contain the numbers 0-9, the lowercase letters a-z and the uppercase letters A-Z.
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

**WARNING**: with each additional qubit added to a state, the number of basis vectors grows exponentially, so print wisely.

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

### `-i-t`, `--if-then`
```
--if-then {condition} {command1 | command2 | ... }
```
If `condition` is true, then execute the commands within the second `{ }`. 

These commands can consequently be nested:
```
--if-then {condition1} {command1 | --if-then {condition2} {command2 | command3 | ... }}
```

### `-i-t-e`, `--if-then-else`
```
--if-then {condition} {command1 | command2 ... } {command3 | ... }
```
If `condition` is true, then execute the commands within the second `{ }`; otherwise, execute the commands within the third `{ }`. 

These commands can consequently be nested:
```
--if-then-else {condition1} {command1 | command2 | ... } {--if-then-else {condition2} {command3 | command4 | ... } {command5 | command6 | ... }}
```

### `-f-e`, `--for-each`
```
--for-each i iter_args {command1 | command2 | ... }
```
Work in progress. `iter_args` is a user supplied tuple that is passed to `range`, resulting in the iterable `range(*iter_args)` (needs rewording).

### `-e`, `--execute`
```
--execute filename
```
Execute the commands within `filename.clqc`, if it exists. The `.clqc` extension is therefore necessary on any files that are to be executed.

For example, the following is a sequence of commands within a file named `script.clqc`:
```
--new q state=zero num_qubits=4;
--state q;
--apply H q 1;
--apply CNOT q [1,2];
--measure q 1 make_vars;
--state q;
--if-then-else { q.1 == 0 }  
{
    --apply X q 1;
    --apply Y q 1;
    --apply Z q 1;
}
{
    --measure q 2 make_vars;
    --if-then-else { q.2 == 0 }
    {
        --apply H q 3;
    }
    {
        --apply H q 4;
    };
    --apply Z q 2;
    --apply Y q 2;
    --apply X q 2;
};
--circuit q;
```
Commands within a script such as this can use either `;` or `|` to separate commands. The script can then be executed within the program:
```
Welcome to my terminal-based quantum computing simulator.
Enter --help or -h for more information. To quit the program, enter --quit or -q.

#~: --execute script
State vector for q [0]:
q = (1+0j) |0000>
State vector for q [3]:
q = (1+0j) |1100>
Circuit diagram for q:
 1   2   3   4
 |   |   |   |      [0]
 H   |   |   |
 |   |   |   |      [1]
 O---X   |   |
 |   |   |   |      [2]
 M===|===|===|===1
 |   |   |   |      [3]
 |   M===|===|===1
 |   |   |   |      [4]
 |   |   |   H
 |   |   |   |      [5]
 |   Z   |   |
 |   |   |   |      [6]
 |   Y   |   |
 |   |   |   |      [7]
 |   X   |   |
 |   |   |   |      [8]
#~:
```