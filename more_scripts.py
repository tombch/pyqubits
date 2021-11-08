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
# --timer on | --new q | --new bellstate num_qubits=2 state=zero | --apply H bellstate 1 | --apply CNOT bellstate [1,2] | --state q bellstate | --join q bellstate name=qb | --apply CNOT qb [1,2] | --apply H qb 1 | --measure qb 1 2 mv | --if-then {qb.2 == 1} {--apply X qb 3} | --if-then {qb.1 == 1} {--apply Z qb 3} | --circuit qb | --state qb
