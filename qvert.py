import numpy as np
import random

#Class for creating, displaying and measuring quantum states
class QuantumState:
    def __init__(self, num_qubits=1, preset_state=None, preset_state_vector=None, state_name=""):
        self.num_qubits = num_qubits
        self.num_classical_states = 2**num_qubits
        self.state_name = state_name
        if preset_state == "zero_state":
            self.state_vector = np.zeros(self.num_classical_states) + np.zeros(self.num_classical_states) * 1j
            self.state_vector[0] = 1
        elif preset_state == "one_state":
            self.state_vector = np.zeros(self.num_classical_states) + np.zeros(self.num_classical_states) * 1j
            self.state_vector[self.num_classical_states-1] = 1
        elif type(preset_state_vector) is np.ndarray:
            self.state_vector = preset_state_vector
        else:
            self.state_vector = (2*np.random.random(self.num_classical_states)-1) + (2*np.random.random(self.num_classical_states)-1) * 1j
            self.state_vector = self.state_vector/np.sqrt(np.sum(self.state_vector**2))

    def print_state(self, dp=16):
        state_string = str(self.state_name) + " = "
        for i in range(0, self.num_classical_states):
            current_amplitude = self.state_vector[i]
            if current_amplitude != 0:
                current_amplitude_string = str(round(current_amplitude.real, dp) + round(current_amplitude.imag, dp) * 1j)
                state_string += current_amplitude_string + " |" + bin(i)[2:].zfill(self.num_qubits) + ">\n"
        newline_count = state_string.count("\n")
        state_string = state_string.replace("\n", "\n" + " " * len(self.state_name) + " + ", newline_count-1)
        print(state_string)

    def measurement(self, qubit):
        I_matrix = np.array([[1+0j, 0+0j],
                             [0+0j, 1+0j]])
        zero_matrix = np.array([[1+0j, 0+0j],
                                [0+0j, 0+0j]])
        one_matrix = np.array([[0+0j, 0+0j],
                               [0+0j, 1+0j]])
        if (qubit == 1):
            measurement_matrix_zero = zero_matrix
            measurement_matrix_one = one_matrix
        else:
            measurement_matrix_zero = I_matrix
            measurement_matrix_one = I_matrix
        for i in range(2, self.num_qubits+1):
            if (i == qubit):
                measurement_matrix_zero = np.kron(measurement_matrix_zero, zero_matrix)
                measurement_matrix_one = np.kron(measurement_matrix_one, one_matrix)
            else:
                measurement_matrix_zero = np.kron(measurement_matrix_zero, I_matrix)
                measurement_matrix_one = np.kron(measurement_matrix_one, I_matrix)

        collapsed_zero = np.matmul(measurement_matrix_zero, self.state_vector)
        zero_probability = np.matmul(measurement_matrix_zero.conjugate().transpose(), collapsed_zero)   
        zero_probability = np.matmul(self.state_vector.conjugate().transpose(), zero_probability)

        collapsed_one = np.matmul(measurement_matrix_one, self.state_vector)
        one_probability = np.matmul(measurement_matrix_one.conjugate().transpose(), collapsed_one)
        one_probability = np.matmul(self.state_vector.conjugate().transpose(), one_probability)

        dice = random.random()
        if dice < zero_probability:
            self.state_vector = collapsed_zero
            bit = 0
        else:
            self.state_vector = collapsed_one
            bit = 1
        self.state_vector = self.state_vector/np.sqrt(np.sum(self.state_vector**2))
        return bit

#Functions for manipulating quantum states
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

def U_f(s, f_choice=random.randint(1, 4)):
    if f_choice == 1:
        U_f_matrix = np.array([[1+0j, 0+0j, 0+0j, 0+0j],
                               [0+0j, 1+0j, 0+0j, 0+0j],
                               [0+0j, 0+0j, 1+0j, 0+0j],
                               [0+0j, 0+0j, 0+0j, 1+0j]]) 
    elif f_choice == 2:
        U_f_matrix = np.array([[0+0j, 1+0j, 0+0j, 0+0j],
                               [1+0j, 0+0j, 0+0j, 0+0j],
                               [0+0j, 0+0j, 0+0j, 1+0j],
                               [0+0j, 0+0j, 1+0j, 0+0j]])         
    elif f_choice == 3:
        U_f_matrix = np.array([[1+0j, 0+0j, 0+0j, 0+0j],
                               [0+0j, 1+0j, 0+0j, 0+0j],
                               [0+0j, 0+0j, 0+0j, 1+0j],
                               [0+0j, 0+0j, 1+0j, 0+0j]])  
    elif f_choice == 4:
        U_f_matrix = np.array([[1+0j, 0+0j, 0+0j, 0+0j],
                               [0+0j, 1+0j, 0+0j, 0+0j],
                               [0+0j, 0+0j, 0+0j, 1+0j],
                               [0+0j, 0+0j, 1+0j, 0+0j]])
    s.state_vector = np.matmul(U_f_matrix, s.state_vector)

def swap(s, qubit1, qubit2):
    if s.num_qubits > 1:
        CNOT(s, control=qubit1, target=qubit2)
        CNOT(s, control=qubit2, target=qubit1)
        CNOT(s, control=qubit1, target=qubit2)

def join_states(s_list, state_name=""):
    s_list_len = len(s_list)
    if s_list_len > 0:
        s_joint_num_qubits = s_list[0].num_qubits
        s_joint_state_vector = s_list[0].state_vector
        for i in range(1, s_list_len):
            s_joint_num_qubits = s_joint_num_qubits + s_list[i].num_qubits
            s_joint_state_vector = np.kron(s_joint_state_vector, s_list[i].state_vector)
        s_joint = QuantumState(num_qubits=s_joint_num_qubits, preset_state_vector=s_joint_state_vector, state_name=state_name)
    else:
        s_joint = None
    return s_joint