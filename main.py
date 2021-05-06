from qubit import Qubit
from qubits import Qubits
import gates
import numpy as np
import time

#quantum-computing-sim
start = time.time()

print("System 1")
system1 = Qubits(3, "zero_state")
system1.print_state()
gates.H(system1, qubit=1)
system1.print_state()
gates.CNOT(system1, target=1)
system1.print_state()
gates.measurement(system1, 1)
system1.print_state()

print("System 2")
system2 = Qubits(1)
system2.print_state()
gates.X(system2, qubit=1)
system2.print_state()

end = time.time()
print("Time taken: " + str(end - start) + " seconds")