from pyqubits import QuantumState


def quantum_teleportation():
    s = QuantumState.from_bits('q00')
    print(s)
    s.H(2)
    s.CNOT(2, 3)
    s.CNOT(1, 2)
    s.H(1)
    m1 = s.measure(1).bit
    m2 = s.measure(2).bit
    if m2 == 1:
        s.X(3)
    if m1 == 1:
        s.Z(3)
    print(s)
    print(s.circuit)


if __name__ == '__main__':
    print("===QUANTUM TELEPORTATION===")
    quantum_teleportation()