from qubit import Qubit
import gates

#quantum-computing-sim
q1 = Qubit("q1")
q1.print_state()
gates.X(q1)
q1.print_state()

q2 = Qubit("q2", "zero")
q2.print_state()
gates.H(q2)
q2.print_state()

q3 = Qubit("q3")
q3.print_state()
q3.measurement()
q3.print_state()
gates.H(q3)
q3.print_state()
q3.measurement()
q3.print_state()