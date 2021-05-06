import numpy as np 

def multiply(z0, z1):
    return [z0[0]*z1[0] - z0[1]*z1[1], z0[0]*z1[1] + z0[1]*z1[0]]

def show(z):
    return str(z[0]) + " + " + str(z[1]) + " i"