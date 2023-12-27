from __future__ import annotations
import math
import random
import inspect
from typing import Optional, List
import numpy as np
import numba as nb
from numbers import Number
from . import gates


def validate_qubits(method):
    """
    This decorator checks that the integer arguments of a `QuantumState` method (which are assumed to be qubits) are valid.
    """

    # Define the decorated function
    def wrapped_method(obj, *args, **kwargs):
        arg_names = list(inspect.signature(method).parameters)[1:]
        arg_types = {
            x: inspect.signature(method).parameters[x].annotation for x in arg_names
        }

        # Turn positional arguments into keyword arguments
        for name, value in zip(arg_names, args):
            kwargs[name] = value

        # Validate keyword arguments
        for name, value in kwargs.items():
            # If the argument type is not an integer, then it is not a qubit argument so can be ignored
            if arg_types.get(name) == int:
                if not isinstance(value, int):
                    raise TypeError(f"'{name}' must be an integer")

                if not (1 <= value <= obj.n_qubits):
                    raise ValueError(
                        f"'{name}' must be positive and less than or equal to the number of qubits in the state"
                    )

        # Return the original method, with its (now validated) all keyword arguments
        return method(obj, **kwargs)

    return wrapped_method


@nb.njit(fastmath=True, parallel=True)
def memkron(gate_matrices, state, binary_values):
    """
    Apply gate(s) to qubit(s) in the state, without creating an enormous matrix in the process
    """
    new_state = [0 + 0j for _ in range(len(state))]
    for i in nb.prange(len(state)):
        for j in nb.prange(len(state)):
            val = 1
            for k in range(len(gate_matrices)):
                val *= gate_matrices[k][binary_values[i][k]][binary_values[j][k]]
            new_state[i] += val * state[j]
    return new_state


# Force compile on import
memkron(
    np.asarray([gates.I_matrix]),
    np.asarray([1.0 + 0.0j, 0.0 + 0.0j]),
    np.asarray([[0], [1]]),
)


class QuantumState:
    """
    A class for simulating multi-qubit states.
    """

    __slots__ = (
        "vector",
        "bit",
        "circuit",
        "n_qubits",
        "n_states",
    )
    # Rounding accuracy
    DECIMAL_PLACES = 16

    def __init__(self, n_qubits: int = 1) -> None:
        """
        Construct a `QuantumState` object.

        Args:
            n: The number of qubits in the state. Defaults to 1.
        """

        if not isinstance(n_qubits, int):
            raise TypeError("'n_qubits' must be an integer")

        if n_qubits < 1:
            raise ValueError("'n_qubits' must be positive")

        self.n_qubits = n_qubits
        self.n_states = 2**self.n_qubits
        # A state vector is created with random values from the unit circle around the origin
        self.vector = np.asarray(
            (2 * np.random.random(self.n_states) - 1)
            + (2 * np.random.random(self.n_states) - 1) * 1j
        )  # complex128
        # The vector is normalised
        self.vector = self.vector / np.linalg.norm(self.vector)
        self.bit = None
        self._init_circuit()

    @classmethod
    def from_bits(cls, bits: str) -> QuantumState:
        """
        Construct a `QuantumState` object from a binary number string.

        Args:
            bits: A binary number string, where each character is either '0', '1', or 'q'.
                '0' represents a zero qubit, '1' represents a one qubit, and 'q' represents a random qubit.
        """

        if not isinstance(bits, str):
            raise TypeError("'bits' must be a string")

        if any([not c in "01q" for c in bits]):
            raise ValueError(
                f"'bits' must contain only the characters '0', '1', and 'q'"
            )

        obj = cls()
        for i, c in enumerate(bits):
            obj_ = cls()
            if c == "0":
                # Create the zero qubit
                obj_.vector = np.zeros(2) + np.zeros(2) * 1j  # complex128
                obj_.vector[0] = 1
            elif c == "1":
                # Create the one qubit
                obj_.vector = np.zeros(2) + np.zeros(2) * 1j  # complex128
                obj_.vector[-1] = 1
            else:
                # c == 'q'
                # Therefore, create a random qubit
                obj_.vector = np.asarray(
                    (2 * np.random.random(2) - 1) + (2 * np.random.random(2) - 1) * 1j
                )  # complex128
                obj_.vector = obj_.vector / np.linalg.norm(obj_.vector)
            if i == 0:
                # Set the state equal to this qubit, because it is the first one
                obj = obj_
            else:
                # This qubit is not the first, so combine it with the state
                obj *= obj_
        return obj

    @classmethod
    def from_vector(cls, vector: np.ndarray) -> QuantumState:
        """
        Construct a `QuantumState` object from a vector (this could be a NumPy array or a list).
        The vector is normalised to ensure it is a valid state.

        Args:
            vector: A vector of numbers, where the length is a power of two.
        """

        if not isinstance(vector, np.ndarray) and not isinstance(vector, list):
            raise TypeError("'vector' must be either a NumPy array or a list")

        if len(vector) <= 1 or int(math.log2(len(vector))) != math.log2(len(vector)):
            # Only when the length of the vector is a power of two will its log2 be an integer
            # And in this case int(length) will be equal to length
            raise ValueError(
                "The vector's length must be greater than one, and can only be a power of two"
            )
        for x in vector:
            if not isinstance(x, Number):
                raise TypeError(
                    f"Elements of 'vector' must be numbers. Encountered invalid type: {type(x).__name__}"
                )
        # The state vector is created
        state_vector = np.asarray(vector, dtype="complex128")
        # The vector is normalised
        state_vector = state_vector / np.linalg.norm(state_vector)
        # The QuantumState is created with the state vector
        obj = cls()
        obj.n_qubits = int(math.log2(len(state_vector)))
        obj.n_states = 2**obj.n_qubits
        obj.vector = state_vector
        obj.bit = None
        obj._init_circuit()
        return obj

    def _init_circuit(self) -> None:
        # Initialise circuit
        self.circuit = []
        for i in range(0, self.n_qubits):
            qubit_wire = []
            qubit_wire.append(str((i + 1) % 10))
            # Add the wire to the circuit
            self.circuit.append(qubit_wire)
            # Add the empty space between wires to the circuit
            self.circuit.append([" "])
        self._advance_circuit()

    def _advance_circuit(self) -> None:
        # Adds the space/wires between qubit operations in a circuit
        for i, qubit_wire in enumerate(self.circuit):
            if (i % 2) == 0:
                # We are on a qubit wire
                qubit_wire.extend(["─", "─", "─"])
            else:
                # We are on empty space
                qubit_wire.extend([" ", " ", " "])

    def _update_circuit(self, start_qubit: int, gate_rep: List[List[str]]) -> None:
        new_circuit = []
        gate_length = len(gate_rep[0])
        i = 0
        while i < self.n_qubits:
            if (i + 1) == start_qubit:
                for row in gate_rep:
                    new_circuit.append(row)
                new_circuit.append([" "] * gate_length)
                i += int((len(gate_rep) + 1) / 2)
            else:
                new_circuit.append(["─"] * gate_length)
                new_circuit.append([" "] * gate_length)
                i += 1
        for current_wire, new_wire in zip(self.circuit, new_circuit):
            if isinstance(new_wire, list):
                current_wire.extend(new_wire)
            else:
                current_wire.append(new_wire)
        self._advance_circuit()

    def __mul__(self, qs: QuantumState) -> QuantumState:
        joined = QuantumState()
        joined.n_qubits = self.n_qubits + qs.n_qubits
        joined.n_states = 2**joined.n_qubits
        joined.vector = np.kron(self.vector, qs.vector)
        joined.bit = None
        joined._init_circuit()
        remaining_circuit = []
        # Difference in number of columns in the circuits
        circuit_length_diff = len(self.circuit[0]) - len(qs.circuit[0])
        # For each row in the self state's circuit
        for i in range(len(self.circuit)):
            if (i % 2) == 0:
                # We are on a qubit wire, and not empty space
                wire = list(self.circuit[i])
                if circuit_length_diff < 0:
                    # The length of the self state is less than the other state
                    # So the self state's circuit must be extended by the difference
                    wire.extend(["─"] * abs(circuit_length_diff))
                # We append the remaining 4 items onward
                # This is because init_circuit already has the first 4
                remaining_circuit.append(wire[4:])
            else:
                # We are on empty space
                space = list(self.circuit[i])
                if circuit_length_diff < 0:
                    space.extend([" "] * abs(circuit_length_diff))
                remaining_circuit.append(space[4:])
        # For each row in the other state's circuit
        for i in range(len(qs.circuit)):
            if (i % 2) == 0:
                # We are on a qubit wire, and not empty space
                wire = list(qs.circuit[i])
                if circuit_length_diff > 0:
                    # The length of the self state is greater than the other state
                    # So the other state's circuit must be extended by the difference
                    wire.extend(["─"] * circuit_length_diff)
                # We append the remaining 4 items onward
                # This is because init_circuit already has the first 4
                remaining_circuit.append(wire[4:])
            else:
                # We are on empty space
                space = list(qs.circuit[i])
                if circuit_length_diff > 0:
                    space.extend([" "] * circuit_length_diff)
                remaining_circuit.append(space[4:])
        # Add the rest of the circuit to the new joint circuit
        for i, row in enumerate(remaining_circuit):
            joined.circuit[i].extend(row)
        return joined

    def _apply_gate(self, *args, gate: np.ndarray) -> None:
        gate_matrices = []
        gate_sizes = []
        gate_at_pos = []
        gate_num = 0
        for i in range(1, self.n_qubits + 1):
            if i == args[0]:  # First qubit
                gate_matrices.append(gate)
                gate_sizes.append(len(gate))
                gate_at_pos.append(gate_num)
            elif (
                i == args[-1]
            ):  # Last qubit, or in the case of len(args) = 1, also the first qubit
                gate_at_pos.append(gate_num)
                gate_num += 1
            else:
                gate_matrices.append(
                    np.pad(
                        gates.I_matrix,
                        (0, len(gate) - len(gates.I_matrix)),
                        mode="constant",
                    )
                )
                gate_sizes.append(len(gates.I_matrix))
                gate_at_pos.append(gate_num)
                gate_num += 1
        binary_values = []
        for i in range(self.n_states):
            position = 0
            bin_list = []
            current_bin = bin(i)[2:].zfill(self.n_qubits)
            while position < self.n_qubits:
                num_qubits_for_gate = int(math.log2(gate_sizes[gate_at_pos[position]]))
                bin_list.append(
                    int(current_bin[position : position + num_qubits_for_gate], base=2)
                )
                position += num_qubits_for_gate
            binary_values.append(bin_list)
        gate_matrices = np.asarray(gate_matrices)
        binary_values = np.asarray(binary_values)
        self.vector = np.asarray(memkron(gate_matrices, self.vector, binary_values))

    def _apply_cgate(self, control: int, target: int, gate: np.ndarray) -> None:
        gate_matrices_a = []
        gate_matrices_b = []
        for i in range(1, self.n_qubits + 1):
            if i == control:
                gate_matrices_a.append(gates.zero_matrix)
                gate_matrices_b.append(gates.one_matrix)
            elif i == target:
                gate_matrices_a.append(gates.I_matrix)
                gate_matrices_b.append(gate)
            else:
                gate_matrices_a.append(gates.I_matrix)
                gate_matrices_b.append(gates.I_matrix)
        gate_matrices_a = np.asarray(gate_matrices_a)
        gate_matrices_b = np.asarray(gate_matrices_b)
        binary_values = np.asarray(
            [
                [int(x) for x in bin(i)[2:].zfill(self.n_qubits)]
                for i in range(self.n_states)
            ]
        )
        state_vector_a = np.asarray(
            memkron(gate_matrices_a, self.vector, binary_values)
        )
        state_vector_b = np.asarray(
            memkron(gate_matrices_b, self.vector, binary_values)
        )
        self.vector = np.add(state_vector_a, state_vector_b)

    def _apply_measure(self, qubit: int) -> None:
        gate_matrices_zero = []
        gate_matrices_one = []
        for i in range(1, self.n_qubits + 1):
            if i == qubit:
                gate_matrices_zero.append(gates.zero_matrix)
                gate_matrices_one.append(gates.one_matrix)
            else:
                gate_matrices_zero.append(gates.I_matrix)
                gate_matrices_one.append(gates.I_matrix)
        gate_matrices_zero = np.asarray(gate_matrices_zero)
        gate_matrices_one = np.asarray(gate_matrices_one)
        binary_values = np.asarray(
            [
                [int(x) for x in bin(i)[2:].zfill(self.n_qubits)]
                for i in range(self.n_states)
            ]
        )
        # Determine measurement vectors
        collapsed_zero = np.asarray(
            memkron(gate_matrices_zero, self.vector, binary_values)
        )
        collapsed_one = np.asarray(
            memkron(gate_matrices_one, self.vector, binary_values)
        )
        # Determine probabilities for each measurement
        zero_probability = sum((abs(x) ** 2 for i, x in enumerate(self.vector) if binary_values[i][qubit - 1] == 0))  # type: ignore
        one_probability = sum((abs(x) ** 2 for i, x in enumerate(self.vector) if binary_values[i][qubit - 1] == 1))  # type: ignore
        # Dividing each probability by their sum gets the sum of both resulting probabilities (closer) to 1
        sum_of_probabilities = zero_probability + one_probability
        zero_probability = round(zero_probability / sum_of_probabilities, QuantumState.DECIMAL_PLACES)  # type: ignore
        one_probability = round(one_probability / sum_of_probabilities, QuantumState.DECIMAL_PLACES)  # type: ignore
        # Collapse the state vector
        rand = random.uniform(0, 1)
        if rand <= zero_probability:
            self.vector = collapsed_zero
            bit = 0
        else:
            self.vector = collapsed_one
            bit = 1
        # Normalise the state vector and save the measured bit
        self.vector = self.vector / np.linalg.norm(self.vector)
        self.bit = bit

    @validate_qubits
    def measure(self, qubit: int) -> QuantumState:
        """
        Measure a `qubit` within the quantum state.

        Args:
            qubit: The qubit to measure.

        Returns:
            The `QuantumState` object.
        """

        self._apply_measure(qubit)
        self._update_circuit(qubit, [[str(self.bit)]])
        return self

    @validate_qubits
    def X(self, qubit: int) -> QuantumState:
        """
        Apply the X gate to a `qubit` within the quantum state.

        Args:
            qubit: The qubit to apply the gate to.

        Returns:
            The `QuantumState` object.
        """

        self._apply_gate(qubit, gate=gates.X.matrix())
        self._update_circuit(qubit, gates.X.gate())
        return self

    @validate_qubits
    def Y(self, qubit: int) -> QuantumState:
        """
        Apply the Y gate to a `qubit` within the quantum state.

        Args:
            qubit: The qubit to apply the gate to.

        Returns:
            The `QuantumState` object.
        """

        self._apply_gate(qubit, gate=gates.Y.matrix())
        self._update_circuit(qubit, gates.Y.gate())
        return self

    @validate_qubits
    def Z(self, qubit: int) -> QuantumState:
        """
        Apply the Z gate to a `qubit` within the quantum state.

        Args:
            qubit: The qubit to apply the gate to.

        Returns:
            The `QuantumState` object.
        """

        self._apply_gate(qubit, gate=gates.Z.matrix())
        self._update_circuit(qubit, gates.Z.gate())
        return self

    @validate_qubits
    def H(self, qubit: int) -> QuantumState:
        """
        Apply the H gate to a `qubit` within the quantum state.

        Args:
            qubit: The qubit to apply the gate to.

        Returns:
            The `QuantumState` object.
        """

        self._apply_gate(qubit, gate=gates.H.matrix())
        self._update_circuit(qubit, gates.H.gate())
        return self

    @validate_qubits
    def P(self, qubit: int) -> QuantumState:
        """
        Apply the P gate to a `qubit` within the quantum state.

        Args:
            qubit: The qubit to apply the gate to.

        Returns:
            The `QuantumState` object.
        """

        self._apply_gate(qubit, gate=gates.P.matrix())
        self._update_circuit(qubit, gates.P.gate())
        return self

    @validate_qubits
    def T(self, qubit: int) -> QuantumState:
        """
        Apply the T gate to a `qubit` within the quantum state.

        Args:
            qubit: The qubit to apply the gate to.

        Returns:
            The `QuantumState` object.
        """

        self._apply_gate(qubit, gate=gates.T.matrix())
        self._update_circuit(qubit, gates.T.gate())
        return self

    @validate_qubits
    def CNOT(self, control: int, target: int) -> QuantumState:
        """
        Apply the CNOT (controlled-X) gate to a `control` qubit and `target` qubit within the quantum state.

        Args:
            control: The control qubit.
            target: The target qubit.

        Returns:
            The `QuantumState` object.
        """

        if control == target:
            raise ValueError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, gates.CNOT.matrix())
        self._update_circuit(min(control, target), gates.CNOT.gate(control, target))
        return self

    @validate_qubits
    def CY(self, control: int, target: int) -> QuantumState:
        """
        Apply the CY (controlled-Y) gate to a `control` qubit and `target` qubit within the quantum state.

        Args:
            control: The control qubit.
            target: The target qubit.

        Returns:
            The `QuantumState` object.
        """

        if control == target:
            raise ValueError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, gates.CY.matrix())
        self._update_circuit(min(control, target), gates.CY.gate(control, target))
        return self

    @validate_qubits
    def CZ(self, control: int, target: int) -> QuantumState:
        """
        Apply the CZ (controlled-Z) gate to a `control` qubit and `target` qubit within the quantum state.

        Args:
            control: The control qubit.
            target: The target qubit.

        Returns:
            The `QuantumState` object.
        """

        if control == target:
            raise ValueError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, gates.CZ.matrix())
        self._update_circuit(min(control, target), gates.CZ.gate(control, target))
        return self

    @validate_qubits
    def CH(self, control: int, target: int) -> QuantumState:
        """
        Apply the CH (controlled-H) gate to a `control` qubit and `target` qubit within the quantum state.

        Args:
            control: The control qubit.
            target: The target qubit.

        Returns:
            The `QuantumState` object.
        """

        if control == target:
            raise ValueError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, gates.CH.matrix())
        self._update_circuit(min(control, target), gates.CH.gate(control, target))
        return self

    @validate_qubits
    def CP(self, control: int, target: int) -> QuantumState:
        """
        Apply the CP (controlled-P) gate to a `control` qubit and `target` qubit within the quantum state.

        Args:
            control: The control qubit.
            target: The target qubit.

        Returns:
            The `QuantumState` object.
        """

        if control == target:
            raise ValueError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, gates.CP.matrix())
        self._update_circuit(min(control, target), gates.CP.gate(control, target))
        return self

    @validate_qubits
    def CT(self, control: int, target: int) -> QuantumState:
        """
        Apply the CT (controlled-T) gate to a `control` qubit and `target` qubit within the quantum state.

        Args:
            control: The control qubit.
            target: The target qubit.

        Returns:
            The `QuantumState` object.
        """

        if control == target:
            raise ValueError("'control' and 'target' cannot be the same")

        self._apply_cgate(control, target, gates.CT.matrix())
        self._update_circuit(min(control, target), gates.CT.gate(control, target))
        return self

    @validate_qubits
    def f2(self, qubit_1: int, qubit_2: int, f: str) -> QuantumState:
        if qubit_1 + 1 != qubit_2:
            raise ValueError("'qubit_1' must be one less than 'qubit_2'")
        if not f in ["const0", "const1", "bal0", "bal1"]:
            raise ValueError(f"invalid choice of 'f'")

        self._apply_gate(qubit_1, qubit_2, gate=gates.f2.matrix(f))  # type: ignore
        self._update_circuit(qubit_1, gates.f2.gate())
        return self

    @validate_qubits
    def SWAP(self, qubit_1: int, qubit_2: int) -> QuantumState:
        """
        Apply the SWAP gate to `qubit_1` and `qubit_2` within the quantum state.

        The SWAP gate is (currently) implemented through CNOT gates.

        Args:
            qubit_1: The first qubit.
            qubit_2: The second qubit.

        Returns:
            The `QuantumState` object.
        """

        if qubit_1 == qubit_2:
            raise ValueError("'qubit_1' and 'qubit_2' cannot be the same")

        self.CNOT(qubit_1, qubit_2)
        self.CNOT(qubit_2, qubit_1)
        self.CNOT(qubit_1, qubit_2)
        return self


def print_state(qs: QuantumState) -> None:
    """
    Print the state of a `QuantumState` object.

    Args:
        qs: The `QuantumState` object.
    """

    amplitudes = []
    for amp in qs.vector:
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
    basis = [bin(i)[2:].zfill(qs.n_qubits) for i in range(qs.n_states)]
    state_string = ""
    first_non_zero = True
    first_on_line = True
    for i, (amplitude, vector) in enumerate(zip(amplitudes, basis)):
        if qs.vector[i] != 0:
            state_string += f"{'=' if first_non_zero else '+'} ({amplitude}) |{vector}> {chr(10) if not first_on_line else ''}"
            first_non_zero = False
            first_on_line = not first_on_line

    print(state_string[:-1] if state_string[-1] == "\n" else state_string)


def print_dist(qs: QuantumState) -> None:
    """
    Print the discrete probability distribution of a `QuantumState` object.

    The distribution shows the probability of each outcome if every qubit in the quantum state is measured.

    Args:
        qs: The `QuantumState` object.
    """

    dist_string = ""
    gen_classical_states = (
        (i, bin(i)[2:].zfill(qs.n_qubits)) for i in range(qs.n_states)
    )
    for i, bin_i in gen_classical_states:
        rounded_probability = round(abs(qs.vector[i]) ** 2, 2)
        dist_string += f"{bin_i}\t{rounded_probability}\t|{'=' * int(100 * rounded_probability)}\n"  # type: ignore

    print(dist_string[:-1])


def print_circuit(qs: QuantumState, max_visible: Optional[int] = 200) -> None:
    """
    Print the quantum circuit diagram of a `QuantumState` object.

    The circuit shows all actions that have been carried out on the quantum state.

    Args:
        qs: The `QuantumState` object.
        max_visible: The maximum number of characters visible on each line of the circuit.
            Default limit is 200 characters. Set to `None` to remove this limit.
    """

    circuit_string = ""

    if max_visible is None:
        for i in range(
            len(qs.circuit) - 1
        ):  # We don't want to print the last line of empty space
            circuit_string += "".join(qs.circuit[i]) + "\n"
    else:
        if len(qs.circuit[0]) - 4 > max_visible:
            for i in range(
                len(qs.circuit) - 1
            ):  # We don't want to print the last line of empty space
                circuit_string += qs.circuit[i][0] + "..."
                circuit_string += (
                    "".join(qs.circuit[i][4 + (len(qs.circuit[0]) - max_visible - 4) :])
                    + "\n"
                )
        else:
            for i in range(
                len(qs.circuit) - 1
            ):  # We don't want to print the last line of empty space
                circuit_string += "".join(qs.circuit[i]) + "\n"

    print(circuit_string[:-1])
