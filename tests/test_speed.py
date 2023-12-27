import time
import pyqubits
from tests.utils import apply_gate


def main():
    num_qubits = 14

    # old algorithm (repeated application of np.kron)
    print("===OLD ALGORITHM===")
    start = time.time()
    state = pyqubits.QuantumState.from_bits("0" * num_qubits)
    state = apply_gate(pyqubits.H.matrix(), state, 1)
    end = time.time()
    print("time taken:", end - start)

    # new algorithm (memkron)
    print("===NEW ALGORITHM===")
    start = time.time()
    state = pyqubits.QuantumState.from_bits("0" * num_qubits)
    state.H(1)
    end = time.time()
    print("time taken:", end - start)


if __name__ == "__main__":
    main()
