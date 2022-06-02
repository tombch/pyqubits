from pyqubits import QuantumState


def entanglement():
    s = QuantumState.from_bits('00')
    print(s)
    print(s.H(1))
    print(s.CNOT(1, 2))
    print(s.dist)
    result = s.measure(1).bit 
    print(f'Measured first qubit, received {result}')
    print(s.circuit)
    print(s)


if __name__ == '__main__':
    print("===ENTANGLEMENT===")
    entanglement()