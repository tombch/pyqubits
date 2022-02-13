from pyqubits import QuantumState


def main():
    s = QuantumState.from_bits('00')
    print(s)
    print(s.H(qubit = 1))
    print(s.CNOT(control = 1, target = 2))
    print(s.measure(qubit = 1))    
    print(f'Measured first qubit, received {s.bit}')
    print(s.dist)
    print(s.circuit)


if __name__ == '__main__':
    main()