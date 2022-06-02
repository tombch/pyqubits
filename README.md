# `pyqubits`

A Python module for quantum computing simulations.

### Setup
```
$ git clone https://github.com/tombch/pyqubits.git
$ cd pyqubits/
$ conda env create -f environment.yml
$ conda activate pyqubits
$ pip install .
```

### Usage

#### Creating a `QuantumState`
```python
>>> from pyqubits import QuantumState
>>> s = QuantumState(3)
>>> t = QuantumState.from_bits('00')
```

#### Viewing a `QuantumState`
```python
>>> s
QuantumState([-0.29615118+0.50152956j,  0.37355584-0.06041027j,
               0.40094705-0.13785654j, -0.17540328-0.25628919j,
              -0.26399075+0.28541768j,  0.11632225-0.12028472j,
               0.08627474-0.14452522j,  0.04189382+0.17920989j])
>>> s.vector
array([-0.29615118+0.50152956j,  0.37355584-0.06041027j,
        0.40094705-0.13785654j, -0.17540328-0.25628919j,
       -0.26399075+0.28541768j,  0.11632225-0.12028472j,
        0.08627474-0.14452522j,  0.04189382+0.17920989j])
>>> print(s)
= (- 0.29615 + 0.50153j) |000> + (  0.37356 - 0.06041j) |001> 
+ (  0.40095 - 0.13786j) |010> + ( - 0.1754 - 0.25629j) |011> 
+ (- 0.26399 + 0.28542j) |100> + (  0.11632 - 0.12028j) |101> 
+ (  0.08627 - 0.14453j) |110> + (  0.04189 + 0.17921j) |111> 
>>> print(s.circuit)
1---
    
2---
    
3---
>>> print(s.dist)
000     0.34    |=================
001     0.14    |=======
010     0.18    |=========
011     0.1     |=====
100     0.15    |========
101     0.03    |=
110     0.03    |=
111     0.03    |==
>>> t
QuantumState([1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j])
>>> t.vector
array([1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j])
>>> print(t)
= (1 + 0j) |00> 
>>> print(t.circuit)
1---
    
2---
>>> print(t.dist)
00      1.0     |==================================================
01      0.0     |
10      0.0     |
11      0.0     |
```

#### Manipulating a `QuantumState`
```python
>>> t.H(1)
QuantumState([0.70710678+0.j, 0.        +0.j, 0.70710678+0.j, 0.        +0.j])
>>> t.CNOT(1, 2)
QuantumState([0.70710678+0.j, 0.        +0.j, 0.        +0.j, 0.70710678+0.j])
>>> print(t)
= (0.70711 + 0j) |00> + (0.70711 + 0j) |11> 
>>> print(t.circuit)
1---H---O---
        |   
2-------X---
>>> print(t.dist)
00      0.5     |=========================
01      0.0     |
10      0.0     |
11      0.5     |=========================
>>> t.measure(1)
QuantumState([1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j])
>>> result = t.bit
>>> result
0
>>> print(t)
= (1 + 0j) |00>
```