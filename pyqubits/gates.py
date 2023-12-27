import random
from typing import List
import numpy as np


def _cgate(control: int, target: int, gate_char: str) -> List:
    """
    Helper function for gate classes.
    Creates a cgate representation that will be added to a state's circuit.

    Args:
        control (int): Control qubit.
        target (int): Target qubit.
        gate_char (str): Gate character.

    Returns:
        The cgate representation.
    """
    gate = []
    if control < target:
        gate.append(["O"])
        gate.append(["│"])
        for _ in range(abs(target - control) - 1):
            gate.append(["│"])
            gate.append(["│"])
        gate.append([gate_char])
    elif control > target:
        gate.append([gate_char])
        gate.append(["│"])
        for _ in range(abs(target - control) - 1):
            gate.append(["│"])
            gate.append(["│"])
        gate.append(["O"])
    else:
        raise ValueError("'control' and 'target' cannot be the same")
    return gate


zero_matrix = np.array([[1 + 0j, 0 + 0j], [0 + 0j, 0 + 0j]])


one_matrix = np.array([[0 + 0j, 0 + 0j], [0 + 0j, 1 + 0j]])


I_matrix = np.array([[1 + 0j, 0 + 0j], [0 + 0j, 1 + 0j]])


class X:
    @classmethod
    def matrix(cls):
        return np.array([[0 + 0j, 1 + 0j], [1 + 0j, 0 + 0j]])

    @classmethod
    def gate(cls):
        return [["X"]]


class Y:
    @classmethod
    def matrix(cls):
        return np.array([[0 + 0j, 0 - 1j], [0 + 1j, 0 + 0j]])

    @classmethod
    def gate(cls):
        return [["Y"]]


class Z:
    @classmethod
    def matrix(cls):
        return np.array([[1 + 0j, 0 + 0j], [0 + 0j, -1 + 0j]])

    @classmethod
    def gate(cls):
        return [["Z"]]


class H:
    @classmethod
    def matrix(cls):
        return np.array([[1 + 0j, 1 + 0j], [1 + 0j, -1 + 0j]]) / np.sqrt(2)

    @classmethod
    def gate(cls):
        return [["H"]]


class P:
    @classmethod
    def matrix(cls):
        return np.array([[1 + 0j, 0 + 0j], [0 + 0j, 0 + 1j]])

    @classmethod
    def gate(cls):
        return [["P"]]


class T:
    @classmethod
    def matrix(cls):
        return np.array(
            [[1 + 0j, 0 + 0j], [0 + 0j, (np.sqrt(2) / 2) + (np.sqrt(2) / 2) * 1j]]
        )

    @classmethod
    def gate(cls):
        return [["T"]]


class CNOT:
    @classmethod
    def matrix(cls):
        return X.matrix()

    @classmethod
    def gate(cls, control, target):
        return _cgate(control, target, X.gate()[0][0])


class CY:
    @classmethod
    def matrix(cls):
        return Y.matrix()

    @classmethod
    def gate(cls, control, target):
        return _cgate(control, target, Y.gate()[0][0])


class CZ:
    @classmethod
    def matrix(cls):
        return Z.matrix()

    @classmethod
    def gate(cls, control, target):
        return _cgate(control, target, Z.gate()[0][0])


class CH:
    @classmethod
    def matrix(cls):
        return H.matrix()

    @classmethod
    def gate(cls, control, target):
        return _cgate(control, target, H.gate()[0][0])


class CP:
    @classmethod
    def matrix(cls):
        return P.matrix()

    @classmethod
    def gate(cls, control, target):
        return _cgate(control, target, P.gate()[0][0])


class CT:
    @classmethod
    def matrix(cls):
        return T.matrix()

    @classmethod
    def gate(cls, control, target):
        return _cgate(control, target, T.gate()[0][0])


class f2:
    @classmethod
    def matrix(cls, f=None):
        if f is None:
            f = random.choice(["const0", "const1", "bal0", "bal1"])
        if f == "const0":
            return np.array(
                [
                    [1 + 0j, 0 + 0j, 0 + 0j, 0 + 0j],
                    [0 + 0j, 1 + 0j, 0 + 0j, 0 + 0j],
                    [0 + 0j, 0 + 0j, 1 + 0j, 0 + 0j],
                    [0 + 0j, 0 + 0j, 0 + 0j, 1 + 0j],
                ]
            )
        elif f == "const1":
            return np.array(
                [
                    [0 + 0j, 1 + 0j, 0 + 0j, 0 + 0j],
                    [1 + 0j, 0 + 0j, 0 + 0j, 0 + 0j],
                    [0 + 0j, 0 + 0j, 0 + 0j, 1 + 0j],
                    [0 + 0j, 0 + 0j, 1 + 0j, 0 + 0j],
                ]
            )
        elif f == "bal0":
            return np.array(
                [
                    [1 + 0j, 0 + 0j, 0 + 0j, 0 + 0j],
                    [0 + 0j, 1 + 0j, 0 + 0j, 0 + 0j],
                    [0 + 0j, 0 + 0j, 0 + 0j, 1 + 0j],
                    [0 + 0j, 0 + 0j, 1 + 0j, 0 + 0j],
                ]
            )
        elif f == "bal1":
            return np.array(
                [
                    [0 + 0j, 1 + 0j, 0 + 0j, 0 + 0j],
                    [1 + 0j, 0 + 0j, 0 + 0j, 0 + 0j],
                    [0 + 0j, 0 + 0j, 1 + 0j, 0 + 0j],
                    [0 + 0j, 0 + 0j, 0 + 0j, 1 + 0j],
                ]
            )

    @classmethod
    def gate(cls):
        return [
            ["┬", "─", "─", "┬"],
            ["│", "f", "2", "│"],
            ["┴", "─", "─", "┴"],
        ]
