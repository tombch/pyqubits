from pyqubits import QuantumState, print_state, print_dist, print_circuit


def entanglement():
    s = QuantumState.from_bits("00")
    print_state(s)
    print_state(s.H(1))
    print_state(s.CNOT(1, 2))
    print_dist(s)
    result = s.measure(1).bit
    print(f"Measured first qubit, received {result}")
    print_circuit(s)
    print_state(s)


if __name__ == "__main__":
    print("===ENTANGLEMENT===")
    entanglement()
