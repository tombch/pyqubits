from pyqubits import QuantumState, print_state, print_dist, print_circuit


def entanglement():
    qs = QuantumState.from_bits("00")
    print_state(qs)
    print_state(qs.H(1))
    print_state(qs.CNOT(1, 2))
    print_dist(qs)
    result = qs.measure(1).bit
    print(f"Measured first qubit, received {result}")
    print_circuit(qs)
    print_state(qs)


if __name__ == "__main__":
    print("===ENTANGLEMENT===")
    entanglement()
