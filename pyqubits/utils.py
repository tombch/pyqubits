import inspect
import numpy as np
import numba as nb
from . import gates


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


def print_state(z):
    """
    Print the state of a `QuantumState` object.
    """

    amplitudes = []
    for amp in z.vector:
        amplitudes.append(
            str(amp)
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "")
            .replace("+", " + ")
            .replace("-", " - ")
            .replace("e - ", "e-")
            .strip()
        )
    longest_amp = 0
    for amp in amplitudes:
        if len(amp) > longest_amp:
            longest_amp = len(amp)
    for i, amp in enumerate(amplitudes):
        diff = longest_amp - len(amp)
        if diff != 0:
            amplitudes[i] = (" " * diff) + amplitudes[i]
    basis = [bin(i)[2:].zfill(z._num_qubits) for i in range(z._num_classical_states)]
    state_string = ""
    first_non_zero = True
    first_on_line = True
    for i, (amplitude, vector) in enumerate(zip(amplitudes, basis)):
        if z.vector[i] != 0:
            state_string += f"{'=' if first_non_zero else '+'} ({amplitude}) |{vector}> {chr(10) if not first_on_line else ''}"
            first_non_zero = False
            first_on_line = not first_on_line

    print(state_string[:-1] if state_string[-1] == "\n" else state_string)


def print_dist(z):
    """
    Print the discrete probability distribution of a `QuantumState` object.

    The distribution shows the probability of each outcome if every qubit in the quantum state is measured.
    """

    dist_string = ""
    gen_classical_states = (
        (i, bin(i)[2:].zfill(z._num_qubits)) for i in range(z._num_classical_states)
    )
    for i, bin_i in gen_classical_states:
        rounded_probability = round(abs(z.vector[i]) ** 2, 2)
        dist_string += f"{bin_i}\t{rounded_probability}\t|{'=' * int(100 * rounded_probability)}\n"  # type: ignore

    print(dist_string[:-1])


def print_circuit(z, full=False):
    """
    Print the quantum circuit diagram of a `QuantumState` object.

    The quantum circuit shows all actions that have been carried out on the quantum state.
    """

    circuit_string = ""

    if full:
        for i in range(
            len(z._circuit) - 1
        ):  # We don't want to print the last line of empty space
            circuit_string += "".join(z._circuit[i]) + "\n"
    else:
        if len(z._circuit[0]) - 4 > z.max_visible_circuit:
            for i in range(
                len(z._circuit) - 1
            ):  # We don't want to print the last line of empty space
                circuit_string += z._circuit[i][0] + "..."
                circuit_string += (
                    "".join(
                        z._circuit[i][
                            4 + (len(z._circuit[0]) - z.max_visible_circuit - 4) :
                        ]
                    )
                    + "\n"
                )
        else:
            for i in range(
                len(z._circuit) - 1
            ):  # We don't want to print the last line of empty space
                circuit_string += "".join(z._circuit[i]) + "\n"

    print(circuit_string[:-1])
