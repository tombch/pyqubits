import math
import random
import numpy as np
from numbers import Number
from pyqubits.utils import PyQubitsError, validate_qubits, memkron
from pyqubits.gates import (
    zero_matrix,
    one_matrix,
    I_matrix,
    X,
    Y,
    Z,
    H,
    P,
    T,
    CNOT,
    CY,
    CZ,
    CH,
    CP,
    CT,
    f2,
)


class QuantumState:
    """
    A class for simulating multi-qubit states.
    """

    __slots__ = (
        "_num_qubits",
        "_num_classical_states",
        "_state_vector",
        "_bit",
        "_circuit",
    )
    # Rounding accuracy
    decimal_places = 16
    # How many characters (length-wise) of the circuit can be printed
    max_visible_circuit = 200

    def __init__(self, n: int = 1):
        if (not isinstance(n, int)) or n < 1:
            raise PyQubitsError("'n' must be a positive integer")
        self._num_qubits = n
        self._num_classical_states = 2**self._num_qubits
        # A state vector is created with random values from the unit circle around the origin
        self._state_vector = np.asarray(
            (2 * np.random.random(self._num_classical_states) - 1)
            + (2 * np.random.random(self._num_classical_states) - 1) * 1j
        )  # complex128
        # The vector is normalised
        self._state_vector = self._state_vector / np.linalg.norm(self._state_vector)
        self._bit = None
        self._init_circuit()

    @classmethod
    def from_bits(cls, bits: str):
        if not isinstance(bits, str) or any([not c in "01q" for c in bits]):
            raise PyQubitsError(f"'bits' must be a binary number string")
        obj = cls()
        for i, c in enumerate(bits):
            obj_ = cls()
            if c == "0":
                # Create the zero qubit
                obj_._state_vector = np.zeros(2) + np.zeros(2) * 1j  # complex128
                obj_._state_vector[0] = 1
            elif c == "1":
                # Create the one qubit
                obj_._state_vector = np.zeros(2) + np.zeros(2) * 1j  # complex128
                obj_._state_vector[-1] = 1
            else:
                # c == 'q'
                # Therefore, create a random qubit
                obj_._state_vector = np.asarray(
                    (2 * np.random.random(2) - 1) + (2 * np.random.random(2) - 1) * 1j
                )  # complex128
                obj_._state_vector = obj_._state_vector / np.linalg.norm(
                    obj_._state_vector
                )
            if i == 0:
                # Set the state equal to this qubit, because it is the first one
                obj = obj_
            else:
                # This qubit is not the first, so combine it with the state
                obj *= obj_
        return obj

    @classmethod
    def from_vector(cls, vector: np.ndarray):
        """
        Construct a `QuantumState` object from a vector (this could be a NumPy array or a list).
        The vector is normalised to ensure it is a valid state.
        """
        if not isinstance(vector, np.ndarray) and not isinstance(vector, list):
            raise PyQubitsError("'vector' must be either a NumPy array or a list")
        if len(vector) <= 1 or int(math.log2(len(vector))) != math.log2(len(vector)):
            # Only when the length of the vector is a power of two will its log2 be an integer
            # And in this case int(length) will be equal to length
            raise PyQubitsError(
                "The vector's length must be greater than one, and can only be a power of two"
            )
        for x in vector:
            if not isinstance(x, Number):
                raise PyQubitsError(
                    f"Elements of 'vector' must be numbers. Encountered invalid type: {type(x).__name__}"
                )
        # The state vector is created
        state_vector = np.asarray(vector, dtype="complex128")
        # The vector is normalised
        state_vector = state_vector / np.linalg.norm(state_vector)
        # The QuantumState is created with the state vector
        obj = cls()
        obj._num_qubits = int(math.log2(len(state_vector)))
        obj._num_classical_states = 2**obj._num_qubits
        obj._state_vector = state_vector
        obj._bit = None
        obj._init_circuit()
        return obj

    def _init_circuit(self):
        # Initialise circuit
        self._circuit = []
        for i in range(0, self._num_qubits):
            qubit_wire = []
            qubit_wire.append(str((i + 1) % 10))
            # Add the wire to the circuit
            self._circuit.append(qubit_wire)
            # Add the empty space between wires to the circuit
            self._circuit.append([" "])
        self._advance_circuit()

    def _advance_circuit(self):
        # Adds the space/wires between qubit operations in a circuit
        for i, qubit_wire in enumerate(self._circuit):
            if (i % 2) == 0:
                # We are on a qubit wire
                qubit_wire.extend(["-", "-", "-"])
            else:
                # We are on empty space
                qubit_wire.extend([" ", " ", " "])

    def _update_circuit(self, start_qubit, gate_rep):
        new_circuit = []
        gate_length = len(gate_rep[0])
        i = 0
        while i < self._num_qubits:
            if (i + 1) == start_qubit:
                for row in gate_rep:
                    new_circuit.append(row)
                new_circuit.append([" "] * gate_length)
                i += int((len(gate_rep) + 1) / 2)
            else:
                new_circuit.append(["-"] * gate_length)
                new_circuit.append([" "] * gate_length)
                i += 1
        for current_wire, new_wire in zip(self._circuit, new_circuit):
            if isinstance(new_wire, list):
                current_wire.extend(new_wire)
            else:
                current_wire.append(new_wire)
        self._advance_circuit()

    def __mul__(self, s):
        joined = QuantumState()
        joined._num_qubits = self._num_qubits + s._num_qubits
        joined._num_classical_states = 2**joined._num_qubits
        joined._state_vector = np.kron(self._state_vector, s._state_vector)
        joined._bit = None
        joined._init_circuit()
        remaining_circuit = []
        # Difference in number of columns in the circuits
        circuit_length_diff = len(self._circuit[0]) - len(s._circuit[0])
        # For each row in the self state's circuit
        for i in range(len(self._circuit)):
            if (i % 2) == 0:
                # We are on a qubit wire, and not empty space
                wire = list(self._circuit[i])
                if circuit_length_diff < 0:
                    # The length of the self state is less than the other state
                    # So the self state's circuit must be extended by the difference
                    wire.extend(["-"] * abs(circuit_length_diff))
                # We append the remaining 4 items onward
                # This is because init_circuit already has the first 4
                remaining_circuit.append(wire[4:])
            else:
                # We are on empty space
                space = list(self._circuit[i])
                if circuit_length_diff < 0:
                    space.extend([" "] * abs(circuit_length_diff))
                remaining_circuit.append(space[4:])
        # For each row in the other state's circuit
        for i in range(len(s._circuit)):
            if (i % 2) == 0:
                # We are on a qubit wire, and not empty space
                wire = list(s._circuit[i])
                if circuit_length_diff > 0:
                    # The length of the self state is greater than the other state
                    # So the other state's circuit must be extended by the difference
                    wire.extend(["-"] * circuit_length_diff)
                # We append the remaining 4 items onward
                # This is because init_circuit already has the first 4
                remaining_circuit.append(wire[4:])
            else:
                # We are on empty space
                space = list(s._circuit[i])
                if circuit_length_diff > 0:
                    space.extend([" "] * circuit_length_diff)
                remaining_circuit.append(space[4:])
        # Add the rest of the circuit to the new joint circuit
        for i, row in enumerate(remaining_circuit):
            joined._circuit[i].extend(row)
        return joined

    def __str__(self):
        amplitudes = []
        for amp in self._state_vector:
            amplitudes.append(
                str(amp)
                .replace("(", "")
                .replace(")", "")
                .replace(" ", "")
                .replace("+", " + ")
                .replace("-", " - ")
                .replace("e - ", "e-")
                .strip()
            )
        longest_amp = 0
        for amp in amplitudes:
            if len(amp) > longest_amp:
                longest_amp = len(amp)
        for i, amp in enumerate(amplitudes):
            diff = longest_amp - len(amp)
            if diff != 0:
                amplitudes[i] = (" " * diff) + amplitudes[i]
        basis = [
            bin(i)[2:].zfill(self._num_qubits)
            for i in range(self._num_classical_states)
        ]
        state_string = ""
        first_non_zero = True
        first_on_line = True
        for i, (amplitude, vector) in enumerate(zip(amplitudes, basis)):
            if self._state_vector[i] != 0:
                state_string += f"{'=' if first_non_zero else '+'} ({amplitude}) |{vector}> {chr(10) if not first_on_line else ''}"
                first_non_zero = False
                first_on_line = not first_on_line
        return state_string[:-1] if state_string[-1] == "\n" else state_string

    def __repr__(self):
        return (
            "QuantumState("
            + f"\n{' ' * (len('QuantumState(') - len('array('))}".join(
                repr(self._state_vector)[len("array(") : -1].split("\n")
            )
            + ")"
        )

    @property
    def vector(self):
        """
        NumPy array of the state vector.
        """
        return self._state_vector

    @property
    def dist(self):
        """
        Printable discrete probability distribution.

        The distribution shows the probability of each outcome if every qubit in the quantum state is measured.
        """
        dist_string = ""
        gen_classical_states = (
            (i, bin(i)[2:].zfill(self._num_qubits))
            for i in range(self._num_classical_states)
        )
        for i, bin_i in gen_classical_states:
            rounded_probability = round(abs(self._state_vector[i]) ** 2, 2)
            dist_string += f"{bin_i}\t{rounded_probability}\t|{'=' * int(100 * rounded_probability)}\n"  # type: ignore
        return dist_string[:-1]

    @property
    def circuit(self):
        """
        Printable quantum circuit diagram.

        The quantum circuit shows all actions that have been carried out on the quantum state.
        """
        circuit_string = ""
        if len(self._circuit[0]) - 4 > QuantumState.max_visible_circuit:
            for i in range(
                len(self._circuit) - 1
            ):  # We don't want to print the last line of empty space
                circuit_string += self._circuit[i][0] + "..."
                circuit_string += (
                    "".join(
                        self._circuit[i][
                            4
                            + (
                                len(self._circuit[0])
                                - QuantumState.max_visible_circuit
                                - 4
                            ) :
                        ]
                    )
                    + "\n"
                )
        else:
            for i in range(
                len(self._circuit) - 1
            ):  # We don't want to print the last line of empty space
                circuit_string += "".join(self._circuit[i]) + "\n"
        return circuit_string[:-1]

    @property
    def all_circuit(self):
        """
        Printable quantum circuit diagram (in full).

        The quantum circuit shows all actions that have been carried out on the quantum state.
        """
        circuit_string = ""
        for i in range(
            len(self._circuit) - 1
        ):  # We don't want to print the last line of empty space
            circuit_string += "".join(self._circuit[i]) + "\n"
        return circuit_string[:-1]

    @property
    def bit(self):
        """
        The outcome of the latest measurement of the quantum state.
        """
        return self._bit

    def _apply_gate(self, *args, gate):
        gates = []
        gate_sizes = []
        gate_at_pos = []
        gate_num = 0
        for i in range(1, self._num_qubits + 1):
            if i == args[0]:  # First qubit
                gates.append(gate)
                gate_sizes.append(len(gate))
                gate_at_pos.append(gate_num)
            elif (
                i == args[-1]
            ):  # Last qubit, or in the case of len(args) = 1, also the first qubit
                gate_at_pos.append(gate_num)
                gate_num += 1
            else:
                gates.append(
                    np.pad(I_matrix, (0, len(gate) - len(I_matrix)), mode="constant")
                )
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
                bin_list.append(
                    int(current_bin[position : position + num_qubits_for_gate], base=2)
                )
                position += num_qubits_for_gate
            binary_values.append(bin_list)
        gates = np.asarray(gates)
        binary_values = np.asarray(binary_values)
        self._state_vector = np.asarray(
            memkron(gates, self._state_vector, binary_values)
        )

    def _apply_cgate(self, control, target, gate):
        gates_a = []
        gates_b = []
        for i in range(1, self._num_qubits + 1):
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
        binary_values = np.asarray(
            [
                [int(x) for x in bin(i)[2:].zfill(self._num_qubits)]
                for i in range(self._num_classical_states)
            ]
        )
        state_vector_a = np.asarray(memkron(gates_a, self._state_vector, binary_values))
        state_vector_b = np.asarray(memkron(gates_b, self._state_vector, binary_values))
        self._state_vector = np.add(state_vector_a, state_vector_b)

    def _apply_measure(self, qubit):
        gates_zero = []
        gates_one = []
        for i in range(1, self._num_qubits + 1):
            if i == qubit:
                gates_zero.append(zero_matrix)
                gates_one.append(one_matrix)
            else:
                gates_zero.append(I_matrix)
                gates_one.append(I_matrix)
        gates_zero = np.asarray(gates_zero)
        gates_one = np.asarray(gates_one)
        binary_values = np.asarray(
            [
                [int(x) for x in bin(i)[2:].zfill(self._num_qubits)]
                for i in range(self._num_classical_states)
            ]
        )
        # Determine measurement vectors
        collapsed_zero = np.asarray(
            memkron(gates_zero, self._state_vector, binary_values)
        )
        collapsed_one = np.asarray(
            memkron(gates_one, self._state_vector, binary_values)
        )
        # Determine probabilities for each measurement
        zero_probability = sum((abs(x) ** 2 for i, x in enumerate(self._state_vector) if binary_values[i][qubit - 1] == 0))  # type: ignore
        one_probability = sum((abs(x) ** 2 for i, x in enumerate(self._state_vector) if binary_values[i][qubit - 1] == 1))  # type: ignore
        # Dividing each probability by their sum gets the sum of both resulting probabilities (closer) to 1
        sum_of_probabilities = zero_probability + one_probability
        zero_probability = round(zero_probability / sum_of_probabilities, QuantumState.decimal_places)  # type: ignore
        one_probability = round(one_probability / sum_of_probabilities, QuantumState.decimal_places)  # type: ignore
        # Collapse the state vector
        rand = random.uniform(0, 1)
        if rand <= zero_probability:
            self._state_vector = collapsed_zero
            bit = 0
        else:
            self._state_vector = collapsed_one
            bit = 1
        # Normalise the state vector and save the measured bit
        self._state_vector = self._state_vector / np.linalg.norm(self._state_vector)
        self._bit = bit

    @validate_qubits
    def measure(self, qubit: int):
        """
        Measure a `qubit` within the quantum state.
        """
        self._apply_measure(qubit)
        self._update_circuit(qubit, [[str(self._bit)]])
        return self

    @validate_qubits
    def X(self, qubit: int):
        """
        Apply the X gate to a `qubit` within the quantum state.
        """
        self._apply_gate(qubit, gate=X.matrix())
        self._update_circuit(qubit, X.gate())
        return self

    @validate_qubits
    def Y(self, qubit: int):
        """
        Apply the Y gate to a `qubit` within the quantum state.
        """
        self._apply_gate(qubit, gate=Y.matrix())
        self._update_circuit(qubit, Y.gate())
        return self

    @validate_qubits
    def Z(self, qubit: int):
        """
        Apply the Z gate to a `qubit` within the quantum state.
        """
        self._apply_gate(qubit, gate=Z.matrix())
        self._update_circuit(qubit, Z.gate())
        return self

    @validate_qubits
    def H(self, qubit: int):
        """
        Apply the H gate to a `qubit` within the quantum state.
        """
        self._apply_gate(qubit, gate=H.matrix())
        self._update_circuit(qubit, H.gate())
        return self

    @validate_qubits
    def P(self, qubit: int):
        """
        Apply the P gate to a `qubit` within the quantum state.
        """
        self._apply_gate(qubit, gate=P.matrix())
        self._update_circuit(qubit, P.gate())
        return self

    @validate_qubits
    def T(self, qubit: int):
        """
        Apply the T gate to a `qubit` within the quantum state.
        """
        self._apply_gate(qubit, gate=T.matrix())
        self._update_circuit(qubit, T.gate())
        return self

    @validate_qubits
    def CNOT(self, control: int, target: int):
        """
        Apply the CNOT (controlled-X) gate to a `control` qubit and `target` qubit within the quantum state.
        """
        if control == target:
            raise PyQubitsError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, CNOT.matrix())
        self._update_circuit(min(control, target), CNOT.gate(control, target))
        return self

    @validate_qubits
    def CY(self, control: int, target: int):
        """
        Apply the CY (controlled-Y) gate to a `control` qubit and `target` qubit within the quantum state.
        """
        if control == target:
            raise PyQubitsError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, CY.matrix())
        self._update_circuit(min(control, target), CY.gate(control, target))
        return self

    @validate_qubits
    def CZ(self, control: int, target: int):
        """
        Apply the CZ (controlled-Z) gate to a `control` qubit and `target` qubit within the quantum state.
        """
        if control == target:
            raise PyQubitsError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, CZ.matrix())
        self._update_circuit(min(control, target), CZ.gate(control, target))
        return self

    @validate_qubits
    def CH(self, control: int, target: int):
        """
        Apply the CH (controlled-H) gate to a `control` qubit and `target` qubit within the quantum state.
        """
        if control == target:
            raise PyQubitsError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, CH.matrix())
        self._update_circuit(min(control, target), CH.gate(control, target))
        return self

    @validate_qubits
    def CP(self, control: int, target: int):
        """
        Apply the CP (controlled-P) gate to a `control` qubit and `target` qubit within the quantum state.
        """
        if control == target:
            raise PyQubitsError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, CP.matrix())
        self._update_circuit(min(control, target), CP.gate(control, target))
        return self

    @validate_qubits
    def CT(self, control: int, target: int):
        """
        Apply the CT (controlled-T) gate to a `control` qubit and `target` qubit within the quantum state.
        """
        if control == target:
            raise PyQubitsError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, CT.matrix())
        self._update_circuit(min(control, target), CT.gate(control, target))
        return self

    @validate_qubits
    def f2(self, qubit1: int, qubit2: int, f: str):
        if qubit1 + 1 != qubit2:
            raise PyQubitsError("'qubit1' must be one less than 'qubit2'")
        if not f in ["const0", "const1", "bal0", "bal1"]:
            raise PyQubitsError(f"invalid choice of 'f'")

        self._apply_gate(qubit1, qubit2, gate=f2.matrix(f))
        self._update_circuit(qubit1, f2.gate())
        return self

    @validate_qubits
    def SWAP(self, qubit1: int, qubit2: int):
        """
        Apply the SWAP gate to `qubit1` and `qubit2` within the quantum state.

        The SWAP gate is (currently) implemented through CNOT gates.
        """
        if qubit1 == qubit2:
            raise PyQubitsError("'qubit1' and 'qubit2' cannot be the same")

        self.CNOT(qubit1, qubit2)
        self.CNOT(qubit2, qubit1)
        self.CNOT(qubit1, qubit2)
        return self
