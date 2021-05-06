import numpy as np 

def multiply(z0, z1):
    return [z0[0]*z1[0] - z0[1]*z1[1], z0[0]*z1[1] + z0[1]*z1[0]]

def show(z):
    if (z[0] == 0) and (z[1] == 0):
        return str(z[0])         
    elif (z[0] == 0):
        return str(z[1]) + " i" 
    elif (z[1] == 0):
        return str(z[0])    
    else:
        return str(z[0]) + " + " + str(z[1]) + " i"