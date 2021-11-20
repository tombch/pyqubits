# CmdQuantum 

## Terminal-based quantum computing simulator

### Requirements
For dependencies see `requirements.txt`. Once necessary requirements are installed, run the program by entering `python cmdq.py`.

## Things you can do

### Create a Bell State
```
Welcome to CmdQuantum, a terminal-based quantum computing simulator. 
To see a list of available commands, enter '##' and then press tab twice.
Enter 'help' or '-h' for more information regarding commands.
To quit the program, enter 'quit' or '-q'.

#~: new q .qubits=2 .preset=zero
#~: state q
State vector for q [0]:
 q = (1+0j) |00>
#~: apply H q 1; apply CNOT q [1, 2]
#~: rename q bellstate; circuit bellstate; state bellstate; prob-dist bellstate;
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
Probability distribution for bellstate [2]:
 00	0.5	=========================
 01	0.0	
 10	0.0	
 11	0.5	=========================
#~: 
```

### Quantum Teleportation
```
Welcome to CmdQuantum, a terminal-based quantum computing simulator. 
To see a list of available commands, enter '##' and then press tab twice.
Enter 'help' or '-h' for more information regarding commands.
To quit the program, enter 'quit' or '-q'.

#~: new q; new bellstate .qubits=2 .preset=zero
#~: apply H bellstate 1; apply CNOT bellstate [1, 2]
#~: state q bellstate
State vector for q [0]:
 q = (0.4632710258963568-0.2885929261268142j) |0>
   + (-0.0068189777999385-0.8378827967539757j) |1>
State vector for bellstate [2]:
 bellstate = (0.7071067811865475+0j) |00>
           + (0.7071067811865475+0j) |11>
#~: join q bellstate .name=qb
#~: apply CNOT qb [1, 2]; apply H qb 1
#~: measure qb 1 2
#~: if-then {qb.2.m1 == 1} {apply X qb 3} 
#~: if-then {qb.1.m1 == 1} {apply Z qb 3}
#~: circuit qb; state qb
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
 M=1 |   |   
 |   |   |      [5]
 |   M=1 |   
 |   |   |      [6]
 |   |   X   
 |   |   |      [7]
 |   |   Z   
 |   |   |      [8]
State vector for qb [8]:
 qb = (0.4632710258963568-0.2885929261268142j) |110>
    + (-0.0068189777999385-0.8378827967539757j) |111>
#~: 
```

## How to use

### Executing Commands
This program has various commands that can be used to simulate quantum circuits. These commands can either be entered and executed line-by-line:

```
#~: command1
#~: command2
#~: command3
...
```

or on a single line (separated by semicolons), where upon pressing enter, they are executed from left to right:

```
#~: command4; command5; command6; ...
``` 
If an error occurs while executing a series of commands entered on the same line, the program will fall back to its state before attempting to execute that line.

For example, if `command6` in the above line causes an error, any changes that `command4` and `command5` made to the environment of the program will not be saved.

### Running Scripts
CmdQuantum can execute scripts within the program (using the `execute` command):

```
#~: execute script1 script2 ...
```

or it can independently execute multiple scripts passed as arguments to the program:

```
python -m cmdq script1 script2 ...
```

## Command List
### `-n`, `new`
```
new s1 s2 s3 ... .qubits=NUM_QUBITS .preset=PRESET_STATE
```
Create multiple new quantum states. 

The names `s1`, `s2`, `s3`, etc of the created quantum states can only contain the digits `0-9`, the lowercase letters `a-z` and the uppercase letters `A-Z`.
#### Optional parameters
* `.q`, `.qubits`
    * Specifies the number of qubits in each new state.
    * Not specifying this parameter will mean each new state has only one qubit.
* `.ps`, `.preset`
    * Specifies a preset state.
        * `.preset=zero` - each new state will be of the form `|0...0>`.
        * `.preset=one` - each new state will be of the form `|1...1>`.
    * Not specifying this parameter will mean each new state has a random state vector.


### `-j`, `join`
```
join s1 s2 s3 ... .name=NEW_NAME
```
Join multiple pre-existing quantum states into one quantum state.
#### Optional parameters
* `.name`
    * Specify a custom name for the new joint state.
    * The new name can only contain the digits `0-9`, the lowercase letters `a-z` and the uppercase letters `A-Z`.
    * Not specifying this parameter will mean the name of the joint state is created by joining each of the state names with an `x`. For example, the default name for the above joined states is `s1xs2xs3x...`. 

### `-s`, `state`
```
state s1 s2 s3 ...
```
Print the state vectors for multiple quantum states. 

**WARNING**: with each additional qubit added to a state, the number of basis vectors grows exponentially, so print wisely.

### `-c`, `circuit`
```
circuit s1 s2 s3 ...
```
Print the circuit diagrams for multiple quantum states.

### `-p`, `prob-dist`
```
prob-dist s1 s2 s3 ...
```
Print probability distributions for the measurement outcomes of multiple quantum states.

### `-a`, `apply`
```
apply g s q1 q2 q3 ...
apply g s [q1, q2] [q3, q4] ...
```
Apply quantum logic gate `g` to specified qubit(s) in the state `s`. 


Each qubit `q1, q2, ...` is specified by an integer that denotes their position in their states' circuit. 
Printing the circuit diagram for the state can help keep track of which qubits have been manipulated.

#### Single qubit gates
Qubit arguments must be passed in the form `q1 q2 ...`, which corresponds to the gate being applied to `q1`, then `q2` and so on.

#### Two qubit gates
Qubit arguments must be passed in the form `[q1, q2] [q3, q4] ...`, which corresponds to the gate being applied to `q1` and `q2`, then `q3` and `q4`, and so on.

### `-m`, `measure`
```
measure s q1 q2 q3 ...
```
Measure multiple qubits in a quantum state.

Each measurement is stored with an associated name. For example, the 6th measurement of the 4th qubit in state `s` is saved with the name `s.4.m6`.

### `-r`, `rename`
```
rename current_name new_name
```
Rename a quantum state. 

If a pre-existing state already has the name `new_name`, that state will be overwritten.

### `-t`, `timer`
```
--timer show/hide
```
Show/hide the timer by specifying with either `show` or `hide`.

### `-l`, `list`
List all currently existing quantum states and measurements in the program.

### `-q`, `quit`
Quit the program.

### `-h`, `help`
Print a help message that outlines each command.

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