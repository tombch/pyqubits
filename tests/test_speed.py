from quantum_state import QuantumState
import gates
import time


# Try timeit module
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

# import cProfile, pstats, io
# pr = cProfile.Profile()
# pr.enable()
# ...
# pr.disable()
# s = io.StringIO()
# ps = pstats.Stats(pr, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
# ps.print_stats()
# print(s.getvalue())