import numpy as np
import random
from gates import *

# Class for creating, displaying and measuring quantum states
class QuantumState:
    # Creates a new QuantumState object
    def __init__(self, num_qubits=1, preset_state=None, preset_state_vector=None, state_name=None):
        # Decimal place rounding accuracy (rounding occurs before measurement and when printing states)
        self.dp = 16
        # Set number of qubits and the corresponding number of classical states
        self.num_qubits = num_qubits
        self.num_classical_states = 2**self.num_qubits
        # Set the name of the state, if provided
        self.state_name = ""
        if state_name != None:
            self.state_name = state_name
        else:
            self.state_name = "(no name)"
        # The initial state vector will be generated randomly if neither a string description or ndarray are provided     
        if preset_state == "zero_state":
            # The zero state is the state |00...00>
            self.state_vector = np.zeros(self.num_classical_states) + np.zeros(self.num_classical_states) * 1j
            self.state_vector[0] = 1
        elif preset_state == "one_state":
            # The one state is the state |11...11>
            self.state_vector = np.zeros(self.num_classical_states) + np.zeros(self.num_classical_states) * 1j
            self.state_vector[self.num_classical_states-1] = 1
        elif isinstance(preset_state_vector, np.ndarray):
            self.state_vector = preset_state_vector
        else:
            # A state vector is created with random values from the unit circle around the origin
            self.state_vector = (2*np.random.random(self.num_classical_states)-1) + (2*np.random.random(self.num_classical_states)-1) * 1j
            # The vector is normalised to have length 1
            self.state_vector = self.state_vector/np.linalg.norm(self.state_vector)
        # Function which creates the initial circuit string for the state
        self.init_circuit()

    # Merges the QuantumState object q into the current object
    def __mul__(self, q):
        self.num_qubits += q.num_qubits
        self.num_classical_states = 2**self.num_qubits
        self.state_name += f"x{q.state_name}"
        self.state_vector = np.kron(self.state_vector, q.state_vector)
        self.init_circuit()
        return self

    def blank_circuit_lanes(self):
        lanes = "\n "
        for i in range(0, self.num_qubits):
            lanes += f"|{' '*self.w}"
        lanes += f"{' '*self.w}[{self.num_actions}]\n"
        return lanes

    def init_circuit(self):
        self.num_actions = 0
        self.w = 3
        self.circuit_string = " "
        for i in range(0, self.num_qubits):
            self.circuit_string += f"{(i+1)%10}{' '*self.w}"     
        self.circuit_string += self.blank_circuit_lanes()

    def update_circuit(self, new_wire):
        self.num_actions += 1
        self.circuit_string += f" {new_wire}"
        self.circuit_string += self.blank_circuit_lanes()

    def measurement(self, qubit=1):
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
        collapsed_zero = measurement_matrix_zero @ self.state_vector
        collapsed_one = measurement_matrix_one @ self.state_vector
        zero_probability = self.state_vector.conjugate().transpose() @ measurement_matrix_zero.conjugate().transpose() @ collapsed_zero
        one_probability = self.state_vector.conjugate().transpose() @ measurement_matrix_one.conjugate().transpose() @ collapsed_one
        # Dividing each probability by their sum gets the sum of both resulting probabilities (closer) to 1    
        sum_of_probabilities = zero_probability + one_probability
        zero_probability = round(zero_probability/sum_of_probabilities, self.dp)
        one_probability = round(one_probability/sum_of_probabilities, self.dp)
        dice = random.random()
        if dice < zero_probability:
            self.state_vector = collapsed_zero
            bit = 0
        else:
            self.state_vector = collapsed_one
            bit = 1
        self.state_vector = self.state_vector/np.linalg.norm(self.state_vector)
        new_wire = ""
        gap = " "
        for i in range(0, self.num_qubits):
            if (i+1) == qubit: 
                gap = "="
                new_wire += "M"+gap*self.w
            else:
                new_wire += "|"+gap*self.w
        new_wire += str(bit)
        self.update_circuit(new_wire)
        return bit

    def print_state(self):
        state_string = f"{self.state_name} = "
        for i in range(0, self.num_classical_states):
            current_amplitude = round(self.state_vector[i].real, self.dp) + round(self.state_vector[i].imag, self.dp) * 1j
            if current_amplitude != 0:
                current_amplitude_string = str(current_amplitude)
                state_string += f"{current_amplitude_string} |{bin(i)[2:].zfill(self.num_qubits)}>\n"
        newline_count = state_string.count("\n")
        state_string = state_string.replace("\n", f"\n{' ' * len(self.state_name)} + ", newline_count-1)
        print(f"State vector for {self.state_name} [{self.num_actions}]:\n{state_string[:len(state_string)-1]}")

    def print_circuit(self):
        print(f"Circuit diagram for {self.state_name}:\n{self.circuit_string[:len(self.circuit_string)-1]}") # more dodgy

    def print_probabilities(self):
        print(f"Probabilities for {self.state_name} {[self.num_actions]}:")
        for i in range(0, self.num_classical_states):
            print(f" {bin(i)[2:].zfill(self.num_qubits)}\t{round(abs(self.state_vector[i])**2, 2)}\t{'=' * round(50 * abs(self.state_vector[i])**2)}")