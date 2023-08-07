import numpy as np
from scipy.linalg import solve


# Функция нелинейной деформационной модели
def NDM(Nz, Mx, My, Eb, sigmab_func, Es, sigmas_func, ConcreteX, ConcreteY, ConcreteArea, RebarX, RebarY, RebarArea, deltaMN):
    # Коэффициенты упругости
    nub = np.ones(len(ConcreteX))
    nus = np.ones(len(RebarX))
    if Mx != 0: deltaMx = 1
    else: deltaMx = 0
    if My != 0: deltaMy = 1
    else: deltaMy = 0
    if Nz != 0: deltaNz = 1
    else: deltaNz = 0
    sigmab = np.zeros(len(ConcreteX))
    sigmaS = np.zeros(len(RebarX))
    while deltaNz >= deltaMN and deltaMx >= deltaMN and deltaMy >= deltaMN:
        D11 = np.dot(ConcreteArea, ConcreteX**2 * nub) * Eb + np.dot(RebarArea, RebarX**2 * nus) * Es
        D22 = np.dot(ConcreteArea, ConcreteY**2 * nub) * Eb + np.dot(RebarArea, RebarY**2 * nus) * Es
        D12 = np.dot(ConcreteArea, ConcreteX * ConcreteY * nub) * Eb + np.dot(RebarArea, RebarX * RebarY * nus) * Es
        D13 = np.dot(ConcreteArea, ConcreteX * nub) * Eb + np.dot(RebarArea, RebarX * nus) * Es
        D23 = np.dot(ConcreteArea, ConcreteY * nub) * Eb + np.dot(RebarArea, RebarY * nus) * Es
        D33 = np.dot(ConcreteArea, nub) * Eb + np.dot(RebarArea, nus) * Es
        if Mx != 0 and My != 0:
            A = np.array([[Mx], [My], [Nz]])
            B = np.array([[D11, D12, D13], [D12, D22, D23], [D13, D23, D33]])
            X = solve(B, A)
            rx = 1/X[0]
            ry = 1/X[1]
        if Nz != 0 and Mx != 0 and My == 0:
            A = np.array([[Mx], [Nz]])
            B = np.array([[D11, D13], [D13, D33]])
            X = solve(B, A)
            rx = 1/X[0]
            ry = 1/X[1]
        if Mx != 0 and My == 0 and Nz == 0:
            A = np.array([[Mx], [0]])
            B = np.array([[D11, D13], [D13, D33]])
            X = solve(B, A)
            rx = 1/X[0]
            ry = 1/X[1]
        eps0 = X[2]
        epsb = eps0 + 1/rx * ConcreteX + 1/ry * ConcreteY
        epsS = eps0 + 1/rx * RebarX + 1/ry * RebarY
        for i in range(len(epsb)):
            sigmab[i] = sigmab_func(epsb[i])
            #if epsb[i] > 0: sigmab[i] = 0
        for i in range(len(epsS)):
            sigmaS[i] = sigmas_func(epsS[i])
        Mxr = np.dot(sigmab * ConcreteArea, ConcreteX) + np.dot(sigmaS * RebarArea, RebarX)
        Myr = np.dot(sigmab * ConcreteArea, ConcreteY) + np.dot(sigmaS * RebarArea, RebarY)
        Nzr = np.dot(sigmab, ConcreteArea) + np.dot(sigmaS, RebarArea)
        if Nz != 0: deltaNz = abs((Nz - Nzr)/Nz)
        if Mx != 0: deltaMx = abs((Mx - Mxr)/Mx)
        if My != 0: deltaMy = abs((My - Myr)/My)
        nub = sigmab / (Eb * epsb)
        nus = sigmaS / (Es * epsS)
    return sigmab, epsb, sigmaS, epsS