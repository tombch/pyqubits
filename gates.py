import numpy as np
import complex_number as cn

def kronecker_product(m1, m2):
    (r1, c1, b1) = m1.shape
    (r2, c2, b2) = m2.shape
    m3 = np.zeros((r1*r2, c1*c2, 2))
    for i in range(0, r1*r2, r2):
        for j in range(0, c1*c2, c2):
            m1_row = int(i/r2)
            m1_col = int(j/c2)
            m1m2 = np.zeros((r2, c2, 2))
            for l in range(r2):
                for m in range(c2):           
                    m1m2[l][m] = cn.multiply(m1[m1_row, m1_col], m2[l, m])
            m3[i:i+r2, j:j+c2] = m1m2
    return m3

def complex_matmul(m1, m2):
    (r1, c1, b1) = m1.shape
    (r2, c2, b2) = m2.shape
    m3 = np.zeros((r1, c2, 2))
    for i in range(r1):
        for j in range(c2):
            element_sum = [0,0]
            for k in range(c1):
                element_sum = np.add(element_sum, cn.multiply(m1[i][k], m2[k][j]))
            m3[i][j] = element_sum
    return m3

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
            gate_matrix = kronecker_product(gate_matrix, X_matrix)
        else:
            gate_matrix = kronecker_product(gate_matrix, I_matrix)
    s.state_vector = complex_matmul(gate_matrix, s.state_vector)

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
            gate_matrix = kronecker_product(gate_matrix, H_matrix)
        else:
            gate_matrix = kronecker_product(gate_matrix, I_matrix)
    s.state_vector = complex_matmul(gate_matrix, s.state_vector)

def CNOT(s, target): #target and control must be adjacent
    I_matrix = np.array([[[1,0], [0,0]], [[0,0], [1,0]]])
    cnot_matrix = np.array([[[1,0], [0,0], [0,0], [0,0]], 
                            [[0,0], [1,0], [0,0], [0,0]], 
                            [[0,0], [0,0], [0,0], [1,0]], 
                            [[0,0], [0,0], [1,0], [0,0]]])
    if (target == 1):
        gate_matrix = cnot_matrix
    else:
        gate_matrix = kronecker_product(I_matrix, I_matrix)
    for i in range(3, s.num_qubits+1):
        if (i == target):
            gate_matrix = kronecker_product(gate_matrix, cnot_matrix)
            i += 1
        else:
            gate_matrix = kronecker_product(gate_matrix, I_matrix)
    s.state_vector = complex_matmul(gate_matrix, s.state_vector)  

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
            measurement_matrix = kronecker_product(measurement_matrix, zero_operator)
        else:
            measurement_matrix = kronecker_product(measurement_matrix, I_matrix)
    s.state_vector = complex_matmul(measurement_matrix, s.state_vector)
    normaliser = 0
    for i in range(s.num_states):
        normaliser += s.state_vector[i][0][0]**2 + s.state_vector[0][0][1]**2
    s.state_vector = s.state_vector/np.sqrt(normaliser)