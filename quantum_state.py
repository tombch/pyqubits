from random import random
import numpy as np
import linear_algebra as la

class QuantumState:
    #NEW
    def __init__(self, num_qubits, preset_state=None, preset_state_vector=None, state_name=""):
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

    def print_state(self):
        state_string = str(self.state_name) + " = "
        for i in range(0, self.num_classical_states):
            current_amplitude_string = str(self.state_vector[i])
            if current_amplitude_string != "0j":
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

        dice = random()
        if dice < zero_probability:
            self.state_vector = collapsed_zero
            bit = 0
        else:
            self.state_vector = collapsed_one
            bit = 1
        self.state_vector = self.state_vector/np.sqrt(np.sum(self.state_vector**2))
        return bit       



    #OLD
    def __init__old(self, num_qubits, preset_state=""):
        self.num_qubits = num_qubits
        self.num_states = 2**num_qubits
        if preset_state == "zero_state":
            self.state_vector = np.zeros((self.num_states, 1, 2))
            self.state_vector[0][0] = np.array([1,0])
        elif preset_state == "one_state":
            self.state_vector = np.zeros((self.num_states, 1, 2))
            self.state_vector[self.num_states-1][0] = np.array([1,0])
        else:
            self.state_vector = np.zeros((self.num_states, 1, 2))
            for i in range(self.num_states):
                (self.state_vector[i][0][0], self.state_vector[i][0][1]) = (2*random()-1, 2*random()-1)
            self.state_vector = self.state_vector/la.normaliser(self.state_vector)

    def show_amplitude_old(self, z):
        if (z[1] == 0):
            return str(z[0])         
        elif (z[0] == 0):
            return str(z[1]) + " i" 
        else:
            return str(z[0]) + " + " + str(z[1]) + " i"

    def print_state_old(self):     
        state_string = " = "
        for i in range(0, self.num_states):
            if str(self.state_vector[i][0]) != "0.0":   
                state_string += "(" + str(self.state_vector[i][0]) + ") |" + bin(i)[2:].zfill(self.num_qubits) + ">\n"
        newline_count = state_string.count("\n")
        state_string = state_string.replace("\n", "\n + ", newline_count-1)
        state_string = state_string.replace("(1.0) ", "")
        print(state_string)

    def measurement_old(self, qubit):
        I_matrix = np.array([[[1,0], [0,0]], [[0,0], [1,0]]])
        zero_matrix = np.array([[[1,0], [0,0]], [[0,0], [0,0]]]) 
        one_matrix = np.array([[[0,0], [0,0]], [[0,0], [1,0]]])
        if (qubit == 1):
            measurement_matrix_zero = zero_matrix
            measurement_matrix_one = one_matrix
        else:
            measurement_matrix_zero = I_matrix
            measurement_matrix_one = I_matrix
        for i in range(2, self.num_qubits+1):
            if (i == qubit):
                measurement_matrix_zero = la.kronecker_product(measurement_matrix_zero, zero_matrix)
                measurement_matrix_one = la.kronecker_product(measurement_matrix_one, one_matrix)
            else:
                measurement_matrix_zero = la.kronecker_product(measurement_matrix_zero, I_matrix)
                measurement_matrix_one = la.kronecker_product(measurement_matrix_one, I_matrix)
        
        collapsed_zero = la.complex_matmul(measurement_matrix_zero, self.state_vector)
        zero_probability = la.complex_matmul(la.conjugate_transpose(measurement_matrix_zero), collapsed_zero)
        zero_probability = la.complex_matmul(la.conjugate_transpose(self.state_vector), zero_probability)[0][0][0]

        collapsed_one = la.complex_matmul(measurement_matrix_one, self.state_vector)
        one_probability = la.complex_matmul(la.conjugate_transpose(measurement_matrix_one), collapsed_one)
        one_probability = la.complex_matmul(la.conjugate_transpose(self.state_vector), one_probability)[0][0][0]

        dice = random()
        if dice < zero_probability:
            self.state_vector = collapsed_zero
            bit = 0
        else:
            self.state_vector = collapsed_one
            bit = 1
        self.state_vector = self.state_vector/la.normaliser(self.state_vector)
        return bit