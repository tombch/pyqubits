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

class QuantumState:
    __slots__ = '__num_qubits', '__num_classical_states', '__state_vector', '__num_stages', '__circuit'
    # Decimal place rounding accuracy (rounding occurs before measurement and when printing states)
    decimal_places = 16
    # Width between wires in quantum circuit when displayed
    lane_width = 3

    def __init__(self, qubits : int = 1, vector : str = ''):
        if (not isinstance(qubits, int)) or qubits < 1:
            raise QuantumStateError("'qubits' must be a positive integer")
        
        self.__num_qubits = qubits
        self.__num_classical_states = 2**self.__num_qubits

        if vector:
            if vector.upper() == 'ZERO':
                # The state |00...00>
                self.__state_vector = np.zeros(self.__num_classical_states) + np.zeros(self.__num_classical_states) * 1j
                self.__state_vector[0] = 1
            elif vector.upper() == 'ONE':
                # The state |11...11>
                self.__state_vector = np.zeros(self.__num_classical_states) + np.zeros(self.__num_classical_states) * 1j
                self.__state_vector[-1] = 1
            else:
                raise QuantumStateError(f"'vector' cannot be assigned the value: {vector}")
        else:
            # A state vector is created with random values from the unit circle around the origin
            self.__state_vector = (2*np.random.random(self.__num_classical_states)-1) + (2*np.random.random(self.__num_classical_states)-1) * 1j
            # The vector is normalised
            self.__state_vector = self.__state_vector/np.linalg.norm(self.__state_vector)
        # Initialise circuit
        self.__num_stages = 0
        self.__circuit = []
        lane = []
        for i in range(0, self.__num_qubits):
            lane.append((i + 1) % 10)
        self.__circuit.append(lane)
        self.__circuit.append(self.__empty_circuit_row())

    # def __mul__(self, q): 
    #     # Merge circuits first because this requires using attributes from both objects
    #     diff_in_length = len(self.__circuit) - len(q.circuit)
    #     # q.circuit is longer
    #     if diff_in_length < 0:
    #         joint_circuit_length = len(q.circuit)
    #         for i in range(abs(diff_in_length)):
    #             self.__circuit.append(self.__empty_circuit_row(include_stages=False))
    #     # self.__circuit is longer
    #     elif diff_in_length > 0:
    #         joint_circuit_length = len(self.__circuit)
    #         for i in range(abs(diff_in_length)):
    #             q.circuit.append(q.__empty_circuit_row(include_stages=False))
    #     # The circuits are the same length, so we can take the length of either
    #     else:
    #         joint_circuit_length = len(self.__circuit)
    #     merged_circuit = [""]
    #     for i in range(0, self.__num_qubits + q.__num_qubits):
    #         merged_circuit[0] += f"{(i+1)%10}{' '*QuantumState.lane_width}"
    #     merged_circuit.append(self.__empty_circuit_row(include_stages=False) + q.__empty_circuit_row(current_stage=0))
    #     for i in range(2, joint_circuit_length, 2):
    #         merged_circuit.append(self.__circuit[i] + q.circuit[i])
    #         merged_circuit.append(self.__empty_circuit_row(include_stages=False) + q.__empty_circuit_row(current_stage=int(i/2)))
    #     # Update all attributes to factor in q
    #     self.__num_qubits += q.__num_qubits
    #     self.__num_classical_states = 2**self.__num_qubits
    #     self.__state_vector = np.kron(self.__state_vector, q.__state_vector)
    #     self.__num_stages = max(self.__num_stages, q.__num_stages)
    #     self.__circuit = merged_circuit 
    #     # Delete reference to q
    #     del q
    #     return self

    def vector(self):
        return self.__state_vector

    def state(self):
        def get_state(state_vector):
            state_string = ''
            gen_classical_states = ((i, bin(i)[2:].zfill(self.__num_qubits)) for i in range(self.__num_classical_states))
            first_non_zero = True  
            for i, bin_i in gen_classical_states:
                current_amplitude = round(state_vector[i].real, QuantumState.decimal_places) + round(state_vector[i].imag, QuantumState.decimal_places) * 1j
                if current_amplitude != 0:
                    state_string += f"{'=' if first_non_zero else '+'} {current_amplitude} |{bin_i}>\n"
                    first_non_zero = False
            return state_string[:-1]
        return get_state(self.__state_vector)

    def dist(self):
        def get_dist(state_vector):
            dist_string = ''
            gen_classical_states = ((i, bin(i)[2:].zfill(self.__num_qubits)) for i in range(self.__num_classical_states))
            for i, bin_i in gen_classical_states:
                dist_string += f"{bin_i}\t{round(abs(state_vector[i])**2, 2)}\t|{'=' * int(round(50 * abs(state_vector[i])**2))}\n"
            return dist_string[:-1]
        return get_dist(self.__state_vector)

    def circuit(self):
        circuit_string = ''
        for row in self.__circuit:
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

    def __empty_circuit_row(self):
        lanes = []
        for _ in range(0, self.__num_qubits):
            lanes.append("|")
        lanes.append(self.__num_stages)
        return lanes
    
    def __update_circuit(self, new_wire):
        self.__num_stages += 1
        self.__circuit.append(new_wire)
        self.__circuit.append(self.__empty_circuit_row())

    def measure(self, qubit : int):
        if (not isinstance(qubit, int)) or (not (1 <= qubit <= self.__num_qubits)):
            raise QuantumStateError("'qubit' must be a positive integer, less than or equal to the number of qubits in the state")

        if (qubit == 1):
            measurement_matrix_zero = zero_matrix
            measurement_matrix_one = one_matrix
        else:
            measurement_matrix_zero = I_matrix
            measurement_matrix_one = I_matrix
        for i in range(2, self.__num_qubits+1):
            if (i == qubit):
                measurement_matrix_zero = np.kron(measurement_matrix_zero, zero_matrix)
                measurement_matrix_one = np.kron(measurement_matrix_one, one_matrix)
            else:
                measurement_matrix_zero = np.kron(measurement_matrix_zero, I_matrix)
                measurement_matrix_one = np.kron(measurement_matrix_one, I_matrix)
        collapsed_zero = measurement_matrix_zero @ self.__state_vector
        collapsed_one = measurement_matrix_one @ self.__state_vector
        zero_probability = self.__state_vector.conjugate().transpose() @ measurement_matrix_zero.conjugate().transpose() @ collapsed_zero # type: ignore
        one_probability = self.__state_vector.conjugate().transpose() @ measurement_matrix_one.conjugate().transpose() @ collapsed_one # type: ignore
        # Dividing each probability by their sum gets the sum of both resulting probabilities (closer) to 1    
        sum_of_probabilities = zero_probability + one_probability
        zero_probability = round(zero_probability/sum_of_probabilities, QuantumState.decimal_places) # type: ignore
        one_probability = round(one_probability/sum_of_probabilities, QuantumState.decimal_places) # type: ignore
        dice = random.random()
        if dice < zero_probability:
            self.__state_vector = collapsed_zero
            bit = 0
        else:
            self.__state_vector = collapsed_one
            bit = 1
        self.__state_vector = self.__state_vector/np.linalg.norm(self.__state_vector)
        new_wire = []
        for i in range(0, self.__num_qubits):
            if (i+1) == qubit: 
                new_wire.append(bit)
            else:
                new_wire.append("|")
        self.__update_circuit(new_wire)
        return bit

    def __apply_gate(self, chosen_matrix, gate_char, qubit):
        if (qubit == 1):
            gate_matrix = chosen_matrix
        else:
            gate_matrix = I_matrix
        for i in range(2, self.__num_qubits+1):
            if (i == qubit):
                gate_matrix = np.kron(gate_matrix, chosen_matrix)
            else:
                gate_matrix = np.kron(gate_matrix, I_matrix)
        self.__state_vector = gate_matrix @ self.__state_vector
        new_wire = []
        for i in range(0, self.__num_qubits):
            if (i+1) == qubit: 
                new_wire.append(gate_char)
            else:
                new_wire.append("|")
        self.__update_circuit(new_wire)

    def __apply_cgate(self, chosen_matrix, gate_char, control, target):
        if (control == 1):
            gate_matrix_a = zero_matrix
            gate_matrix_b = one_matrix
        elif (target == 1):
            gate_matrix_a = I_matrix
            gate_matrix_b = chosen_matrix
        else:
            gate_matrix_a = I_matrix
            gate_matrix_b = I_matrix
        for i in range(2, self.__num_qubits+1):
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
        self.__state_vector = gate_matrix @ self.__state_vector
        new_wire = []
        for i in range(0, self.__num_qubits):
            if (i+1) == control: 
                new_wire.append("O")
            elif (i+1) == target:
                new_wire.append(gate_char)
            else:
                new_wire.append("|")
        self.__update_circuit(new_wire)

    def X(self, qubit : int):
        if (not isinstance(qubit, int)) or (not (1 <= qubit <= self.__num_qubits)):
            raise QuantumStateError("'qubit' must be a positive integer, less than or equal to the number of qubits in the state")
        self.__apply_gate(X_matrix, "X", qubit)

    def Y(self, qubit : int):
        if (not isinstance(qubit, int)) or (not (1 <= qubit <= self.__num_qubits)):
            raise QuantumStateError("'qubit' must be a positive integer, less than or equal to the number of qubits in the state")
        self.__apply_gate(Y_matrix, "Y", qubit)

    def Z(self, qubit : int):
        if (not isinstance(qubit, int)) or (not (1 <= qubit <= self.__num_qubits)):
            raise QuantumStateError("'qubit' must be a positive integer, less than or equal to the number of qubits in the state")
        self.__apply_gate(Z_matrix, "Z", qubit)

    def H(self, qubit : int):
        if (not isinstance(qubit, int)) or (not (1 <= qubit <= self.__num_qubits)):
            raise QuantumStateError("'qubit' must be a positive integer, less than or equal to the number of qubits in the state")
        self.__apply_gate(H_matrix, "H", qubit)

    def P(self, qubit : int):
        if (not isinstance(qubit, int)) or (not (1 <= qubit <= self.__num_qubits)):
            raise QuantumStateError("'qubit' must be a positive integer, less than or equal to the number of qubits in the state")
        self.__apply_gate(P_matrix, "P", qubit)

    def T(self, qubit : int):
        if (not isinstance(qubit, int)) or (not (1 <= qubit <= self.__num_qubits)):
            raise QuantumStateError("'qubit' must be a positive integer, less than or equal to the number of qubits in the state")
        self.__apply_gate(T_matrix, "T", qubit)

    def CNOT(self, control : int, target : int):
        if (not isinstance(control, int)) or (not (1 <= control <= self.__num_qubits)):
            raise QuantumStateError("'control' must be a positive integer, less than or equal to the number of qubits in the state")
        if (not isinstance(target, int)) or (not (1 <= target <= self.__num_qubits)):
            raise QuantumStateError("'target' must be a positive integer, less than or equal to the number of qubits in the state")
        if control == target:
            raise QuantumStateError("'control' and 'target' cannot be the same")
        self.__apply_cgate(X_matrix, "X", control, target)

    def C_Y(self, control : int, target : int):
        if (not isinstance(control, int)) or (not (1 <= control <= self.__num_qubits)):
            raise QuantumStateError("'control' must be a positive integer, less than or equal to the number of qubits in the state")
        if (not isinstance(target, int)) or (not (1 <= target <= self.__num_qubits)):
            raise QuantumStateError("'target' must be a positive integer, less than or equal to the number of qubits in the state")
        if control == target:
            raise QuantumStateError("'control' and 'target' cannot be the same")
        self.__apply_cgate(Y_matrix, "Y", control, target)

    def C_Z(self, control : int, target : int):
        if (not isinstance(control, int)) or (not (1 <= control <= self.__num_qubits)):
            raise QuantumStateError("'control' must be a positive integer, less than or equal to the number of qubits in the state")
        if (not isinstance(target, int)) or (not (1 <= target <= self.__num_qubits)):
            raise QuantumStateError("'target' must be a positive integer, less than or equal to the number of qubits in the state")
        if control == target:
            raise QuantumStateError("'control' and 'target' cannot be the same")
        self.__apply_cgate(Z_matrix, "Z", control, target)

    def C_H(self, control : int, target : int):
        if (not isinstance(control, int)) or (not (1 <= control <= self.__num_qubits)):
            raise QuantumStateError("'control' must be a positive integer, less than or equal to the number of qubits in the state")
        if (not isinstance(target, int)) or (not (1 <= target <= self.__num_qubits)):
            raise QuantumStateError("'target' must be a positive integer, less than or equal to the number of qubits in the state")
        if control == target:
            raise QuantumStateError("'control' and 'target' cannot be the same")
        self.__apply_cgate(H_matrix, "H", control, target)

    def C_P(self, control : int, target : int):
        if (not isinstance(control, int)) or (not (1 <= control <= self.__num_qubits)):
            raise QuantumStateError("'control' must be a positive integer, less than or equal to the number of qubits in the state")
        if (not isinstance(target, int)) or (not (1 <= target <= self.__num_qubits)):
            raise QuantumStateError("'target' must be a positive integer, less than or equal to the number of qubits in the state")
        if control == target:
            raise QuantumStateError("'control' and 'target' cannot be the same")
        self.__apply_cgate(P_matrix, "P", control, target)

    def C_T(self, control : int, target : int):
        if (not isinstance(control, int)) or (not (1 <= control <= self.__num_qubits)):
            raise QuantumStateError("'control' must be a positive integer, less than or equal to the number of qubits in the state")
        if (not isinstance(target, int)) or (not (1 <= target <= self.__num_qubits)):
            raise QuantumStateError("'target' must be a positive integer, less than or equal to the number of qubits in the state")
        if control == target:
            raise QuantumStateError("'control' and 'target' cannot be the same")
        self.__apply_cgate(T_matrix, "T", control, target)

    def swap(self, qubit1 : int, qubit2 : int):
        if (not isinstance(qubit1, int)) or (not (1 <= qubit1 <= self.__num_qubits)):
            raise QuantumStateError("'qubit1' must be a positive integer, less than or equal to the number of qubits in the state")
        if (not isinstance(qubit2, int)) or (not (1 <= qubit2 <= self.__num_qubits)):
            raise QuantumStateError("'qubit2' must be a positive integer, less than or equal to the number of qubits in the state")
        if qubit1 == qubit2:
            raise QuantumStateError("'qubit1' and 'qubit2' cannot be the same")
        self.CNOT(qubit1, qubit2)
        self.CNOT(qubit2, qubit1)
        self.CNOT(qubit1, qubit2)

    def Uf2(self, qubit1 : int, qubit2 : int, f : int = random.randint(1, 4)):
        if (not isinstance(qubit1, int)) or (not (1 <= qubit1 <= self.__num_qubits)):
            raise QuantumStateError("'qubit1' must be a positive integer, less than or equal to the number of qubits in the state")
        if (not isinstance(qubit2, int)) or (not (1 <= qubit2 <= self.__num_qubits)):
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
        for i in range(2, self.__num_qubits+1):
            if (i == qubit1):
                gate_matrix = np.kron(gate_matrix, U_f_matrix)
            elif (i == qubit2): 
                continue
            else:
                gate_matrix = np.kron(gate_matrix, I_matrix)
        self.__state_vector = gate_matrix @ self.__state_vector
        new_wire = []
        for i in range(0, self.__num_qubits):
            if (i+1) == qubit1: 
                new_wire.append("<")
            elif (i+1) == qubit2:
                new_wire.append(">")
            else:
                new_wire.append("|")
        self.__update_circuit(new_wire) 