import numpy as np
import random

zero_matrix = np.array([[1+0j, 0+0j], [0+0j, 0+0j]])
one_matrix = np.array([[0+0j, 0+0j], [0+0j, 1+0j]])
I_matrix = np.array([[1+0j, 0+0j], [0+0j, 1+0j]])
X_matrix = np.array([[0+0j, 1+0j], [1+0j, 0+0j]])
Y_matrix = np.array([[0+0j, 0-1j], [0+1j, 0+0j]])
Z_matrix = np.array([[1+0j, 0+0j], [0+0j, -1+0j]])
H_matrix = np.array([[1+0j, 1+0j], [1+0j, -1+0j]])/np.sqrt(2)
P_matrix = np.array([[1+0j, 0+0j], [0+0j, 0+1j]])
T_matrix = np.array([[1+0j, 0+0j], [0+0j, (np.sqrt(2)/2)+(np.sqrt(2)/2)*1j]])
U_f_matrix_1 = np.array([[1+0j, 0+0j, 0+0j, 0+0j], [0+0j, 1+0j, 0+0j, 0+0j], [0+0j, 0+0j, 1+0j, 0+0j], [0+0j, 0+0j, 0+0j, 1+0j]]) 
U_f_matrix_2 = np.array([[0+0j, 1+0j, 0+0j, 0+0j], [1+0j, 0+0j, 0+0j, 0+0j], [0+0j, 0+0j, 0+0j, 1+0j], [0+0j, 0+0j, 1+0j, 0+0j]])         
U_f_matrix_3 = np.array([[1+0j, 0+0j, 0+0j, 0+0j], [0+0j, 1+0j, 0+0j, 0+0j], [0+0j, 0+0j, 0+0j, 1+0j], [0+0j, 0+0j, 1+0j, 0+0j]])  
U_f_matrix_4 = np.array([[1+0j, 0+0j, 0+0j, 0+0j], [0+0j, 1+0j, 0+0j, 0+0j], [0+0j, 0+0j, 0+0j, 1+0j], [0+0j, 0+0j, 1+0j, 0+0j]])

# Functions for manipulating quantum states
def apply_gate(s, qubit, chosen_matrix, gate_char):
    if (qubit == 1):
        gate_matrix = chosen_matrix
    else:
        gate_matrix = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == qubit):
            gate_matrix = np.kron(gate_matrix, chosen_matrix)
        else:
            gate_matrix = np.kron(gate_matrix, I_matrix)
    s.state_vector = gate_matrix @ s.state_vector
    new_wire = ""
    for i in range(0, s.num_qubits):
        if (i+1) == qubit: 
            new_wire += gate_char+" "*s.w
        else:
            new_wire += "|"+" "*s.w
    s.update_circuit(new_wire)

def apply_cgate(s, control, target, chosen_matrix, gate_char):
    if (control == 1):
        gate_matrix_a = zero_matrix
        gate_matrix_b = one_matrix
    elif (target == 1):
        gate_matrix_a = I_matrix
        gate_matrix_b = chosen_matrix
    else:
        gate_matrix_a = I_matrix
        gate_matrix_b = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == control):
            gate_matrix_a = np.kron(gate_matrix_a, zero_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, one_matrix)
        elif (i == target):
            gate_matrix_a = np.kron(gate_matrix_a, I_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, chosen_matrix)         
        else:
            gate_matrix_a = np.kron(gate_matrix_a, I_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, I_matrix)
    gate_matrix = np.add(gate_matrix_a, gate_matrix_b)
    s.state_vector = gate_matrix @ s.state_vector
    new_wire = ""
    gap = " "
    if control < target:
        for i in range(0, s.num_qubits):
            if (i+1) == control: 
                gap = "-"
                new_wire += "O"+gap*s.w
            elif (i+1) == target:
                gap = " "                    
                new_wire += gate_char+gap*s.w
            else:
                new_wire += "|"+gap*s.w
    elif target < control:
        for i in range(0, s.num_qubits):
            if (i+1) == control: 
                gap = " "
                new_wire += "O"+gap*s.w
            elif (i+1) == target:
                gap = "-"                    
                new_wire += gate_char+gap*s.w
            else:
                new_wire += "|"+gap*s.w
    s.update_circuit(new_wire)

def X(s, qubit=1):
    apply_gate(s, qubit, X_matrix, "X")

def Y(s, qubit=1):
    apply_gate(s, qubit, Y_matrix, "Y")

def Z(s, qubit=1):
    apply_gate(s, qubit, Z_matrix, "Z")

def H(s, qubit=1):
    apply_gate(s, qubit, H_matrix, "H")

def P(s, qubit=1):
    apply_gate(s, qubit, P_matrix, "P")

def T(s, qubit=1):
    apply_gate(s, qubit, T_matrix, "T")

def CNOT(s, control=1, target=2):
    apply_cgate(s, control, target, X_matrix, "X")

def C_Y(s, control=1, target=2):
    apply_cgate(s, control, target, Y_matrix, "Y")

def C_Z(s, control=1, target=2):
    apply_cgate(s, control, target, Z_matrix, "Z")

def C_H(s, control=1, target=2):
    apply_cgate(s, control, target, H_matrix, "H")

def C_P(s, qubit=1):
    apply_cgate(s, control, target, P_matrix, "P")

def C_T(s, qubit=1):
    apply_cgate(s, control, target, T_matrix, "T")

def swap(s, qubit1, qubit2):
    if s.num_qubits > 1:
        CNOT(s, control=qubit1, target=qubit2)
        CNOT(s, control=qubit2, target=qubit1)
        CNOT(s, control=qubit1, target=qubit2)

def Uf2(s, f_choice=random.randint(1, 4)):
    if f_choice == 1:
        U_f_matrix = U_f_matrix_1
    elif f_choice == 2:
        U_f_matrix = U_f_matrix_2     
    elif f_choice == 3:
        U_f_matrix = U_f_matrix_3
    elif f_choice == 4:
        U_f_matrix = U_f_matrix_4
    s.state_vector = U_f_matrix @ s.state_vector
    new_wire = "|Uf2|"
    s.update_circuit(new_wire)