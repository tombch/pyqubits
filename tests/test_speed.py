from quantum_state import QuantumState
import gates
import time

start = time.time()
for i in range(10000):
    q = QuantumState(state_name='q', num_qubits=4)
    gates.H(q, qubit=1)
    gates.CNOT(q, control=2, target=3)
    q.measurement(qubit=2)

q.print_circuit()

end = time.time()
print("Time taken: " + str(end - start) + " seconds")
# 2.889599084854126