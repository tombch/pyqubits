from pyquantum import QuantumState

def main():
    s = QuantumState(n=2, bits='00')
    print(s)

    s.H(qubit=1)
    s.CNOT(control=1, target=2)    
    bit = s.measure(qubit=1).bit
    s.vector
    print(f'Measured first qubit, received {bit}')
    print(s)
    print(s.dist)
    print(s.circuit)


if __name__ == '__main__':
    main()