from random import random
import numpy as np
import linear_algebra as la

def X(s, qubit):
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

def H(s, qubit):
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

def CNOT(s, control, target):
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