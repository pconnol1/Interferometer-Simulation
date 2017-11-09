def complexAmplitude(U_0,k,r):
    U = U_0 * (math.cos(k*r) + 1j*math.sin(k*r))/r
    return U