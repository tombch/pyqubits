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
    
    def print_state(self):      
        state_string = " = (" + la.show(self.state_vector[0][0]) + ") |" + bin(0)[2:].zfill(self.num_qubits) + ">"
        for i in range(1, self.num_states):
            state_string += "\n + (" + la.show(self.state_vector[i][0]) + ") |" + bin(i)[2:].zfill(self.num_qubits) + ">"
        print(state_string + "\n")
        