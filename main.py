from qubits import Qubits
import gates
import numpy as np
import linear_algebra as la
import time

#quantum-computing-sim
start = time.time()

s1 = Qubits(2, "zero_state")
s1.print_state()

gates.H(s1, qubit=1)
s1.print_state()

gates.CNOT(s1, control=1, target=2)
s1.print_state()

s1.measurement(qubit=1)
s1.print_state()

end = time.time()
print("Time taken: " + str(end - start) + " seconds")