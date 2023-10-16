import time
import pyqubits
import numpy as np


def apply_gate(chosen_matrix, state, qubit):
    if qubit == 1:
        gate_matrix = chosen_matrix
    else:
        gate_matrix = pyqubits.I_matrix
    for i in range(2, state._num_qubits + 1):
        if i == qubit:
            gate_matrix = np.kron(gate_matrix, chosen_matrix)
        else:
            gate_matrix = np.kron(gate_matrix, pyqubits.I_matrix)
    state._state_vector = gate_matrix @ state._state_vector
    return state


def main():
    num_qubits = 14

    # old algorithm (repeated application of np.kron)
    start = time.time()
    state = pyqubits.QuantumState.from_bits("0" * num_qubits)
    state = apply_gate(pyqubits.H.matrix(), state, 1)
    end = time.time()
    print(end - start)

    # new algorithm (memkron)
    start = time.time()
    state = pyqubits.QuantumState.from_bits("0" * num_qubits)
    state.H(1)
    end = time.time()
    print(end - start)


if __name__ == "__main__":
    main()
