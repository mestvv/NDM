import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate


# Класс для задания физико-механических характеристик арматуры
class RebarClass:
    def __init__(self, Es, Rsn, Rs, Rsc, Rsc1):
        self.Es = Es
        self.Rsn = Rsn
        self.Rs = Rs
        self.Rsc = Rsc
        self.Rsc = Rsc1


# Класс для получения двухлинейной диаграммы деформирования арматуры по СП 63.13330 (Диаграмма Прандтля)
class Rebar2L:
    def __init__(self, RebarClass):
        self.RebarClass = RebarClass
    
    # Метод для получения нормативной диаграммы
    def Normative(self):
        Es = self.RebarClass.Es
        Rsn = self.RebarClass.Rsn
        eps_s0 = Rsn / Es
        eps_s2 = 0.025
        sigma_s = [-Rsn, -Rsn, 0, Rsn, Rsn]
        eps_s = [-eps_s2 * 5, -eps_s0, 0, eps_s0, eps_s2 * 5]
        sigma_s1 = interpolate.interp1d(eps_s, sigma_s, fill_value='extrapolate')
        return sigma_s1
    
    # Метод для получения расчетной диаграммы
    def Design(self):
        Es = self.RebarClass.Es
        Rs = self.RebarClass.Rs
        eps_s0 = Rs / Es
        eps_s2 = 0.025
        sigma_s = [-Rs, -Rs, 0, Rs, Rs]
        eps_s = [-eps_s2 * 5, -eps_s0, 0, eps_s0, eps_s2 * 5]
        sigma_s1 = interpolate.interp1d(eps_s, sigma_s, fill_value='extrapolate')
        return sigma_s1


# Задаем классы арматуры
A400 = RebarClass(2e5, 390, 340, 340, 340)
A500 = RebarClass(2e5, 500, 435, 435, 400)