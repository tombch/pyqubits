from scripts import quantum_state
from . import run_command
import numpy as np


def test_new():
    env = run_command.run_command("new q .qubits=4 .preset=zero")
    q = env['states_dict']['q']
    zero_state_vector = np.zeros(2**4, dtype='complex')
    zero_state_vector[0] = 1
    assert isinstance(q, quantum_state.QuantumState)
    assert q.num_qubits == 4
    assert round(np.linalg.norm(q.state_vector), quantum_state.QuantumState.dp) == 1
    assert np.array_equal(q.state_vector, zero_state_vector)

    env = run_command.run_command("new r .qubits=8 .preset=one")
    q = env['states_dict']['r']
    one_state_vector = np.zeros(2**8, dtype='complex')
    one_state_vector[-1] = 1
    assert isinstance(q, quantum_state.QuantumState)
    assert q.num_qubits == 8
    assert round(np.linalg.norm(q.state_vector), quantum_state.QuantumState.dp) == 1
    assert np.array_equal(q.state_vector, one_state_vector)

    env = run_command.run_command("new s")
    q = env['states_dict']['s']
    assert isinstance(q, quantum_state.QuantumState)
    assert q.num_qubits == 1
    assert round(np.linalg.norm(q.state_vector), quantum_state.QuantumState.dp) == 1

