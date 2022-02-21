import math
import random
import inspect
import numpy as np
import numba as nb


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
    [0+0j, 1+0j, 0+0j, 0+0j], 
    [1+0j, 0+0j, 0+0j, 0+0j], 
    [0+0j, 0+0j, 1+0j, 0+0j], 
    [0+0j, 0+0j, 0+0j, 1+0j]
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
        for name, value in zip(arg_names, args):
            # If the argument type is not an integer, then it is not a qubit argument so can be ignored
            if arg_types.get(name) == int:
                if (not isinstance(value, int)) or (not (1 <= value <= obj._num_qubits)):
                    raise QuantumStateError(f"'{name}' must be a positive integer, less than or equal to the number of qubits in the state")
        
        # Validate keyword arguments
        for name, value in kwargs.items():
            # If the argument type is not an integer, then it is not a qubit argument so can be ignored
            if arg_types.get(name) == int:
                if (not isinstance(value, int)) or (not (1 <= value <= obj._num_qubits)):
                    raise QuantumStateError(f"'{name}' must be a positive integer, less than or equal to the number of qubits in the state")
        
        # Return the original method, with its (now validated) original arguments
        return method(obj, *args, **kwargs)
    
    return wrapped_method


# TODO: Test this against previous gate application method
@nb.njit(fastmath=True, parallel=True)
def memkron(gates, state, binary_values):
    '''
    Apply gate(s) to qubit(s) in the state, without creating an enormous matrix in the process
    '''
    new_state = [0+0j for _ in range(len(state))]
    for i in nb.prange(len(state)):
        for j in nb.prange(len(state)):
            val = 1
            for k in range(len(gates)):
                val *= gates[k][binary_values[i][k]][binary_values[j][k]]
            new_state[i] += val * state[j]
    return new_state
# Force compile on import
memkron(np.asarray([I_matrix]), np.asarray([1.+0.j, 0.+0.j]), np.asarray([[0], [1]]))


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

    # TODO: '-' feature in bit strings
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

    # TODO: I have witnessed very small values get displayed as empty components. 
    # E.g. on deutsch algorithm with initial qubits set to 10 instead of 01. 
    # ???
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
        first_on_line = True
        for i, (amplitude, vector) in enumerate(zip(amplitudes, basis)):
            if self._state_vector[i] != 0: # type: ignore
                state_string += f"{'=' if first_non_zero else '+'} ({amplitude}) |{vector}> {chr(10) if not first_on_line else ''}"
                first_non_zero = False
                first_on_line = not first_on_line
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
        dist_string = ''
        gen_classical_states = ((i, bin(i)[2:].zfill(self._num_qubits)) for i in range(self._num_classical_states))
        for i, bin_i in gen_classical_states:
            dist_string += f"{bin_i}\t{round(abs(self._state_vector[i])**2, 2)}\t|{'=' * int(round(50 * abs(self._state_vector[i])**2))}\n" # type: ignore
        return dist_string[:-1]
        
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

    def _apply_gate(self, gate, qubit):
        gates = []
        for i in range(1, self._num_qubits+1):
            if i == qubit:
                gates.append(gate)
            else:
                gates.append(I_matrix)
        gates = np.asarray(gates)
        binary_values = np.asarray([[int(x) for x in bin(i)[2:].zfill(self._num_qubits)] for i in range(self._num_classical_states)])
        self._state_vector = np.asarray(memkron(gates, self._state_vector, binary_values))
    
    def _apply_multigate(self, *args, gate):
        gates = []
        gate_sizes = []
        gate_at_pos = []
        gate_num = 0
        for i in range(1, self._num_qubits+1):
            if i == args[0]: # First qubit
                gates.append(gate)
                gate_sizes.append(len(gate))
                gate_at_pos.append(gate_num)
            elif i == args[-1]: # Last qubit, or in the case of len(args) = 1, also the first qubit
                gate_at_pos.append(gate_num)
                gate_num += 1
            else:
                gates.append(np.pad(I_matrix, (0, len(gate) - len(I_matrix)), mode='constant'))
                gate_sizes.append(len(I_matrix))
                gate_at_pos.append(gate_num)
                gate_num += 1
        binary_values = []
        for i in range(self._num_classical_states):
            position = 0
            bin_list = []
            current_bin = bin(i)[2:].zfill(self._num_qubits)
            while position < self._num_qubits:
                num_qubits_for_gate = int(math.log2(gate_sizes[gate_at_pos[position]]))
                bin_list.append(int(current_bin[position:position+num_qubits_for_gate], base=2))
                position += num_qubits_for_gate
            binary_values.append(bin_list)
        gates = np.asarray(gates)
        binary_values = np.asarray(binary_values)
        self._state_vector = np.asarray(memkron(gates, self._state_vector, binary_values))

    def _apply_cgate(self, gate, control, target):
        gates_a = []
        gates_b = []
        for i in range(1, self._num_qubits+1):
            if i == control:
                gates_a.append(zero_matrix)
                gates_b.append(one_matrix)
            elif i == target:
                gates_a.append(I_matrix)
                gates_b.append(gate)
            else:
                gates_a.append(I_matrix)
                gates_b.append(I_matrix)
        gates_a = np.asarray(gates_a)
        gates_b = np.asarray(gates_b)
        binary_values = np.asarray([[int(x) for x in bin(i)[2:].zfill(self._num_qubits)] for i in range(self._num_classical_states)])
        state_vector_a = np.asarray(memkron(gates_a, self._state_vector, binary_values))
        state_vector_b = np.asarray(memkron(gates_b, self._state_vector, binary_values))
        self._state_vector = np.add(state_vector_a, state_vector_b)

    def _apply_measure(self, qubit):
        gates_zero = []
        gates_one = []
        for i in range(1, self._num_qubits+1):
            if i == qubit:
                gates_zero.append(zero_matrix)
                gates_one.append(one_matrix)
            else:
                gates_zero.append(I_matrix)
                gates_one.append(I_matrix)
        gates_zero = np.asarray(gates_zero)
        gates_one = np.asarray(gates_one)
        binary_values = np.asarray([[int(x) for x in bin(i)[2:].zfill(self._num_qubits)] for i in range(self._num_classical_states)])
        # Determine measurement vectors
        collapsed_zero = np.asarray(memkron(gates_zero, self._state_vector, binary_values))
        collapsed_one = np.asarray(memkron(gates_one, self._state_vector, binary_values))
        # Determine probabilities for each measurement
        zero_probability = sum((abs(x)**2 for i, x in enumerate(self._state_vector) if binary_values[i][qubit-1] == 0)) # type: ignore
        one_probability = sum((abs(x)**2 for i, x in enumerate(self._state_vector) if binary_values[i][qubit-1] == 1)) # type: ignore
        # Dividing each probability by their sum gets the sum of both resulting probabilities (closer) to 1    
        sum_of_probabilities = zero_probability + one_probability
        zero_probability = round(zero_probability/sum_of_probabilities, QuantumState.decimal_places) # type: ignore
        one_probability = round(one_probability/sum_of_probabilities, QuantumState.decimal_places) # type: ignore
        # Collapse the state vector
        rand = random.uniform(0, 1)
        if rand <= zero_probability:
            self._state_vector = collapsed_zero
            bit = 0
        else:
            self._state_vector = collapsed_one
            bit = 1
        # Normalise the state vector and save the measured bit
        self._state_vector = self._state_vector/np.linalg.norm(self._state_vector)
        self._bit = bit

    def _register_gate(self, gate_char, qubit):
        operations = []
        for i in range(0, self._num_qubits):
            if (i+1) == qubit: 
                operations.append(gate_char)
            else:
                operations.append('-')
            operations.append(' ') # Empty space between qubit wires
        self._update_circuit(operations)

    def _register_multigate(self, gate_name, qubit1, qubit2):
        operations = []
        inbetween_gate = False
        for i in range(0, self._num_qubits):
            if (i+1) == qubit1: 
                inbetween_gate = not inbetween_gate
                operations.append(['|'] + ['-'] * len(gate_name) + ['|']) 
            elif (i+1) == qubit2:
                inbetween_gate = not inbetween_gate
                operations.append(['|'] + ['-'] * len(gate_name) + ['|']) 
            else:
                operations.append(['-'] * (len(gate_name) + 2))    
            if inbetween_gate:
                operations.append(['|'] +  [x for x in gate_name] + ['|'])
            else:
                operations.append([' '] * (len(gate_name) + 2)) # Empty space between qubit wires
        self._update_circuit(operations)

    def _register_cgate(self, gate_char, control, target):
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
        self._apply_measure(qubit)
        self._register_gate(str(self._bit), qubit)
        return self

    @validate_qubits
    def X(self, qubit : int):
        '''
        Apply the X gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(X_matrix, qubit)
        self._register_gate('X', qubit)
        return self

    @validate_qubits
    def Y(self, qubit : int):
        '''
        Apply the Y gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(Y_matrix, qubit)
        self._register_gate('Y', qubit)
        return self

    @validate_qubits
    def Z(self, qubit : int):
        '''
        Apply the Z gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(Z_matrix, qubit)
        self._register_gate('Z', qubit)
        return self

    @validate_qubits
    def H(self, qubit : int):
        '''
        Apply the H gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(H_matrix, qubit)
        self._register_gate('H', qubit)
        return self

    @validate_qubits
    def P(self, qubit : int):
        '''
        Apply the P gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(P_matrix, qubit)
        self._register_gate('P', qubit)
        return self

    @validate_qubits
    def T(self, qubit : int):
        '''
        Apply the T gate to a `qubit` within the quantum state.
        '''
        self._apply_gate(T_matrix, qubit)
        self._register_gate('T', qubit)
        return self

    @validate_qubits
    def CNOT(self, control : int, target : int):
        '''
        Apply the CNOT (controlled-X) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(X_matrix, control, target)
        self._register_cgate('X', control, target)
        return self

    @validate_qubits
    def CY(self, control : int, target : int):
        '''
        Apply the CY (controlled-Y) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(Y_matrix, control, target)
        self._register_cgate('Y', control, target)
        return self

    @validate_qubits
    def CZ(self, control : int, target : int):
        '''
        Apply the CZ (controlled-Z) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(Z_matrix, control, target)
        self._register_cgate('Z', control, target)
        return self

    @validate_qubits
    def CH(self, control : int, target : int):
        '''
        Apply the CH (controlled-H) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(H_matrix, control, target)
        self._register_cgate('H', control, target)
        return self

    @validate_qubits
    def CP(self, control : int, target : int):
        '''
        Apply the CP (controlled-P) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(P_matrix, control, target)
        self._register_cgate('P', control, target)
        return self

    @validate_qubits
    def CT(self, control : int, target : int):
        '''
        Apply the CT (controlled-T) gate to a `control` qubit and `target` qubit within the quantum state.
        '''
        self._apply_cgate(T_matrix, control, target)
        self._register_cgate('T', control, target)
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
    def f2(self, qubit1 : int, qubit2 : int, f : str):
        if qubit1 + 1 != qubit2:
            raise QuantumStateError("'qubit1' must be one less than 'qubit2'")  
        if f == 'const0':
            f_matrix = f_const_0
        elif f == 'const1':
            f_matrix = f_const_1  
        elif f == 'bal0':
            f_matrix = f_bal_0
        elif f == 'bal1':
            f_matrix = f_bal_1
        else:
            raise QuantumStateError(f"invalid choice of 'f'")
        self._apply_multigate(qubit1, qubit2, gate=f_matrix)
        self._register_multigate('f2', qubit1, qubit2)
        return self