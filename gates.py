from random import random
import numpy as np
import linear_algebra as la
from quantum_state import QuantumState

#NEW
def single_qubit_gate(s, qubit, chosen_matrix):
    I_matrix = np.array([[1+0j, 0+0j],
                         [0+0j, 1+0j]])
    if (qubit == 1):
        gate_matrix = chosen_matrix
    else:
        gate_matrix = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == qubit):
            gate_matrix = np.kron(gate_matrix, chosen_matrix)
        else:
            gate_matrix = np.kron(gate_matrix, I_matrix)
    s.state_vector = np.matmul(gate_matrix, s.state_vector)

def X(s, qubit):
    X_matrix = np.array([[0+0j, 1+0j],
                         [1+0j, 0+0j]])
    single_qubit_gate(s, qubit, X_matrix)

def Y(s, qubit):
    Y_matrix = np.array([[0+0j, 0-1j],
                         [0+1j, 0+0j]])
    single_qubit_gate(s, qubit, Y_matrix)

def Z(s, qubit):
    Z_matrix = np.array([[1+0j, 0+0j],
                         [0+0j, -1+0j]])
    single_qubit_gate(s, qubit, Z_matrix)

def H(s, qubit):
    H_matrix = np.array([[1+0j, 1+0j],
                         [1+0j, -1+0j]])/np.sqrt(2)
    single_qubit_gate(s, qubit, H_matrix)

def P(s, qubit):
    P_matrix = np.array([[1+0j, 0+0j],
                         [0+0j, 0+1j]])
    single_qubit_gate(s, qubit, P_matrix)

def T(s, qubit):
    T_matrix = np.array([[1+0j, 0+0j],
                         [0+0j, (sqrt(2)/2)+(sqrt(2)/2)*1j]])

def CNOT(s, control, target):
    I_matrix = np.array([[1+0j, 0+0j],
                         [0+0j, 1+0j]])    
    X_matrix = np.array([[0+0j, 1+0j],
                         [1+0j, 0+0j]])
    zero_matrix = np.array([[1+0j, 0+0j],
                            [0+0j, 0+0j]])
    one_matrix = np.array([[0+0j, 0+0j],
                           [0+0j, 1+0j]])
    if (control == 1):
        gate_matrix_a = zero_matrix
        gate_matrix_b = one_matrix
    elif (target == 1):
        gate_matrix_a = I_matrix
        gate_matrix_b = X_matrix
    else:
        gate_matrix_a = I_matrix
        gate_matrix_b = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == control):
            gate_matrix_a = np.kron(gate_matrix_a, zero_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, one_matrix)
        elif (i == target):
            gate_matrix_a = np.kron(gate_matrix_a, I_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, X_matrix)         
        else:
            gate_matrix_a = np.kron(gate_matrix_a, I_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, I_matrix)
    gate_matrix = np.add(gate_matrix_a, gate_matrix_b)
    s.state_vector = np.matmul(gate_matrix, s.state_vector)

def join_states(s1, s2, state_name=None):
    joint_state_vector = np.kron(s1.state_vector, s2.state_vector)
    s3_num_qubits = s1.num_qubits + s2.num_qubits
    s3 = QuantumState(num_qubits=s3_num_qubits, preset_state_vector=joint_state_vector, state_name=state_name)
    return s3


#OLD
def X_old(s, qubit):
    I_matrix = np.array([[[1,0], [0,0]], 
                         [[0,0], [1,0]]])
    X_matrix = np.array([[[0,0], [1,0]], 
                         [[1,0], [0,0]]])
    if (qubit == 1):
        gate_matrix = X_matrix
    else:
        gate_matrix = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == qubit):
            gate_matrix = la.kronecker_product(gate_matrix, X_matrix)
        else:
            gate_matrix = la.kronecker_product(gate_matrix, I_matrix)
    s.state_vector = la.complex_matmul(gate_matrix, s.state_vector)

def H_old(s, qubit):
    I_matrix = np.array([[[1,0], [0,0]], 
                         [[0,0], [1,0]]])
    H_matrix = np.array([[[1,0], [1,0]], 
                         [[1,0], [-1,0]]])/np.sqrt(2)
    if (qubit == 1):
        gate_matrix = H_matrix
    else:
        gate_matrix = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == qubit):
            gate_matrix = la.kronecker_product(gate_matrix, H_matrix)
        else:
            gate_matrix = la.kronecker_product(gate_matrix, I_matrix)
    s.state_vector = la.complex_matmul(gate_matrix, s.state_vector)

def CNOT_old(s, control, target):
    I_matrix = np.array([[[1,0], [0,0]], [[0,0], [1,0]]])
    X_matrix = np.array([[[0,0], [1,0]], [[1,0], [0,0]]])
    zero_matrix = np.array([[[1,0], [0,0]], [[0,0], [0,0]]]) 
    one_matrix = np.array([[[0,0], [0,0]], [[0,0], [1,0]]])
    if (control == 1):
        gate_matrix_a = zero_matrix
        gate_matrix_b = one_matrix
    elif (target == 1):
        gate_matrix_a = I_matrix
        gate_matrix_b = X_matrix
    else:
        gate_matrix_a = I_matrix
        gate_matrix_b = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == control):
            gate_matrix_a = la.kronecker_product(gate_matrix_a, zero_matrix)
            gate_matrix_b = la.kronecker_product(gate_matrix_b, one_matrix)
        elif (i == target):
            gate_matrix_a = la.kronecker_product(gate_matrix_a, I_matrix)
            gate_matrix_b = la.kronecker_product(gate_matrix_b, X_matrix)         
        else:
            gate_matrix_a = la.kronecker_product(gate_matrix_a, I_matrix)
            gate_matrix_b = la.kronecker_product(gate_matrix_b, I_matrix)
    gate_matrix = np.add(gate_matrix_a, gate_matrix_b)
    s.state_vector = la.complex_matmul(gate_matrix, s.state_vector)