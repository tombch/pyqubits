import pyqubits
import numpy as np


# Max difference between floats
TOLERANCE = 1e-12


def apply_gate(chosen_matrix, state, qubit):
    if (qubit == 1):
        gate_matrix = chosen_matrix
    else:
        gate_matrix = pyqubits.I_matrix
    for i in range(2, state._num_qubits+1):
        if (i == qubit):
            gate_matrix = np.kron(gate_matrix, chosen_matrix)
        else:
            gate_matrix = np.kron(gate_matrix, pyqubits.I_matrix)
    state._state_vector = gate_matrix @ state._state_vector
    return state


def apply_2gate(chosen_matrix, state, qubit1, qubit2):
    if (qubit1 == 1):
        gate_matrix = chosen_matrix
    else:
        gate_matrix = pyqubits.I_matrix
    for i in range(2, state._num_qubits+1):
        if (i == qubit1):
            gate_matrix = np.kron(gate_matrix, chosen_matrix)
        elif (i == qubit2):
            continue
        else:
            gate_matrix = np.kron(gate_matrix, pyqubits.I_matrix)
    state._state_vector = gate_matrix @ state._state_vector
    return state


def apply_cgate(chosen_matrix, state, control, target):
    if (control == 1):
        gate_matrix_a = pyqubits.zero_matrix
        gate_matrix_b = pyqubits.one_matrix
    elif (target == 1):
        gate_matrix_a = pyqubits.I_matrix
        gate_matrix_b = chosen_matrix
    else:
        gate_matrix_a = pyqubits.I_matrix
        gate_matrix_b = pyqubits.I_matrix
    for i in range(2, state._num_qubits+1):
        if (i == control):
            gate_matrix_a = np.kron(gate_matrix_a, pyqubits.zero_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, pyqubits.one_matrix)
        elif (i == target):
            gate_matrix_a = np.kron(gate_matrix_a, pyqubits.I_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, chosen_matrix)         
        else:
            gate_matrix_a = np.kron(gate_matrix_a, pyqubits.I_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, pyqubits.I_matrix)
    gate_matrix = np.add(gate_matrix_a, gate_matrix_b)
    state._state_vector = gate_matrix @ state._state_vector
    return state


def _test_gate(gate, gate_attr):
    for i in range(1, 6):
        for j in range(1, i+1):
            state_1 = pyqubits.QuantumState(n=i)
            state_2 = pyqubits.QuantumState.from_vector(state_1.vector) # type: ignore
            np.testing.assert_allclose(state_1.vector, state_2.vector, rtol=TOLERANCE)
            state_1 = getattr(state_1, gate_attr)(j)
            state_2 = apply_gate(gate, state_2, j)
            np.testing.assert_allclose(state_1.vector, state_2.vector, rtol=TOLERANCE)    


def _test_cgate(gate, gate_attr):
    for i in range(2, 6):
        for j in range(1, i+1):
            for k in range(1, i+1):
                if j != k:
                    state_1 = pyqubits.QuantumState(n=i)
                    state_2 = pyqubits.QuantumState.from_vector(state_1.vector) # type: ignore
                    np.testing.assert_allclose(state_1.vector, state_2.vector, rtol=TOLERANCE)
                    state_1 = getattr(state_1, gate_attr)(j, k)
                    state_2 = apply_cgate(gate, state_2, j, k)
                    np.testing.assert_allclose(state_1.vector, state_2.vector, rtol=TOLERANCE)   


def _test_f2(gate, gate_attr, f):
    for i in range(2, 6):
        for j in range(1, i):
            state_1 = pyqubits.QuantumState(n=i)
            state_2 = pyqubits.QuantumState.from_vector(state_1.vector) # type: ignore
            np.testing.assert_allclose(state_1.vector, state_2.vector, rtol=TOLERANCE)
            state_1 = getattr(state_1, gate_attr)(j, j+1, f=f)
            state_2 = apply_2gate(gate, state_2, j, j+1)
            np.testing.assert_allclose(state_1.vector, state_2.vector, rtol=TOLERANCE)   


def test_X():
    _test_gate(pyqubits.X.matrix(), 'X')


def test_Y():
    _test_gate(pyqubits.Y.matrix(), 'Y')


def test_Z():
    _test_gate(pyqubits.Z.matrix(), 'Z')


def test_H():
    _test_gate(pyqubits.H.matrix(), 'H')


def test_P():
    _test_gate(pyqubits.P.matrix(), 'P')


def test_T():
    _test_gate(pyqubits.T.matrix(), 'T')


def test_CNOT():
    _test_cgate(pyqubits.CNOT.matrix(), 'CNOT')


def test_CY():
    _test_cgate(pyqubits.CY.matrix(), 'CY')


def test_CZ():
    _test_cgate(pyqubits.CZ.matrix(), 'CZ')


def test_CH():
    _test_cgate(pyqubits.CH.matrix(), 'CH')


def test_CP():
    _test_cgate(pyqubits.CP.matrix(), 'CP')


def test_CT():
    _test_cgate(pyqubits.CT.matrix(), 'CT')


def test_f2():
    _test_f2(pyqubits.f2.matrix('bal0'), 'f2', 'bal0')
    _test_f2(pyqubits.f2.matrix('bal1'), 'f2', 'bal1')
    _test_f2(pyqubits.f2.matrix('const0'), 'f2', 'const0')
    _test_f2(pyqubits.f2.matrix('const1'), 'f2', 'const1')
