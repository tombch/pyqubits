from scripts import quantum_state
from scripts import gates
from scripts import main
import numpy as np
# python3 -m pytest -v


def test_new():
    env = main.new_env()
    env = main.run_commands("new q .num-qubits=4 .vector=zero", env)
    q = env['states_dict']['q']
    zero_state_vector = np.zeros(2**4, dtype='complex')
    zero_state_vector[0] = 1
    assert isinstance(q, quantum_state.QuantumState)
    assert q.num_qubits == 4
    assert round(np.linalg.norm(q.state_vector), quantum_state.QuantumState.dp - 2) == 1
    assert np.array_equal(q.state_vector, zero_state_vector)

    env = main.run_commands("new r .num-qubits=8 .vector=one", env)
    q = env['states_dict']['r']
    one_state_vector = np.zeros(2**8, dtype='complex')
    one_state_vector[-1] = 1
    assert isinstance(q, quantum_state.QuantumState)
    assert q.num_qubits == 8
    assert round(np.linalg.norm(q.state_vector), quantum_state.QuantumState.dp - 2) == 1
    assert np.array_equal(q.state_vector, one_state_vector)

    env = main.run_commands("new s", env)
    q = env['states_dict']['s']
    assert isinstance(q, quantum_state.QuantumState)
    assert q.num_qubits == 1
    assert round(np.linalg.norm(q.state_vector), quantum_state.QuantumState.dp - 2) == 1


def test_join():
    pass


def test_rename():
    pass


def test_delete():
    pass