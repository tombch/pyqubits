import numpy as np 

def complex_multiply(z0, z1):
    return [z0[0]*z1[0] - z0[1]*z1[1], z0[0]*z1[1] + z0[1]*z1[0]]

def kronecker_product(m1, m2):
    (r1, c1, b1) = m1.shape
    (r2, c2, b2) = m2.shape
    m3 = np.zeros((r1*r2, c1*c2, 2))
    for i in range(0, r1*r2, r2):
        for j in range(0, c1*c2, c2):
            m1_row = int(i/r2)
            m1_col = int(j/c2)
            m1m2 = np.zeros((r2, c2, 2))
            for l in range(r2):
                for m in range(c2):           
                    m1m2[l][m] = complex_multiply(m1[m1_row, m1_col], m2[l, m])
            m3[i:i+r2, j:j+c2] = m1m2
    return m3

def complex_matmul(m1, m2):
    (r1, c1, b1) = m1.shape
    (r2, c2, b2) = m2.shape
    m3 = np.zeros((r1, c2, 2))
    for i in range(r1):
        for j in range(c2):
            element_sum = [0,0]
            for k in range(c1):
                element_sum = np.add(element_sum, complex_multiply(m1[i][k], m2[k][j]))
            m3[i][j] = element_sum
    return m3

def normaliser(state_vec):
    normaliser = 0
    for i in range(len(state_vec)):
        normaliser += state_vec[i][0][0]**2 + state_vec[0][0][1]**2
    return np.sqrt(normaliser)

def complex_conjugate(m):
    (r, c, b) = m.shape
    for i in range(r):
        for j in range(c):
            m[i][j][1] = -m[i][j][1]
    return m

def conjugate_transpose(m):
    m = complex_conjugate(m)
    m = np.transpose(m, (1, 0, 2))
    return m