from pyqubits import QuantumState


def quantum_teleportation():
    v = QuantumState(n = 1)
    b = QuantumState.from_bits('00')
    vb = v * b
    print(vb)
    vb.H(qubit = 2)
    vb.CNOT(control = 2, target = 3)
    vb.CNOT(control = 1, target = 2)
    vb.H(qubit = 1)
    m1 = vb.measure(qubit = 1).bit
    m2 = vb.measure(qubit = 2).bit
    if m2 == 1:
        vb.X(qubit = 3)
    if m1 == 1:
        vb.Z(qubit = 3)
    print(vb)
    print(vb.circuit)


if __name__ == '__main__':
    print("===QUANTUM TELEPORTATION===")
    quantum_teleportation()