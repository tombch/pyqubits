from random import random
import numpy as np
import complex_number as cn

class Qubit:
    def __init__(self, name, set_qubit=""):
        self.name = name
        if set_qubit == "zero":
            (a0, b0, a1, b1) = (1.0, 0.0, 0.0, 0.0)
        elif set_qubit == "one":
            (a0, b0, a1, b1) = (0.0, 0.0, 1.0, 0.0)    
        else:
            (a0, b0, a1, b1) = (random(), random(), random(), random())
        normaliser = np.sqrt(a0**2 + b0**2 + a1**2 + b1**2)
        self.state_vector = np.array([[a0, b0],[a1, b1]])/normaliser
    
    def measurement(self):
        zero_probability = self.state_vector[0][0]**2 + self.state_vector[0][1]**2
        one_probability = self.state_vector[1][0]**2 + self.state_vector[1][1]**2
        outcome = random()
        if outcome <= zero_probability: #not perfect
            self.state_vector = np.array([[1.0, 0.0],[0.0, 0.0]])
        else:
            self.state_vector = np.array([[0.0, 0.0],[1.0, 0.0]])
        print(self.name + " --> [_/_](" + self.name + ")")

    def print_state(self):
        print(self.name + " = (" + cn.show(self.state_vector[0]) + ") |0> + (" + cn.show(self.state_vector[1]) + ") |1>")
