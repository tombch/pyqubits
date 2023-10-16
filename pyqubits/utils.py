import inspect
import numpy as np
import numba as nb
import pyqubits.gates as gates


class PyQubitsError(Exception):
    pass


def validate_qubits(method):
    """
    This decorator checks that the integer arguments of a `QuantumState` method (which are assumed to be qubits) are valid.
    """

    # Define the decorated function
    def wrapped_method(obj, *args, **kwargs):
        arg_names = list(inspect.signature(method).parameters)[1:]
        arg_types = {
            x: inspect.signature(method).parameters[x].annotation for x in arg_names
        }

        # Turn positional arguments into keyword arguments
        for name, value in zip(arg_names, args):
            kwargs[name] = value

        # Validate keyword arguments
        for name, value in kwargs.items():
            # If the argument type is not an integer, then it is not a qubit argument so can be ignored
            if arg_types.get(name) == int:
                if (not isinstance(value, int)) or (
                    not (1 <= value <= obj._num_qubits)
                ):
                    raise PyQubitsError(
                        f"'{name}' must be a positive integer, less than or equal to the number of qubits in the state"
                    )

        # Return the original method, with its (now validated) all keyword arguments
        return method(obj, **kwargs)

    return wrapped_method


@nb.njit(fastmath=True, parallel=True)
def memkron(gates, state, binary_values):
    """
    Apply gate(s) to qubit(s) in the state, without creating an enormous matrix in the process
    """
    new_state = [0 + 0j for _ in range(len(state))]
    for i in nb.prange(len(state)):
        for j in nb.prange(len(state)):
            val = 1
            for k in range(len(gates)):
                val *= gates[k][binary_values[i][k]][binary_values[j][k]]
            new_state[i] += val * state[j]
    return new_state


# Force compile on import
memkron(
    np.asarray([gates.I_matrix]),
    np.asarray([1.0 + 0.0j, 0.0 + 0.0j]),
    np.asarray([[0], [1]]),
)


def _cgate(control, target, gate_char):
    """
    Helper function for gate classes.
    Creates a cgate representation that will be added to a state's circuit.
    """
    gate = []
    if control < target:
        gate.append(["O"])
        gate.append(["|"])
        for _ in range(abs(target - control) - 1):
            gate.append(["|"])
            gate.append(["|"])
        gate.append([gate_char])
    elif control > target:
        gate.append([gate_char])
        gate.append(["|"])
        for _ in range(abs(target - control) - 1):
            gate.append(["|"])
            gate.append(["|"])
        gate.append(["O"])
    else:
        raise PyQubitsError("'control' and 'target' cannot be the same")
    return gate
