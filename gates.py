import numpy as np
import random


class GateError(Exception):
    pass


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
def apply_gate(s, chosen_matrix, gate_char, qubit=1):
    # TODO: handle cases like qubit being a string
    # Currently unnecessary as it is filtered out by the parser and command modules
    # But will need doing if gates becomes a standalone module
    # if not isinstance(qubit, int):
    #     raise GateError(f"{s.state_name}: qubit {qubit} is not an integer")
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


def apply_cgate(s, chosen_matrix, gate_char, control=1, target=2):
    if control != target:
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
            s.update_circuit(new_wire)
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
    else:
        raise GateError(f"{s.state_name}: controlled gate with control={control}, target={target}: control and target cannot be the same")


def X(s, qubit):
    apply_gate(s, X_matrix, "X", qubit)


def Y(s, qubit):
    apply_gate(s, Y_matrix, "Y", qubit)


def Z(s, qubit):
    apply_gate(s, Z_matrix, "Z", qubit)


def H(s, qubit):
    apply_gate(s, H_matrix, "H", qubit)


def P(s, qubit):
    apply_gate(s, P_matrix, "P", qubit)


def T(s, qubit):
    apply_gate(s, T_matrix, "T", qubit)


def CNOT(s, control, target):
    apply_cgate(s, X_matrix, "X", control, target)


def C_Y(s, control, target):
    apply_cgate(s, Y_matrix, "Y", control, target)


def C_Z(s, control, target):
    apply_cgate(s, Z_matrix, "Z", control, target)


def C_H(s, control, target):
    apply_cgate(s, H_matrix, "H", control, target)


def C_P(s, qubit):
    apply_cgate(s, P_matrix, "P", control, target)


def C_T(s, qubit):
    apply_cgate(s, T_matrix, "T", control, target)


def swap(s, qubit1, qubit2):
    if s.num_qubits > 1:
        CNOT(s, qubit1, qubit2)
        CNOT(s, qubit2, qubit1)
        CNOT(s, qubit1, qubit2)


def Uf2(s, f_choice=random.randint(1, 4), qubit1=1, qubit2=2):
    if f_choice == 1:
        U_f_matrix = U_f_matrix_1
    elif f_choice == 2:
        U_f_matrix = U_f_matrix_2     
    elif f_choice == 3:
        U_f_matrix = U_f_matrix_3
    elif f_choice == 4:
        U_f_matrix = U_f_matrix_4
    if s.num_qubits < 2:
        raise GateError("{s.state_name}: Cannot apply two-qubit gate Uf2 to a one-qubit state")
    if qubit2 > s.num_qubits or qubit1 > s.num_qubits:
        raise GateError("{s.state_name}: When applying Uf2, found qubit reference(s) out of bounds")  
    if qubit1 + 1 != qubit2:
        raise GateError("{s.state_name}: Uf2 can only be applied to two qubits that are next to each other")    
    if qubit1 >= qubit2:
        raise GateError("{s.state_name}: When applying Uf2, the first qubit must be left of the second qubit")
    if (qubit1 == 1):
        gate_matrix = U_f_matrix
    else:
        gate_matrix = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == qubit1):
            gate_matrix = np.kron(gate_matrix, U_f_matrix)
        elif (i == qubit2): 
            continue
        else:
            gate_matrix = np.kron(gate_matrix, I_matrix)
    s.state_vector = gate_matrix @ s.state_vector
    new_wire = ""
    for i in range(0, s.num_qubits):
        if (i+1) == qubit1: 
            new_wire += "|Uf2"
        else:
            new_wire += "|"+" "*s.w
    s.update_circuit(new_wire)


gates_dict = {
    'X' : {'func' : X, 'nargs' : 1},
    'Y' : {'func' : Y, 'nargs' : 1},
    'Z' : {'func' : Z, 'nargs' : 1},
    'H' : {'func' : H, 'nargs' : 1},
    'P' : {'func' : P, 'nargs' : 1},
    'T' : {'func' : T, 'nargs' : 1},
    'CNOT' : {'func' : CNOT, 'nargs' : 2},
    'C_Y' : {'func' : C_Y, 'nargs' : 2},
    'C_Z' : {'func' : C_Z, 'nargs' : 2},
    'C_H' : {'func' : C_H, 'nargs' : 2},
    'C_P' : {'func' : C_P, 'nargs' : 2},
    'C_T' : {'func' : C_T, 'nargs' : 2},
    'SWAP' : {'func' : swap, 'nargs' : 2},
}