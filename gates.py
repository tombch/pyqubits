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
    zero_operator = np.array([[[1,0], [0,0]], [[0,0], [0,0]]]) 
    one_operator = np.array([[[0,0], [0,0]], [[0,0], [1,0]]])
    if (qubit == 1):
        measurement_matrix = zero_operator
    else:
        measurement_matrix = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == qubit):
            measurement_matrix = la.kronecker_product(measurement_matrix, zero_operator)
        else:
            measurement_matrix = la.kronecker_product(measurement_matrix, I_matrix)
    s.state_vector = la.complex_matmul(measurement_matrix, s.state_vector)/la.normaliser(s.state_vector)