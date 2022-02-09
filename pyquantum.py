import random
import numpy as np

zero_matrix = np.array([
    [1+0j, 0+0j], 
    [0+0j, 0+0j]
])

one_matrix = np.array([
    [0+0j, 0+0j], 
    [0+0j, 1+0j]
])

I_matrix = np.array([
    [1+0j, 0+0j], 
    [0+0j, 1+0j]
])

X_matrix = np.array([
    [0+0j, 1+0j], 
    [1+0j, 0+0j]
])

Y_matrix = np.array([
    [0+0j, 0-1j], 
    [0+1j, 0+0j]
])

Z_matrix = np.array([
    [1+0j, 0+0j], 
    [0+0j, -1+0j]
])

H_matrix = np.array([
    [1+0j, 1+0j], 
    [1+0j, -1+0j]
])/np.sqrt(2)

P_matrix = np.array([
    [1+0j, 0+0j], 
    [0+0j, 0+1j]
])

T_matrix = np.array([
    [1+0j, 0+0j], 
    [0+0j, (np.sqrt(2)/2)+(np.sqrt(2)/2)*1j]
])

U_f_matrix_1 = np.array([
    [1+0j, 0+0j, 0+0j, 0+0j], 
    [0+0j, 1+0j, 0+0j, 0+0j], 
    [0+0j, 0+0j, 1+0j, 0+0j], 
    [0+0j, 0+0j, 0+0j, 1+0j]
]) 

U_f_matrix_2 = np.array([
    [0+0j, 1+0j, 0+0j, 0+0j], 
    [1+0j, 0+0j, 0+0j, 0+0j], 
    [0+0j, 0+0j, 0+0j, 1+0j], 
    [0+0j, 0+0j, 1+0j, 0+0j]
])         

U_f_matrix_3 = np.array([
    [1+0j, 0+0j, 0+0j, 0+0j], 
    [0+0j, 1+0j, 0+0j, 0+0j], 
    [0+0j, 0+0j, 0+0j, 1+0j], 
    [0+0j, 0+0j, 1+0j, 0+0j]
])  

U_f_matrix_4 = np.array([
    [1+0j, 0+0j, 0+0j, 0+0j], 
    [0+0j, 1+0j, 0+0j, 0+0j], 
    [0+0j, 0+0j, 0+0j, 1+0j], 
    [0+0j, 0+0j, 1+0j, 0+0j]
])

class QuantumStateError(Exception):
    pass

def validate_qubit(method):
    def wrapped_method(obj, qubit):
        if (not isinstance(qubit, int)) or (not (1 <= qubit <= obj._num_qubits)):
            raise QuantumStateError("'qubit' must be a positive integer, less than or equal to the number of qubits in the state")
        return method(obj, qubit)
    return wrapped_method

def validate_control_target(method):
    def wrapped_method(obj, control, target):
        if (not isinstance(control, int)) or (not (1 <= control <= obj._num_qubits)):
            raise QuantumStateError("'control' must be a positive integer, less than or equal to the number of qubits in the state")
        if (not isinstance(target, int)) or (not (1 <= target <= obj._num_qubits)):
            raise QuantumStateError("'target' must be a positive integer, less than or equal to the number of qubits in the state")
        if control == target:
            raise QuantumStateError("'control' and 'target' cannot be the same")
        return method(obj, control, target)
    return wrapped_method

class QuantumState:
    '''
    A class for representing and manipulating multi-qubit states.

    `qubits`: The number of qubits to initialise the state with.
    `vector`: Set the initial state to a chosen computational basis vector, given as a binary number string of length `qubits`.

    Examples:
    * `s = QuantumState()`
    * `s = QuantumState(qubits=2)`
    * `s = QuantumState(qubits=3, vector='111')`
    * `s = QuantumState(qubits=5, vector='01000')`
    '''

    __slots__ = '_num_qubits', '_num_classical_states', '_state_vector', '_num_stages', '_circuit'
    # Decimal place rounding accuracy (rounding occurs before measurement and when printing states)
    decimal_places = 16
    # Width between wires in quantum circuit when displayed
    lane_width = 3

    def __init__(self, qubits : int = 1, vector : str = ''):
        if (not isinstance(qubits, int)) or qubits < 1:
            raise QuantumStateError("'qubits' must be a positive integer") 
        self._num_qubits = qubits
        self._num_classical_states = 2**self._num_qubits
        if vector:
            if isinstance(vector, str) and (len(vector) == self._num_qubits) and (not [c for c in vector if c != '0' and c != '1']):
                self._state_vector = np.zeros(self._num_classical_states) + np.zeros(self._num_classical_states) * 1j
                self._state_vector[int(vector, 2)] = 1
            else:
                raise QuantumStateError(f"'vector' must be a binary number string of length {self._num_qubits}")
        else:
            # A state vector is created with random values from the unit circle around the origin
            self._state_vector = (2*np.random.random(self._num_classical_states)-1) + (2*np.random.random(self._num_classical_states)-1) * 1j
            # The vector is normalised
            self._state_vector = self._state_vector/np.linalg.norm(self._state_vector)
        # Initialise circuit
        self._num_stages = 0
        self._circuit = []
        lane = []
        for i in range(0, self._num_qubits):
            lane.append((i + 1) % 10)
        self._circuit.append(lane)
        self._circuit.append(self._empty_circuit_row())

    def _empty_circuit_row(self):
        lanes = []
        for _ in range(0, self._num_qubits):
            lanes.append("|")
        lanes.append(self._num_stages)
        return lanes
    
    def _update_circuit(self, new_wire):
        self._num_stages += 1
        self._circuit.append(new_wire)
        self._circuit.append(self._empty_circuit_row())

    def _apply_gate(self, chosen_matrix, gate_char, qubit):
        if (qubit == 1):
            gate_matrix = chosen_matrix
        else:
            gate_matrix = I_matrix
        for i in range(2, self._num_qubits+1):
            if (i == qubit):
                gate_matrix = np.kron(gate_matrix, chosen_matrix)
            else:
                gate_matrix = np.kron(gate_matrix, I_matrix)
        self._state_vector = gate_matrix @ self._state_vector
        new_wire = []
        for i in range(0, self._num_qubits):
            if (i+1) == qubit: 
                new_wire.append(gate_char)
            else:
                new_wire.append("|")
        self._update_circuit(new_wire)

    def _apply_cgate(self, chosen_matrix, gate_char, control, target):
        if (control == 1):
            gate_matrix_a = zero_matrix
            gate_matrix_b = one_matrix
        elif (target == 1):
            gate_matrix_a = I_matrix
            gate_matrix_b = chosen_matrix
        else:
            gate_matrix_a = I_matrix
            gate_matrix_b = I_matrix
        for i in range(2, self._num_qubits+1):
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
        self._state_vector = gate_matrix @ self._state_vector
        new_wire = []
        for i in range(0, self._num_qubits):
            if (i+1) == control: 
                new_wire.append("O")
            elif (i+1) == target:
                new_wire.append(gate_char)
            else:
                new_wire.append("|")
        self._update_circuit(new_wire)

    # def __mul__(self, q): 
    #     # Merge circuits first because this requires using attributes from both objects
    #     diff_in_length = len(self._circuit) - len(q.circuit)
    #     # q.circuit is longer
    #     if diff_in_length < 0:
    #         joint_circuit_length = len(q.circuit)
    #         for i in range(abs(diff_in_length)):
    #             self._circuit.append(self._empty_circuit_row(include_stages=False))
    #     # self._circuit is longer
    #     elif diff_in_length > 0:
    #         joint_circuit_length = len(self._circuit)
    #         for i in range(abs(diff_in_length)):
    #             q.circuit.append(q._empty_circuit_row(include_stages=False))
    #     # The circuits are the same length, so we can take the length of either
    #     else:
    #         joint_circuit_length = len(self._circuit)
    #     merged_circuit = [""]
    #     for i in range(0, self._num_qubits + q._num_qubits):
    #         merged_circuit[0] += f"{(i+1)%10}{' '*QuantumState.lane_width}"
    #     merged_circuit.append(self._empty_circuit_row(include_stages=False) + q._empty_circuit_row(current_stage=0))
    #     for i in range(2, joint_circuit_length, 2):
    #         merged_circuit.append(self._circuit[i] + q.circuit[i])
    #         merged_circuit.append(self._empty_circuit_row(include_stages=False) + q._empty_circuit_row(current_stage=int(i/2)))
    #     # Update all attributes to factor in q
    #     self._num_qubits += q._num_qubits
    #     self._num_classical_states = 2**self._num_qubits
    #     self._state_vector = np.kron(self._state_vector, q._state_vector)
    #     self._num_stages = max(self._num_stages, q._num_stages)
    #     self._circuit = merged_circuit 
    #     # Delete reference to q
    #     del q
    #     return self

    def vector(self):
        return self._state_vector

    def state(self):
        def get_state(state_vector):
            state_string = ''
            gen_classical_states = ((i, bin(i)[2:].zfill(self._num_qubits)) for i in range(self._num_classical_states))
            first_non_zero = True  
            for i, bin_i in gen_classical_states:
                current_amplitude = round(state_vector[i].real, QuantumState.decimal_places) + round(state_vector[i].imag, QuantumState.decimal_places) * 1j
                if current_amplitude != 0:
                    state_string += f"{'=' if first_non_zero else '+'} {current_amplitude} |{bin_i}>\n"
                    first_non_zero = False
            return state_string[:-1]
        return get_state(self._state_vector)

    def dist(self):
        def get_dist(state_vector):
            dist_string = ''
            gen_classical_states = ((i, bin(i)[2:].zfill(self._num_qubits)) for i in range(self._num_classical_states))
            for i, bin_i in gen_classical_states:
                dist_string += f"{bin_i}\t{round(abs(state_vector[i])**2, 2)}\t|{'=' * int(round(50 * abs(state_vector[i])**2))}\n"
            return dist_string[:-1]
        return get_dist(self._state_vector)

    def circuit(self):
        circuit_string = ''
        for row in self._circuit:
            row_string = ""
            for col in row:
                row_string += str(col) + " " * QuantumState.lane_width
            if 'O' in row_string:
                o_pos = row_string.index('O')
                gate_pos = -1
                for x in row_string:
                    if not (x in 'O| '):
                        gate_pos = row_string.index(x)
                if o_pos < gate_pos:
                    row_string = row_string[0:o_pos+1] + (abs(o_pos - gate_pos) - 1) * '-' + row_string[gate_pos:]
                else:
                    row_string = row_string[0:gate_pos+1] + (abs(o_pos - gate_pos) - 1) * '-' + row_string[o_pos:]
            circuit_string += f'{row_string}\n'
        return circuit_string[:-1]

    @validate_qubit
    def measure(self, qubit : int):
        '''
        Measure a `qubit` within the quantum state, and return the result.
        '''
        if (qubit == 1):
            measurement_matrix_zero = zero_matrix
            measurement_matrix_one = one_matrix
        else:
            measurement_matrix_zero = I_matrix
            measurement_matrix_one = I_matrix
        for i in range(2, self._num_qubits+1):
            if (i == qubit):
                measurement_matrix_zero = np.kron(measurement_matrix_zero, zero_matrix)
                measurement_matrix_one = np.kron(measurement_matrix_one, one_matrix)
            else:
                measurement_matrix_zero = np.kron(measurement_matrix_zero, I_matrix)
                measurement_matrix_one = np.kron(measurement_matrix_one, I_matrix)
        collapsed_zero = measurement_matrix_zero @ self._state_vector
        collapsed_one = measurement_matrix_one @ self._state_vector
        zero_probability = self._state_vector.conjugate().transpose() @ measurement_matrix_zero.conjugate().transpose() @ collapsed_zero # type: ignore
        one_probability = self._state_vector.conjugate().transpose() @ measurement_matrix_one.conjugate().transpose() @ collapsed_one # type: ignore
        # Dividing each probability by their sum gets the sum of both resulting probabilities (closer) to 1    
        sum_of_probabilities = zero_probability + one_probability
        zero_probability = round(zero_probability/sum_of_probabilities, QuantumState.decimal_places) # type: ignore
        one_probability = round(one_probability/sum_of_probabilities, QuantumState.decimal_places) # type: ignore
        dice = random.random()
        if dice < zero_probability:
            self._state_vector = collapsed_zero
            bit = 0
        else:
            self._state_vector = collapsed_one
            bit = 1
        self._state_vector = self._state_vector/np.linalg.norm(self._state_vector)
        new_wire = []
        for i in range(0, self._num_qubits):
            if (i+1) == qubit: 
                new_wire.append(bit)
            else:
                new_wire.append("|")
        self._update_circuit(new_wire)
        return bit

    @validate_qubit
    def X(self, qubit : int):
        '''
        Apply the X gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(X_matrix, "X", qubit)
        return self

    @validate_qubit
    def Y(self, qubit : int):
        '''
        Apply the Y gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(Y_matrix, "Y", qubit)
        return self

    @validate_qubit
    def Z(self, qubit : int):
        '''
        Apply the Z gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(Z_matrix, "Z", qubit)
        return self

    @validate_qubit
    def H(self, qubit : int):
        '''
        Apply the H gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(H_matrix, "H", qubit)
        return self

    @validate_qubit
    def P(self, qubit : int):
        '''
        Apply the P gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(P_matrix, "P", qubit)
        return self

    @validate_qubit
    def T(self, qubit : int):
        '''
        Apply the T gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(T_matrix, "T", qubit)
        return self

    @validate_control_target
    def CNOT(self, control : int, target : int):
        '''
        Apply the CNOT gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(X_matrix, "X", control, target)
        return self

    @validate_control_target
    def C_Y(self, control : int, target : int):
        self._apply_cgate(Y_matrix, "Y", control, target)
        return self

    @validate_control_target
    def C_Z(self, control : int, target : int):
        self._apply_cgate(Z_matrix, "Z", control, target)
        return self

    @validate_control_target
    def C_H(self, control : int, target : int):
        self._apply_cgate(H_matrix, "H", control, target)
        return self

    @validate_control_target
    def C_P(self, control : int, target : int):
        self._apply_cgate(P_matrix, "P", control, target)
        return self

    @validate_control_target
    def C_T(self, control : int, target : int):
        self._apply_cgate(T_matrix, "T", control, target)
        return self

    def swap(self, qubit1 : int, qubit2 : int):
        if (not isinstance(qubit1, int)) or (not (1 <= qubit1 <= self._num_qubits)):
            raise QuantumStateError("'qubit1' must be a positive integer, less than or equal to the number of qubits in the state")
        if (not isinstance(qubit2, int)) or (not (1 <= qubit2 <= self._num_qubits)):
            raise QuantumStateError("'qubit2' must be a positive integer, less than or equal to the number of qubits in the state")
        if qubit1 == qubit2:
            raise QuantumStateError("'qubit1' and 'qubit2' cannot be the same")
        self.CNOT(qubit1, qubit2)
        self.CNOT(qubit2, qubit1)
        self.CNOT(qubit1, qubit2)
        return self

    def Uf2(self, qubit1 : int, qubit2 : int, f : int = random.randint(1, 4)):
        if (not isinstance(qubit1, int)) or (not (1 <= qubit1 <= self._num_qubits)):
            raise QuantumStateError("'qubit1' must be a positive integer, less than or equal to the number of qubits in the state")
        if (not isinstance(qubit2, int)) or (not (1 <= qubit2 <= self._num_qubits)):
            raise QuantumStateError("'qubit2' must be a positive integer, less than or equal to the number of qubits in the state")
        if qubit1 + 1 != qubit2:
            raise QuantumStateError("the value 'qubit1' must be one less than the value 'qubit2'")  
        if f == 1:
            U_f_matrix = U_f_matrix_1
        elif f == 2:
            U_f_matrix = U_f_matrix_2     
        elif f == 3:
            U_f_matrix = U_f_matrix_3
        elif f == 4:
            U_f_matrix = U_f_matrix_4
        else:
            raise QuantumStateError(f"'f' must be an integer from 1 to 4")
        if (qubit1 == 1):
            gate_matrix = U_f_matrix
        else:
            gate_matrix = I_matrix
        for i in range(2, self._num_qubits+1):
            if (i == qubit1):
                gate_matrix = np.kron(gate_matrix, U_f_matrix)
            elif (i == qubit2): 
                continue
            else:
                gate_matrix = np.kron(gate_matrix, I_matrix)
        self._state_vector = gate_matrix @ self._state_vector
        new_wire = []
        for i in range(0, self._num_qubits):
            if (i+1) == qubit1: 
                new_wire.append("<")
            elif (i+1) == qubit2:
                new_wire.append(">")
            else:
                new_wire.append("|")
        self._update_circuit(new_wire) 
        return self