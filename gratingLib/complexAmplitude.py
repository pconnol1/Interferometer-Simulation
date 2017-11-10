import numpy as np

def complexAmplitude(U_0,k,r,phase):
    U = U_0* np.exp(1j*phase) * (np.cos(k*r) + 1j*np.sin(k*r))/r
    return U