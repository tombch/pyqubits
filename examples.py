from pyquantum import QuantumState

def main():
    s = QuantumState(qubits=2, vector='00')
    print(s.state())
    
    s.H(1).CNOT(1, 2)    
    bit = s.measure(qubit=1)
    
    print(f'Measured first qubit, received {bit}')
    print(s.state())
    print(s.dist())
    print(s.circuit())


if __name__ == '__main__':
    main()