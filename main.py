from quantum_state import QuantumState
import gates
import numpy as np
import linear_algebra as la
import time

def main():
    start = time.time()
    s1 = QuantumState(num_qubits=4, preset_state="zero_state", state_name="s1")
    s1.print_state()
    s2 = QuantumState(num_qubits=4, preset_state="zero_state", state_name="s2")
    s2.print_state()
    s1s2 = gates.join_states(s1, s2, state_name="s1s2")
    s1s2.print_state()
    gates.H(s1s2, qubit=1)
    s1s2.print_state()
    gates.CNOT(s1s2, control=1, target=2)
    s1s2.print_state()
    s1s2.measurement(qubit=1)
    s1s2.print_state()
    end = time.time()
    print("Time taken: " + str(end - start) + " seconds")

if __name__ == '__main__':
    main()