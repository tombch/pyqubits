import numpy as np
import pyqubits
from tests.utils import apply_gate, apply_cgate, apply_2gate


# Max difference between floats
TOLERANCE = 1e-12


def _test_gate(gate, gate_attr):
    for i in range(1, 6):
        for j in range(1, i + 1):
            state_1 = pyqubits.QuantumState(n_qubits=i)
            state_2 = pyqubits.QuantumState.from_vector(state_1.vector)  # type: ignore
            np.testing.assert_allclose(state_1.vector, state_2.vector, rtol=TOLERANCE)
            state_1 = getattr(state_1, gate_attr)(j)
            state_2 = apply_gate(gate, state_2, j)
            np.testing.assert_allclose(state_1.vector, state_2.vector, rtol=TOLERANCE)


def _test_cgate(gate, gate_attr):
    for i in range(2, 6):
        for j in range(1, i + 1):
            for k in range(1, i + 1):
                if j != k:
                    state_1 = pyqubits.QuantumState(n_qubits=i)
                    state_2 = pyqubits.QuantumState.from_vector(state_1.vector)  # type: ignore
                    np.testing.assert_allclose(
                        state_1.vector, state_2.vector, rtol=TOLERANCE
                    )
                    state_1 = getattr(state_1, gate_attr)(j, k)
                    state_2 = apply_cgate(gate, state_2, j, k)
                    np.testing.assert_allclose(
                        state_1.vector, state_2.vector, rtol=TOLERANCE
                    )


def _test_f2(gate, gate_attr, f):
    for i in range(2, 6):
        for j in range(1, i):
            state_1 = pyqubits.QuantumState(n_qubits=i)
            state_2 = pyqubits.QuantumState.from_vector(state_1.vector)  # type: ignore
            np.testing.assert_allclose(state_1.vector, state_2.vector, rtol=TOLERANCE)
            state_1 = getattr(state_1, gate_attr)(j, j + 1, f=f)
            state_2 = apply_2gate(gate, state_2, j, j + 1)
            np.testing.assert_allclose(state_1.vector, state_2.vector, rtol=TOLERANCE)


def test_X():
    _test_gate(pyqubits.X.matrix(), "X")


def test_Y():
    _test_gate(pyqubits.Y.matrix(), "Y")


def test_Z():
    _test_gate(pyqubits.Z.matrix(), "Z")


def test_H():
    _test_gate(pyqubits.H.matrix(), "H")


def test_P():
    _test_gate(pyqubits.P.matrix(), "P")


def test_T():
    _test_gate(pyqubits.T.matrix(), "T")


def test_CNOT():
    _test_cgate(pyqubits.CNOT.matrix(), "CNOT")


def test_CY():
    _test_cgate(pyqubits.CY.matrix(), "CY")


def test_CZ():
    _test_cgate(pyqubits.CZ.matrix(), "CZ")


def test_CH():
    _test_cgate(pyqubits.CH.matrix(), "CH")


def test_CP():
    _test_cgate(pyqubits.CP.matrix(), "CP")


def test_CT():
    _test_cgate(pyqubits.CT.matrix(), "CT")


def test_f2():
    _test_f2(pyqubits.f2.matrix("bal0"), "f2", "bal0")
    _test_f2(pyqubits.f2.matrix("bal1"), "f2", "bal1")
    _test_f2(pyqubits.f2.matrix("const0"), "f2", "const0")
    _test_f2(pyqubits.f2.matrix("const1"), "f2", "const1")
