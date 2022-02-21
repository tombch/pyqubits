from pyqubits import QuantumState


def deutsch_algorithm():
    for x in ['const0', 'const1', 'bal0', 'bal1']:
        s = QuantumState.from_bits('01')
        s.H(qubit = 1)
        s.H(qubit = 2)
        s.f2(qubit1 = 1, qubit2 = 2, f = x)
        s.H(qubit = 1)
        f0_xor_f1 = s.measure(qubit = 1).bit
        print(s.circuit)
        if f0_xor_f1 == 0:
            print(f"{x} is constant")
        elif f0_xor_f1 == 1:
            print(f"{x} is balanced")

    
if __name__ == '__main__':
    print("===DEUTSCH'S ALGORITHM===")
    deutsch_algorithm()