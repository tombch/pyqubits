from random import random
import numpy as np
import linear_algebra as la

class Qubits:
    def __init__(self, num, set_qubit=""):
        self.num_qubits = num
        self.num_states = 2**num
        if set_qubit == "zero_state":
            self.state_vector = np.zeros((self.num_states, 1, 2))
            self.state_vector[0][0] = np.array([1,0])
        elif set_qubit == "one_state":
            self.state_vector = np.zeros((self.num_states, 1, 2))
            self.state_vector[self.num_states-1][0] = np.array([1,0])
        else:
            self.state_vector = np.zeros((self.num_states, 1, 2))
            for i in range(self.num_states):
                (self.state_vector[i][0][0], self.state_vector[i][0][1]) = (random(), random())
            self.state_vector = self.state_vector/la.normaliser(self.state_vector)

    def show_amplitude(self, z):
        if (z[1] == 0):
            return str(z[0])         
        elif (z[0] == 0):
            return str(z[1]) + " i" 
        else:
            return str(z[0]) + " + " + str(z[1]) + " i"

    def print_state(self):     
        state_string = " = "
        for i in range(0, self.num_states):
            if self.show_amplitude(self.state_vector[i][0]) != "0.0":   
                state_string += "(" + self.show_amplitude(self.state_vector[i][0]) + ") |" + bin(i)[2:].zfill(self.num_qubits) + ">\n"
        newline_count = state_string.count("\n")
        state_string = state_string.replace("\n", "\n + ", newline_count-1)
        state_string = state_string.replace("(1.0) ", "")
        print(state_string)

    def measurement(self, qubit):
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