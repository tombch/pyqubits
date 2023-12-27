import numpy as np
import pyqubits


def apply_gate(chosen_matrix, state, qubit):
    if qubit == 1:
        gate_matrix = chosen_matrix
    else:
        gate_matrix = pyqubits.I_matrix
    for i in range(2, state.n_qubits + 1):
        if i == qubit:
            gate_matrix = np.kron(gate_matrix, chosen_matrix)
        else:
            gate_matrix = np.kron(gate_matrix, pyqubits.I_matrix)
    state.vector = gate_matrix @ state.vector
    return state


def apply_2gate(chosen_matrix, state, qubit1, qubit2):
    if qubit1 == 1:
        gate_matrix = chosen_matrix
    else:
        gate_matrix = pyqubits.I_matrix
    for i in range(2, state.n_qubits + 1):
        if i == qubit1:
            gate_matrix = np.kron(gate_matrix, chosen_matrix)
        elif i == qubit2:
            continue
        else:
            gate_matrix = np.kron(gate_matrix, pyqubits.I_matrix)
    state.vector = gate_matrix @ state.vector
    return state


def apply_cgate(chosen_matrix, state, control, target):
    if control == 1:
        gate_matrix_a = pyqubits.zero_matrix
        gate_matrix_b = pyqubits.one_matrix
    elif target == 1:
        gate_matrix_a = pyqubits.I_matrix
        gate_matrix_b = chosen_matrix
    else:
        gate_matrix_a = pyqubits.I_matrix
        gate_matrix_b = pyqubits.I_matrix
    for i in range(2, state.n_qubits + 1):
        if i == control:
            gate_matrix_a = np.kron(gate_matrix_a, pyqubits.zero_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, pyqubits.one_matrix)
        elif i == target:
            gate_matrix_a = np.kron(gate_matrix_a, pyqubits.I_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, chosen_matrix)
        else:
            gate_matrix_a = np.kron(gate_matrix_a, pyqubits.I_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, pyqubits.I_matrix)
    gate_matrix = np.add(gate_matrix_a, gate_matrix_b)
    state.vector = gate_matrix @ state.vector
    return state
