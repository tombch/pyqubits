from pyqubits import QuantumState, print_state, print_circuit


def quantum_teleportation():
    qs = QuantumState.from_bits("q00")
    print_state(qs)
    qs.H(2)
    qs.CNOT(2, 3)
    qs.CNOT(1, 2)
    qs.H(1)
    m1 = qs.measure(1).bit
    m2 = qs.measure(2).bit
    if m2 == 1:
        qs.X(3)
    if m1 == 1:
        qs.Z(3)
    print_state(qs)
    print_circuit(qs)


if __name__ == "__main__":
    print("===QUANTUM TELEPORTATION===")
    quantum_teleportation()
