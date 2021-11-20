import numpy as np
import random
from . import gates


# Class for creating, displaying and measuring quantum states
class QuantumState:
    __slots__ = 'num_qubits', 'num_classical_states', 'state_name', 'state_vector', 'num_actions', 'circuit'
    # Decimal place rounding accuracy (rounding occurs before measurement and when printing states)
    dp = 16
    # Width between wires in quantum circuit when displayed
    w = 3

    def __init__(self, num_qubits=1, preset_state=None, preset_state_vector=None, state_name=None):
        self.num_qubits = num_qubits
        self.num_classical_states = 2**self.num_qubits
        if state_name:
            self.state_name = state_name
        else:
            self.state_name = "(no name)"
        # The initial state vector will be generated randomly if neither a string description or ndarray are provided     
        if preset_state == "zero":
            # The zero state is the state |00...00>
            self.state_vector = np.zeros(self.num_classical_states) + np.zeros(self.num_classical_states) * 1j
            self.state_vector[0] = 1
        elif preset_state == "one":
            # The one state is the state |11...11>
            self.state_vector = np.zeros(self.num_classical_states) + np.zeros(self.num_classical_states) * 1j
            self.state_vector[-1] = 1
        elif isinstance(preset_state_vector, np.ndarray):
            self.state_vector = preset_state_vector
        else:
            # A state vector is created with random values from the unit circle around the origin
            self.state_vector = (2*np.random.random(self.num_classical_states)-1) + (2*np.random.random(self.num_classical_states)-1) * 1j
            # The vector is normalised to have length 1
            self.state_vector = self.state_vector/np.linalg.norm(self.state_vector)
        # Create the initial circuit string for the state
        self.num_actions = 0
        self.circuit = [""]
        for i in range(0, self.num_qubits):
            self.circuit[0] += f"{(i+1)%10}{' '*QuantumState.w}"     
        self.circuit.append(self.blank_circuit_lanes())

    # Merges QuantumState object q into the current object
    def __mul__(self, q): 
        # Merge circuits first because this requires using attributes from both objects
        diff_in_length = len(self.circuit) - len(q.circuit)
        # q.circuit is longer
        if diff_in_length < 0:
            joint_circuit_length = len(q.circuit)
            for i in range(abs(diff_in_length)):
                self.circuit.append(self.blank_circuit_lanes(include_actions=False))
        # self.circuit is longer
        elif diff_in_length > 0:
            joint_circuit_length = len(self.circuit)
            for i in range(abs(diff_in_length)):
                q.circuit.append(q.blank_circuit_lanes(include_actions=False))
        # The circuits are the same length, so we can take the length of either
        else:
            joint_circuit_length = len(self.circuit)
        merged_circuit = [""]
        for i in range(0, self.num_qubits + q.num_qubits):
            merged_circuit[0] += f"{(i+1)%10}{' '*QuantumState.w}"
        merged_circuit.append(self.blank_circuit_lanes(include_actions=False) + q.blank_circuit_lanes(action_value=0))
        for i in range(2, joint_circuit_length, 2):
            merged_circuit.append(self.circuit[i] + q.circuit[i])
            merged_circuit.append(self.blank_circuit_lanes(include_actions=False) + q.blank_circuit_lanes(action_value=int(i/2)))
        # Update all attributes to factor in q
        self.num_qubits += q.num_qubits
        self.num_classical_states = 2**self.num_qubits
        self.state_name += f"x{q.state_name}"
        self.state_vector = np.kron(self.state_vector, q.state_vector)
        self.num_actions = max(self.num_actions, q.num_actions)
        self.circuit = merged_circuit 
        # Delete reference to q
        del q
        return self

    def blank_circuit_lanes(self, action_value=None, num_qubits=None, include_actions=True):
        if action_value is None:
            action_value = self.num_actions
        if num_qubits is None:
            num_qubits = self.num_qubits
        lanes = ""
        for i in range(0, num_qubits):
            lanes += f"|{' '*QuantumState.w}"
        if include_actions:
            lanes += f"{' '*QuantumState.w}[{action_value}]"
        return lanes

    def update_circuit(self, new_wire):
        self.num_actions += 1
        self.circuit.append(f"{new_wire}")
        self.circuit.append(self.blank_circuit_lanes())

    def measurement(self, qubit=1):
        if (qubit == 1):
            measurement_matrix_zero = gates.zero_matrix
            measurement_matrix_one = gates.one_matrix
        else:
            measurement_matrix_zero = gates.I_matrix
            measurement_matrix_one = gates.I_matrix
        for i in range(2, self.num_qubits+1):
            if (i == qubit):
                measurement_matrix_zero = np.kron(measurement_matrix_zero, gates.zero_matrix)
                measurement_matrix_one = np.kron(measurement_matrix_one, gates.one_matrix)
            else:
                measurement_matrix_zero = np.kron(measurement_matrix_zero, gates.I_matrix)
                measurement_matrix_one = np.kron(measurement_matrix_one, gates.I_matrix)
        collapsed_zero = measurement_matrix_zero @ self.state_vector
        collapsed_one = measurement_matrix_one @ self.state_vector
        zero_probability = self.state_vector.conjugate().transpose() @ measurement_matrix_zero.conjugate().transpose() @ collapsed_zero
        one_probability = self.state_vector.conjugate().transpose() @ measurement_matrix_one.conjugate().transpose() @ collapsed_one
        # Dividing each probability by their sum gets the sum of both resulting probabilities (closer) to 1    
        sum_of_probabilities = zero_probability + one_probability
        zero_probability = round(zero_probability/sum_of_probabilities, QuantumState.dp)
        one_probability = round(one_probability/sum_of_probabilities, QuantumState.dp)
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
                new_wire += f"M={bit}"+gap
            else:
                new_wire += "|"+gap*QuantumState.w
        self.update_circuit(new_wire)
        return bit
    
    def print_state(self):
        gen_classical_states = ((i, bin(i)[2:].zfill(self.num_qubits)) for i in range(self.num_classical_states))   
        print(f"State vector for {self.state_name} [{self.num_actions}]:")
        first_line = True
        for i, bin_i in gen_classical_states:
            current_amplitude = round(self.state_vector[i].real, QuantumState.dp) + round(self.state_vector[i].imag, QuantumState.dp) * 1j
            if current_amplitude != 0:
                if first_line:
                    print(f" {self.state_name} = {current_amplitude} |{bin_i}>")
                    first_line = False
                else:
                    print(f" {' ' * len(self.state_name)} + {current_amplitude} |{bin_i}>")

    def print_circuit(self):
        print(f"Circuit diagram for {self.state_name}:")
        for x in self.circuit:
            print(" " + x)

    def print_prob_dist(self):
        gen_classical_states = ((i, bin(i)[2:].zfill(self.num_qubits)) for i in range(self.num_classical_states))
        print(f"Probability distribution for {self.state_name} {[self.num_actions]}:")
        for i, bin_i in gen_classical_states:
            print(f" {bin_i}\t{round(abs(self.state_vector[i])**2, 2)}\t|{'=' * int(round(50 * abs(self.state_vector[i])**2))}")