from pyqubits import QuantumState, print_circuit


def deutsch_algorithm():
    for x in ["const0", "const1", "bal0", "bal1"]:
        qs = QuantumState.from_bits("01")
        qs.H(1)
        qs.H(2)
        qs.f2(1, 2, f=x)
        qs.H(1)
        f0_xor_f1 = qs.measure(1).bit
        print_circuit(qs)
        if f0_xor_f1 == 0:
            print(f"{x} is constant")
        elif f0_xor_f1 == 1:
            print(f"{x} is balanced")


if __name__ == "__main__":
    print("===DEUTSCH'S ALGORITHM===")
    deutsch_algorithm()
