import gates
from quantum_state import QuantumState

# Example quantum algorithms
def entanglement():
    print("===ENTANGLEMENT===")
    s = quantum_state.QuantumState(num_qubits=2, preset_state="zero_state", state_name="s")
    s.print_state()
    gates.H(s, qubit=1)
    s.print_state()
    gates.CNOT(s, control=1, target=2)
    s.print_state()
    s.measurement(qubit=1)
    s.print_state()
    s.print_circuit()

# command line version of quantum teleportation: 
# -t on | 
# -n q | 
# -n b ps=state0 nq=2 | 
# -j q b name=qb | 
# -s qb | 
# -a H qb 2 | 
# -a CNOT qb [2, 3] | 
# -a CNOT qb [1, 2] | 
# -a H qb 1 | 
# -m qb 1 2 mv | 
# -i-t {qb.2 == 1} {-a X qb 3} | 
# -i-t {qb.1 == 1} {-a Z qb 3} | 
# -c qb | 
# -s qb
# -t on | -n q | -n b ps=state0 nq=2 | -j q b name=qb | -s qb | -a H qb 2 | -a CNOT qb [2, 3] | -a CNOT qb [1,2] | -a H qb 1 | -m qb 1 2 mv | -i-t {qb.2 == 1} {-a X qb 3} | -i-t {qb.1 == 1} {-a Z qb 3} | -c qb | -s qb

# alternative:
# --timer on | --new q | --new b00 num_qubits=2 preset_state=state0 | --apply H b00 1 | --apply CNOT b00 [1,2] | --state q b00 | --join q b00 name=qb00 | --apply CNOT qb00 [1, 2] | --apply H qb00 1 | --measure qb00 1 2 mv | --if-then {qb00.2 == 1} {--apply X qb00 3} | --if-then {qb00.1 == 1} {--apply Z qb00 3} | --state qb00 | --circuit qb00

def quantum_teleportation():
    print("===QUANTUM TELEPORTATION===")
    v = quantum_state.QuantumState(state_name="v")    
    b1 = quantum_state.QuantumState(preset_state="zero_state", state_name="b1")
    b2 = quantum_state.QuantumState(preset_state="zero_state", state_name="b2")  
    v.print_state()
    b1.print_state()
    b2.print_state()
    vxb1xb2 = v * b1 * b2
    vxb1xb2.print_state()
    gates.H(vxb1xb2, qubit=2)
    gates.CNOT(vxb1xb2, control=2, target=3)
    vxb1xb2.print_state()
    gates.CNOT(vxb1xb2, control=1, target=2)
    gates.H(vxb1xb2, qubit=1)
    m_1 = vxb1xb2.measurement(qubit=1)
    m_2 = vxb1xb2.measurement(qubit=2)
    if m_2 == 1:
        gates.X(vxb1xb2, qubit=3)
    if m_1 == 1:
        gates.Z(vxb1xb2, qubit=3)
    vxb1xb2.print_state()
    vxb1xb2.print_circuit()

def deutsch_algorithm():
    print("===DEUTSCH'S ALGORITHM===")
    q1 = quantum_state.QuantumState(preset_state="zero_state", state_name="q1")
    q2 = quantum_state.QuantumState(preset_state="one_state", state_name="q2")
    q1xq2 = q1 * q2
    q1xq2.print_state()
    gates.H(q1xq2, qubit=1)
    gates.H(q1xq2, qubit=2)
    gates.Uf2(q1xq2, f_choice=1)
    gates.H(q1xq2, qubit=1)
    q1xq2.print_state()
    f0_xor_f1 = q1xq2.measurement(qubit=1)
    q1xq2.print_state()
    q1xq2.print_circuit()
    if f0_xor_f1 == 0:
        print("f is constant")
    elif f0_xor_f1 == 1:
        print("f is balanced")