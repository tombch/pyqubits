import numpy as np
import complex_number as cn
from qubit import Qubit

def complex_matmul(m, q):
    q0 = np.add(cn.multiply(q.state_vector[0], m[0][0]), cn.multiply(q.state_vector[1], m[0][1]))
    q1 = np.add(cn.multiply(q.state_vector[0], m[1][0]), cn.multiply(q.state_vector[1], m[1][1]))
    return (q0, q1)

def I(q):
    matrix = np.array([[[1,0], [0,0]], [[0,0], [1,0]]])
    (q0, q1) = complex_matmul(matrix, q)
    q.state_vector[0] = q0
    q.state_vector[1] = q1
    print(q.name + " --> I(" + q.name + ")")   

def X(q):
    matrix = np.array([[[0,0], [1,0]], [[1,0], [0,0]]])
    (q0, q1) = complex_matmul(matrix, q)
    q.state_vector[0] = q0
    q.state_vector[1] = q1
    print(q.name + " --> X(" + q.name + ")")

def Y(q):
    matrix = np.array([[[0,0], [0,-1]], [[0,1], [0,0]]])
    (q0, q1) = complex_matmul(matrix, q)
    q.state_vector[0] = q0
    q.state_vector[1] = q1
    print(q.name + " --> Y(" + q.name + ")")

def Z(q):
    matrix = np.array([[[1,0], [0,0]], [[0,0], [-1,0]]])
    (q0, q1) = complex_matmul(matrix, q)
    q.state_vector[0] = q0
    q.state_vector[1] = q1
    print(q.name + " --> Z(" + q.name + ")")

def H(q):
    matrix = np.array([[[1,0], [1,0]], [[1,0], [-1,0]]])/np.sqrt(2)
    (q0, q1) = complex_matmul(matrix, q)
    q.state_vector[0] = q0
    q.state_vector[1] = q1
    print(q.name + " --> H(" + q.name + ")")