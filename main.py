import time
import numpy as np
import qvert as qvt

#Example quantum algorithms
def entanglement():
    s = qvt.QuantumState(num_qubits=2, preset_state="zero_state", state_name="s")
    s.print_state()
    qvt.H(s, qubit=1)
    s.print_state()
    qvt.CNOT(s, control=1, target=2)
    s.print_state()
    s.measurement(qubit=1)
    s.print_state()
    s.print_circuit()

def quantum_teleportation():
    v = qvt.QuantumState(state_name="v")    
    b1 = qvt.QuantumState(preset_state="zero_state", state_name="b1")
    b2 = qvt.QuantumState(preset_state="zero_state", state_name="b2")  
    v.print_state()
    b1.print_state()
    b2.print_state()
    vxb1xb2 = qvt.join_states([v, b1, b2], state_name="vxb1xb2")
    qvt.H(vxb1xb2, qubit=2)
    qvt.CNOT(vxb1xb2, control=2, target=3)
    vxb1xb2.print_state()
    qvt.CNOT(vxb1xb2, control=1, target=2)
    qvt.H(vxb1xb2, qubit=1)
    m_1 = vxb1xb2.measurement(qubit=1)
    m_2 = vxb1xb2.measurement(qubit=2)
    if m_2 == 1:
        qvt.X(vxb1xb2, qubit=3)
    if m_1 == 1:
        qvt.Z(vxb1xb2, qubit=3)
    vxb1xb2.print_state()
    vxb1xb2.print_circuit()

def deutsch_algorithm():
    q1 = qvt.QuantumState(preset_state="zero_state", state_name="q1")
    q2 = qvt.QuantumState(preset_state="one_state", state_name="q2")
    q1xq2 = qvt.join_states([q1, q2], state_name="q1xq2")
    q1xq2.print_state()
    qvt.H(q1xq2, qubit=1)
    qvt.H(q1xq2, qubit=2)
    qvt.Uf2(q1xq2, f_choice=1)
    qvt.H(q1xq2, qubit=1)
    f0_xor_f1 = q1xq2.measurement(qubit=1)
    q1xq2.print_state()
    q1xq2.print_circuit()
    if f0_xor_f1 == 0:
        print("f is constant")
    elif f0_xor_f1 == 1:
        print("f is balanced")

def main():
    start = time.time()
    q = qvt.QuantumState(num_qubits=4, preset_state="zero_state", state_name="q")
    q.print_state()
    qvt.H(q, qubit=1)
    qvt.CNOT(q, control=1, target=2)
    q.print_state()
    qvt.H(q, qubit=4)
    qvt.CNOT(q, control=4, target=2)
    q.print_state()
    q.measurement(qubit=4)
    q.measurement(qubit=1)
    q.print_state()
    q.print_circuit()
    end = time.time()
    print("Time taken: " + str(end - start) + " seconds")

if __name__ == '__main__':
    main()