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

def CNOT(s, control): #control and target must be adjacent
    I_matrix = np.array([[[1,0], [0,0]], [[0,0], [1,0]]])
    cnot_matrix = np.array([[[1,0], [0,0], [0,0], [0,0]], 
                            [[0,0], [1,0], [0,0], [0,0]], 
                            [[0,0], [0,0], [0,0], [1,0]], 
                            [[0,0], [0,0], [1,0], [0,0]]])
    if (control == 1):
        gate_matrix = cnot_matrix
    else:
        gate_matrix = la.kronecker_product(I_matrix, I_matrix)
    for i in range(3, s.num_qubits+1):
        if (i == control):
            gate_matrix = la.kronecker_product(gate_matrix, cnot_matrix)
            i += 1
        else:
            gate_matrix = la.kronecker_product(gate_matrix, I_matrix)
    s.state_vector = la.complex_matmul(gate_matrix, s.state_vector)  

def measurement(s, qubit):
    I_matrix = np.array([[[1,0], [0,0]], [[0,0], [1,0]]])
    zero_matrix = np.array([[[1,0], [0,0]], [[0,0], [0,0]]]) 
    one_matrix = np.array([[[0,0], [0,0]], [[0,0], [1,0]]])
    if (qubit == 1):
        measurement_matrix_zero = zero_matrix
        measurement_matrix_one = one_matrix
    else:
        measurement_matrix_zero = I_matrix
        measurement_matrix_one = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == qubit):
            measurement_matrix_zero = la.kronecker_product(measurement_matrix_zero, zero_matrix)
            measurement_matrix_one = la.kronecker_product(measurement_matrix_one, one_matrix)
        else:
            measurement_matrix_zero = la.kronecker_product(measurement_matrix_zero, I_matrix)
            measurement_matrix_one = la.kronecker_product(measurement_matrix_one, I_matrix)
    
    collapsed_zero = la.complex_matmul(measurement_matrix_zero, s.state_vector)
    zero_probability = la.complex_matmul(la.conjugate_transpose(measurement_matrix_zero), collapsed_zero)
    zero_probability = la.complex_matmul(la.conjugate_transpose(s.state_vector), zero_probability)[0][0][0]

    collapsed_one = la.complex_matmul(measurement_matrix_one, s.state_vector)
    one_probability = la.complex_matmul(la.conjugate_transpose(measurement_matrix_one), collapsed_one)
    one_probability = la.complex_matmul(la.conjugate_transpose(s.state_vector), one_probability)[0][0][0]

    outcome = random()
    if outcome <= zero_probability:
        s.state_vector = collapsed_zero
    else:
        s.state_vector = collapsed_one
    s.state_vector = s.state_vector/la.normaliser(s.state_vector)
