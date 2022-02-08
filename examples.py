import pyquantum as pyq

def main():
    s = pyq.QuantumState(qubits=2, vector='zero')
    print(s.state())
    print(s.dist())

    s.H(qubit=1)
    s.CNOT(control=1, target=2)
    print(s.state())
    print(s.dist())
    
    bit = s.measure(qubit=1)
    print(f'Measured first qubit, received {bit}')
    print(s.state())
    print(s.dist())
    print(s.circuit())


if __name__ == '__main__':
    main()