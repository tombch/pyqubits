# `pyqubits`

A Python module for quantum computing simulations.

## Setup

#### Install via pip

```
$ pip install pyqubits
```

#### Build from source

```
$ git clone https://github.com/tombch/pyqubits.git
$ cd pyqubits/
$ conda env create -f environment.yml
$ conda activate pyqubits
$ pip install .
```

## Usage

#### Create a `QuantumState`
```python
>>> import pyqubits as pq
>>> s = pq.QuantumState(n=3)
>>> t = pq.QuantumState.from_bits("00")
```

#### View a `QuantumState`
```python
>>> s
<pyqubits.quantumstate.QuantumState object at 0x12c8dbe20>
>>> s.vector
array([ 0.26473143+0.04154587j, -0.20067671-0.10755921j,
       -0.39930689+0.10786539j, -0.37699089-0.13327015j,
        0.21134793+0.32994554j, -0.34491258-0.19617726j,
       -0.20214726+0.38443046j,  0.04941406-0.20811735j])
>>> pq.print_state(s)
= (  0.2647314279595292 + 0.041545871067086244j) |000> + ( - 0.2006767092839878 - 0.10755920658685589j) |001> 
+ ( - 0.3993068862359329 + 0.10786539262494077j) |010> + ( - 0.37699089004328423 - 0.1332701464731362j) |011> 
+ (    0.2113479347541418 + 0.3299455366498416j) |100> + (    - 0.3449125843925513 - 0.19617726288093j) |101> 
+ (- 0.20214725738039502 + 0.38443046252328394j) |110> + (    0.0494140555349596 - 0.2081173528288418j) |111> 
>>> pq.print_circuit(s)
1---
    
2---
    
3---
>>> pq.print_dist(s)
000     0.07    |=======
001     0.05    |=====
010     0.17    |=================
011     0.16    |================
100     0.15    |===============
101     0.16    |================
110     0.19    |===================
111     0.05    |=====
>>> t
<pyqubits.quantumstate.QuantumState object at 0x12c8dbce0>
>>> t.vector
array([1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j])
>>> pq.print_state(t)
= (1 + 0j) |00> 
>>> pq.print_circuit(t)
1---
    
2---
>>> pq.print_dist(t)
00      1.0     |====================================================================================================
01      0.0     |
10      0.0     |
11      0.0     |
```

#### Manipulate a `QuantumState`
```python
>>> t.H(qubit=1)
<pyqubits.quantumstate.QuantumState object at 0x12c8db420>
>>> pq.print_state(t)
= (0.7071067811865475 + 0j) |00> + (0.7071067811865475 + 0j) |10> 
>>> t.CNOT(control=1, target=2)
<pyqubits.quantumstate.QuantumState object at 0x12c8db420>
>>> pq.print_state(t)
= (0.7071067811865475 + 0j) |00> + (0.7071067811865475 + 0j) |11> 
>>> pq.print_circuit(t)
1---H---O---
        |   
2-------X---
>>> pq.print_dist(t)
00      0.5     |==================================================
01      0.0     |
10      0.0     |
11      0.5     |==================================================
>>> t.measure(qubit=1)
<pyqubits.quantumstate.QuantumState object at 0x12c8db420>
>>> result = t.bit
>>> result
0
>>> pq.print_state(t)
= (1 + 0j) |00> 
>>> pq.print_circuit(t)
1---H---O---0---
        |       
2-------X-------
>>> pq.print_dist(t)
00      1.0     |====================================================================================================
01      0.0     |
10      0.0     |
11      0.0     |
```