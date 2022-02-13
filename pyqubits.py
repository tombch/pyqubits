import math
import random
import inspect
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


f_const_0 = np.array([
    [1+0j, 0+0j, 0+0j, 0+0j], 
    [0+0j, 1+0j, 0+0j, 0+0j], 
    [0+0j, 0+0j, 1+0j, 0+0j], 
    [0+0j, 0+0j, 0+0j, 1+0j]
]) 


f_const_1 = np.array([
    [0+0j, 1+0j, 0+0j, 0+0j], 
    [1+0j, 0+0j, 0+0j, 0+0j], 
    [0+0j, 0+0j, 0+0j, 1+0j], 
    [0+0j, 0+0j, 1+0j, 0+0j]
])         


f_bal_0 = np.array([
    [1+0j, 0+0j, 0+0j, 0+0j], 
    [0+0j, 1+0j, 0+0j, 0+0j], 
    [0+0j, 0+0j, 0+0j, 1+0j], 
    [0+0j, 0+0j, 1+0j, 0+0j]
])  


f_bal_1 = np.array([
    [1+0j, 0+0j, 0+0j, 0+0j], 
    [0+0j, 1+0j, 0+0j, 0+0j], 
    [0+0j, 0+0j, 0+0j, 1+0j], 
    [0+0j, 0+0j, 1+0j, 0+0j]
])


class QuantumStateError(Exception):
    pass


def validate_qubits(method):
    '''
    This decorator checks that the integer arguments of a `QuantumState` method (which are assumed to be qubits) are valid. 
    '''
    # Define the decorated function
    def wrapped_method(obj, *args, **kwargs):
        arg_names = list(inspect.signature(method).parameters)[1:]
        arg_types = {x : inspect.signature(method).parameters[x].annotation for x in arg_names}
        
        # Validate positional arguments
        for i, qubit in enumerate(args):
            # If the argument type is not an integer, then it is not a qubit argument so can be ignored
            if arg_types[arg_names[i]] == int:
                if (not isinstance(qubit, int)) or (not (1 <= qubit <= obj._num_qubits)):
                    raise QuantumStateError(f"'{arg_names[i]}' must be a positive integer, less than or equal to the number of n in the state")
        
        # Validate keyword arguments
        for i, (name, qubit) in enumerate(kwargs.items()):
            # If the argument type is not an integer, then it is not a qubit argument so can be ignored
            if arg_types[name] == int:
                if (not isinstance(qubit, int)) or (not (1 <= qubit <= obj._num_qubits)):
                    raise QuantumStateError(f"'{name}' must be a positive integer, less than or equal to the number of n in the state")
        
        # Return the original method, with its (now validated) original arguments
        return method(obj, *args, **kwargs)
    
    return wrapped_method


class QuantumState:
    '''
    A class for representing and manipulating multi-qubit states.
    '''
    __slots__ = '_num_qubits', '_num_classical_states', '_state_vector', '_bit', '_circuit' 
    decimal_places = 16 # Rounding accuracy
    max_visible_circuit = 200

    def __init__(self, n : int = 1):
        if (not isinstance(n, int)) or n < 1:
            raise QuantumStateError("'n' must be a positive integer") 
        self._num_qubits = n
        self._num_classical_states = 2**self._num_qubits
        # A state vector is created with random values from the unit circle around the origin
        self._state_vector = (2 * np.random.random(self._num_classical_states) - 1) + ( 2 * np.random.random(self._num_classical_states) - 1) * 1j # complex128
        # The vector is normalised
        self._state_vector = self._state_vector / np.linalg.norm(self._state_vector)
        self._bit = None
        self._init_circuit()

    @classmethod
    def from_bits(cls, bits : str):
        if not isinstance(bits, str) or [c for c in bits if c != '0' and c != '1']:
            raise QuantumStateError(f"'bits' must be a binary number string")
        obj = cls()
        obj._num_qubits = len(bits)
        obj._num_classical_states = 2**obj._num_qubits
        obj._state_vector = np.zeros(obj._num_classical_states) + np.zeros(obj._num_classical_states) * 1j # complex128
        obj._state_vector[int(bits, 2)] = 1
        obj._bit = None
        obj._init_circuit()
        return obj

    # TODO: Validate array
    @classmethod
    def from_vector(cls, vector : np.ndarray):
        '''
        Construct a `QuantumState` object from a pre-existing NumPy array.
        '''
        obj = cls()
        obj._num_qubits = int(math.log2(len(vector)))
        obj._num_classical_states = 2**obj._num_qubits
        obj._state_vector = vector
        obj._bit = None
        obj._init_circuit()
        return obj

    def _init_circuit(self):
        # Initialise circuit
        self._circuit = []
        for i in range(0, self._num_qubits):
            qubit_wire = []
            qubit_wire.append(str((i + 1) % 10))
            self._circuit.append(qubit_wire)
            self._circuit.append([' ']) # The empty space between qubit wires
        self._advance_circuit()

    def _advance_circuit(self):
        for i, qubit_wire in enumerate(self._circuit):
            if (i % 2) == 0:
                # We are on a qubit wire, and not empty space
                qubit_wire.extend(['-', '-', '-'])
            else: 
                qubit_wire.extend([' ', ' ', ' '])

    def _update_circuit(self, operations):
        for qubit_wire, operation in zip(self._circuit, operations):
            if isinstance(operation, list):
                qubit_wire.extend(operation)
            else:
                qubit_wire.append(operation)
        self._advance_circuit()

    def __mul__(self, s):
        joined = QuantumState()
        joined._num_qubits = self._num_qubits + s._num_qubits
        joined._num_classical_states = 2**joined._num_qubits
        joined._state_vector = np.kron(self._state_vector, s._state_vector)
        joined._bit = None
        joined._init_circuit()
        remaining_circuit = []
        circuit_length_diff = len(self._circuit[0]) - len(s._circuit[0])
        for i in range(len(self._circuit)):
            if (i % 2) == 0:
                # We are on a qubit wire, and not empty space
                wire = list(self._circuit[i])
                if circuit_length_diff < 0:
                    wire.extend(['-'] * abs(circuit_length_diff))
                remaining_circuit.append(wire[4:])
            else: 
                wire = list(self._circuit[i])
                if circuit_length_diff < 0:
                    wire.extend([' '] * abs(circuit_length_diff))
                remaining_circuit.append(wire[4:])
        for i in range(len(s._circuit)):
            if (i % 2) == 0:
                # We are on a qubit wire, and not empty space
                wire = list(s._circuit[i])
                if circuit_length_diff > 0:
                    wire.extend(['-'] * circuit_length_diff)
                remaining_circuit.append(wire[4:])
            else:
                wire = list(s._circuit[i])
                if circuit_length_diff > 0:
                    wire.extend([' '] * circuit_length_diff)
                remaining_circuit.append(wire[4:])
        for i, wire in enumerate(remaining_circuit):
            joined._circuit[i].extend(wire)
        return joined

    # TODO: Doesn't always print two basis vectors per line
    def __str__(self):
        amplitudes = []
        for amp in self._state_vector: # type: ignore - genuinely nothing I can do here. Thinks np.random.random makes a complex number instead of an array
            amplitudes.append(str(round(amp, 5))[1:-1].replace(' ', '').replace('+', ' + ').replace('-', ' - ').strip())
        longest_amp = 0
        for amp in amplitudes:
            if len(amp) > longest_amp:
                longest_amp = len(amp)
        for i, amp in enumerate(amplitudes):
            diff = longest_amp - len(amp)
            if diff != 0:
                amplitudes[i] = (' ' * diff) + amplitudes[i]
        basis = [bin(i)[2:].zfill(self._num_qubits) for i in range(self._num_classical_states)]
        state_string = ''
        first_non_zero = True
        for i, (amplitude, vector) in enumerate(zip(amplitudes, basis)):
            if self._state_vector[i] != 0: # type: ignore
                state_string += f"{'=' if first_non_zero else '+'} ({amplitude}) |{vector}> {chr(10) if (i + 1) % 2 == 0 else ''}"
                first_non_zero = False
        return state_string[:-1] if state_string[-1] == '\n' else state_string

    def __repr__(self):
        return 'QuantumState(' + f"\n{' ' * (len('QuantumState(') - len('array('))}".join(repr(self._state_vector)[len('array('):-1].split('\n')) + ')'

    @property
    def vector(self):
        '''
        NumPy array of the state vector.
        '''
        return self._state_vector

    # TODO (maybe): Some probabilities are displayed as the same due to rounding, but have a different number of '=' chars
    @property
    def dist(self):
        '''
        Printable discrete probability distribution. 
        
        The distribution shows the probability of each outcome if every qubit in the quantum state is measured.
        '''
        def get_dist(state_vector):
            dist_string = ''
            gen_classical_states = ((i, bin(i)[2:].zfill(self._num_qubits)) for i in range(self._num_classical_states))
            for i, bin_i in gen_classical_states:
                dist_string += f"{bin_i}\t{round(abs(state_vector[i])**2, 2)}\t|{'=' * int(round(50 * abs(state_vector[i])**2))}\n"
            return dist_string[:-1]
        return get_dist(self._state_vector)

    @property
    def circuit(self):
        '''
        Printable quantum circuit diagram. 
        
        The quantum circuit shows all actions that have been carried out on the quantum state.
        '''
        circuit_string = ''
        if len(self._circuit[0]) - 4 > QuantumState.max_visible_circuit:
            for i in range(len(self._circuit) - 1): # We don't want to print the last line of empty space
                circuit_string += self._circuit[i][0] + '...'
                circuit_string += ''.join(self._circuit[i][4 + (len(self._circuit[0]) - QuantumState.max_visible_circuit - 4):]) + '\n'
        else:
            for i in range(len(self._circuit) - 1): # We don't want to print the last line of empty space
                circuit_string += ''.join(self._circuit[i]) + '\n'
        return circuit_string[:-1]
    
    @property
    def all_circuit(self):
        '''
        Printable quantum circuit diagram (in full). 
        
        The quantum circuit shows all actions that have been carried out on the quantum state.
        '''
        circuit_string = ''
        for i in range(len(self._circuit) - 1): # We don't want to print the last line of empty space
            circuit_string += ''.join(self._circuit[i]) + '\n'
        return circuit_string[:-1]

    @property
    def bit(self):
        '''
        The outcome of the latest measurement of the quantum state.
        '''
        return self._bit

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
        operations = []
        for i in range(0, self._num_qubits):
            if (i+1) == qubit: 
                operations.append(gate_char)
            else:
                operations.append('-')
            operations.append(' ') # Empty space between qubit wires
        self._update_circuit(operations)

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
        operations = []
        inbetween_control_target = False
        for i in range(0, self._num_qubits):
            if (i+1) == control:
                operations.append('O')
                inbetween_control_target = not inbetween_control_target
            elif (i+1) == target:
                operations.append(gate_char)
                inbetween_control_target = not inbetween_control_target
            else:
                if inbetween_control_target:
                    operations.append('|')
                else:
                    operations.append('-')
            if inbetween_control_target:
                operations.append('|') # We have a vertical wire connecting the control and target
            else:
                operations.append(' ') # Empty space between qubit wires
        self._update_circuit(operations)

    @validate_qubits
    def measure(self, qubit : int):
        '''
        Measure a `qubit` within the quantum state.
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
        rand = random.random()
        if rand < zero_probability:
            self._state_vector = collapsed_zero
            bit = 0
        else:
            self._state_vector = collapsed_one
            bit = 1
        self._state_vector = self._state_vector/np.linalg.norm(self._state_vector)
        operations = []
        for i in range(0, self._num_qubits):
            if (i+1) == qubit: 
                operations.append(str(bit))
            else:
                operations.append("-")
            operations.append(' ') # Empty space between qubit wires
        self._update_circuit(operations)
        self._bit = bit
        return self

    @validate_qubits
    def X(self, qubit : int):
        '''
        Apply the X gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(X_matrix, "X", qubit)
        return self

    @validate_qubits
    def Y(self, qubit : int):
        '''
        Apply the Y gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(Y_matrix, "Y", qubit)
        return self

    @validate_qubits
    def Z(self, qubit : int):
        '''
        Apply the Z gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(Z_matrix, "Z", qubit)
        return self

    @validate_qubits
    def H(self, qubit : int):
        '''
        Apply the H gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(H_matrix, "H", qubit)
        return self

    @validate_qubits
    def P(self, qubit : int):
        '''
        Apply the P gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(P_matrix, "P", qubit)
        return self

    @validate_qubits
    def T(self, qubit : int):
        '''
        Apply the T gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(T_matrix, "T", qubit)
        return self

    @validate_qubits
    def CNOT(self, control : int, target : int):
        '''
        Apply the CNOT (controlled-X) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(X_matrix, "X", control, target)
        return self

    @validate_qubits
    def CY(self, control : int, target : int):
        '''
        Apply the CY (controlled-Y) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(Y_matrix, "Y", control, target)
        return self

    @validate_qubits
    def CZ(self, control : int, target : int):
        '''
        Apply the CZ (controlled-Z) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(Z_matrix, "Z", control, target)
        return self

    @validate_qubits
    def CH(self, control : int, target : int):
        '''
        Apply the CH (controlled-H) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(H_matrix, "H", control, target)
        return self

    @validate_qubits
    def CP(self, control : int, target : int):
        '''
        Apply the CP (controlled-P) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(P_matrix, "P", control, target)
        return self

    @validate_qubits
    def CT(self, control : int, target : int):
        '''
        Apply the CT (controlled-T) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(T_matrix, "T", control, target)
        return self

    @validate_qubits
    def SWAP(self, qubit1 : int, qubit2 : int):
        '''
        Apply the SWAP gate to `qubit1` and `qubit2` within the quantum state.

        The SWAP gate is (currently) implemented through CNOT gates.
        '''
        if qubit1 == qubit2:
            raise QuantumStateError("'qubit1' and 'qubit2' cannot be the same")
        self.CNOT(qubit1, qubit2)
        self.CNOT(qubit2, qubit1)
        self.CNOT(qubit1, qubit2)
        return self

    @validate_qubits
    def Uf2(self, qubit1 : int, qubit2 : int, f : str):
        if qubit1 + 1 != qubit2:
            raise QuantumStateError("'qubit1' must be one less than 'qubit2'")  
        if f == 'const0':
            U_f_matrix = f_const_0
        elif f == 'const1':
            U_f_matrix = f_const_1  
        elif f == 'bal0':
            U_f_matrix = f_bal_0
        elif f == 'bal1':
            U_f_matrix = f_bal_1
        else:
            raise QuantumStateError(f"invalid choice of 'f'")
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
        operations = []
        inbetween_gate = False
        for i in range(0, self._num_qubits):
            if (i+1) == qubit1: 
                inbetween_gate = not inbetween_gate
                operations.append(['|', '-', '-', '-', '|']) 
            elif (i+1) == qubit2:
                inbetween_gate = not inbetween_gate
                operations.append(['|', '-', '-', '-', '|'])
            else:
                operations.append(['-', '-', '-', '-', '-'])    
            if inbetween_gate:
                operations.append(['|', 'U', 'f', '2', '|'])
            else:
                operations.append([' ', ' ', ' ', ' ', ' ']) # Empty space between qubit wires
        self._update_circuit(operations) 
        return self