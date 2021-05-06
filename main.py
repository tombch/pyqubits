from qubits import Qubits
import gates
import numpy as np
import time

#quantum-computing-sim
start = time.time()

s1 = Qubits(3, "zero_state")
s1.print_state()

gates.H(s1, qubit=1)
s1.print_state()

gates.CNOT(s1, control=1)
s1.print_state()

gates.measurement(s1, 1)
s1.print_state()

end = time.time()
print("Time taken: " + str(end - start) + " seconds")