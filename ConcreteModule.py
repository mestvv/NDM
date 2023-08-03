import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

# Класс для задания физико-механических характеристик бетона
class ConcreteClass:
    def __init__(self, B, Eb, Rbn, Rbtn, Rb, Rbt):
        self.B = B
        self.Eb = Eb
        self.Rbn = Rbn
        self.Rbtn = Rbtn
        self.Rb = Rb
        self.Rbt = Rbt

# Класс для получения диаграммы деформирования бетона по Карпенко с учетом температуры
class KarpenkoTemp:
    def __init__(self, ConcreteClass, temp, Lambda):
        self.ConcreteClass = ConcreteClass
        self.temp = temp
        self.Lambda = Lambda
    
    # Метод для расчета диаграммы по нормативным характеристикам бетона
    def Normative(self):
        B = self.ConcreteClass.B
        Eb = self.ConcreteClass.Eb
        Rbn = self.ConcreteClass.Rbn
        Rbtn = self.ConcreteClass.Rbtn
        temp = self.temp
        Lambda = self.Lambda

        beta_temp_E = 1 + 0.2 * (20 - temp) / 90  # Коэффициент изменения модуля упругости бетона при воздействии низких отрицательных температур
        beta_temp_R = 1 + 0.6 * (20 - temp) / 90  # Коэффициент увеличения прочности бетона в вершине диаграммы в зависимости от величины отрицательной температуры t
        beta_temp_eps = 1 + 0.55 * (20- temp) / 90  # Коэффициент изменения деформаций в вершине диаграммы сжатия
        beta_temp_Rt = 1 + 1.3 * (20 - temp) / 90  # Коэффициент увеличения прочности бетона в вершине диаграммы при центральном растяжении

        # Деформации в вершине диаграммы работы бетона при temp = +20
        eps1_b = -B/Eb * Lambda * (1 + (0.8-0.15*B**2/1e4) * Lambda*B/60+0.2*Lambda/B) / (0.12+1.03*B/60+0.2/B)

        sigma1_b_temp = -Rbn * beta_temp_R  # Напряжения в вершине диаграммы сжатия при заданной температуре
        nu1_b = sigma1_b_temp / (eps1_b * beta_temp_eps * Eb * beta_temp_E)  # Коэффициент секущего модуля в вершине диаграммы сжатия

        sigma1_bt_temp = Rbtn * beta_temp_Rt  # Напряжения в вершине диаграммы растяжения при заданной температуре
        nu1_bt = 0.6 + 0.15 * sigma1_bt_temp / 2.5  # Коэффициент секущего модуля в вершине диаграммы растяжения

        # Нисходящая ветвь сжатия
        NUM = 50  # Количество участков для вычисления напряжений
        sigmab = np.linspace(sigma1_b_temp * 0.2, sigma1_b_temp, NUM, dtype=float)
        # Вычисляем уровень напряжений
        eta = np.zeros(len(sigmab))
        for i in range(len(sigmab)):
            eta[i] = sigmab[i] / sigma1_b_temp
        # Вычисляем коэффициент секущего модуля
        nu0 = 2.05 * nu1_b
        omega1 = 1.95 * nu1_b - 0.138
        nub = np.zeros(len(sigmab))
        for i in range(len(sigmab)):
            nub[i] = nu1_b - (nu0 - nu1_b) * (1 - omega1 * eta[i] - (1 - omega1) * eta[i]**2)**0.5
        
        # Восходящая ветвь сжатия
        NUM = 50  # Количество участков для вычисления напряжений
        sigmab1 = np.linspace(sigma1_b_temp, 0, NUM,dtype=float)
        # Вычисляем уровень напряжений
        eta = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            eta[i] = sigmab1[i] / sigma1_b_temp
        # Вычисляем коэффициент секущего модуля
        nu0 = 1
        omega1 = 2 - 2.5 * nu1_b
        nub1 = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            nub1[i] = nu1_b + (nu0 - nu1_b) * (1 - omega1 * eta[i] - (1 - omega1) * eta[i]**2)**0.5
        
        # Объединяем восходящую и нисходящую ветвь сжатия
        sigmab = np.hstack([sigmab, np.delete(sigmab1, 0)])
        nub = np.hstack([nub, np.delete(nub1, 0)])

        # Восходящая ветвь растяжения
        NUM = 50  # Количество участков для вычисления напряжений
        sigmab1 = np.linspace(0, sigma1_bt_temp, NUM, dtype=float)
        # Вычисляем уровень напряжений
        eta = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            eta[i] = sigmab1[i] / sigma1_bt_temp
        # Вычисляем коэффициент секущего модуля
        nu0 = 1
        omega1 = 2 - 2.5 * nu1_bt
        nub1 = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            nub1[i] = nu1_bt + (nu0 - nu1_bt) * (1 - omega1 * eta[i] - (1 - omega1) * eta[i]**2)**0.5
        
        # Объединяем массивы
        sigmab = np.hstack([sigmab, np.delete(sigmab1, 0)])
        nub = np.hstack([nub, np.delete(nub1, 0)])

        # Нисходящая ветвь растяжения
        NUM = 50  # Количество участков для вычисления напряжений
        sigmab1 = np.linspace(sigma1_bt_temp, sigma1_bt_temp * 0.1, NUM, dtype=float)
        # Вычисляем уровень напряжений
        eta = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            eta[i] = sigmab1[i] / sigma1_bt_temp
        # Вычисляем коэффициент секущего модуля
        nu0 = 2.05 * nu1_bt
        omega1 = 1.95 * nu1_bt - 0.138
        nub1 = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            nub1[i] = nu1_bt - (nu0 - nu1_bt) * (1 - omega1 * eta[i] - (1 - omega1) * eta[i]**2)**0.5
        
        # Объединяем массивы
        sigmab = np.hstack([sigmab, np.delete(sigmab1, 0)])
        nub = np.hstack([nub, np.delete(nub1, 0)])

        # Вычисляем относительные деформации
        epsb = np.zeros(len(sigmab))
        for i in range(len(sigmab)):
            epsb[i] = sigmab[i] / (Eb * beta_temp_E * nub[i])

        sigmab_func = interpolate.interp1d(epsb, sigmab, kind = "linear", fill_value='extrapolate')
        epsb_func = interpolate.interp1d(sigmab, epsb, kind = "linear", fill_value='extrapolate')

        return sigmab_func

    # Метод для расчета диаграммы по расчетным характеристикам бетона
    def Design(self):
        B = self.ConcreteClass.B
        Eb = self.ConcreteClass.Eb
        Rb = self.ConcreteClass.Rb
        Rbt = self.ConcreteClass.Rbt
        temp = self.temp
        Lambda = self.Lambda

        beta_temp_E = 1 + 0.2 * (20 - temp) / 90  # Коэффициент изменения модуля упругости бетона при воздействии низких отрицательных температур
        beta_temp_R = 1 + 0.6 * (20 - temp) / 90  # Коэффициент увеличения прочности бетона в вершине диаграммы в зависимости от величины отрицательной температуры t
        beta_temp_eps = 1 + 0.55 * (20- temp) / 90  # Коэффициент изменения деформаций в вершине диаграммы сжатия
        beta_temp_Rt = 1 + 1.3 * (20 - temp) / 90  # Коэффициент увеличения прочности бетона в вершине диаграммы при центральном растяжении

        # Деформации в вершине диаграммы работы бетона при temp = +20
        eps1_b = -B/Eb * Lambda * (1 + (0.8-0.15*B**2/1e4) * Lambda*B/60+0.2*Lambda/B) / (0.12+1.03*B/60+0.2/B)

        sigma1_b_temp = -Rb * beta_temp_R  # Напряжения в вершине диаграммы сжатия при заданной температуре
        nu1_b = sigma1_b_temp / (eps1_b * beta_temp_eps * Eb * beta_temp_E)  # Коэффициент секущего модуля в вершине диаграммы сжатия

        sigma1_bt_temp = Rbt * beta_temp_Rt  # Напряжения в вершине диаграммы растяжения при заданной температуре
        nu1_bt = 0.6 + 0.15 * sigma1_bt_temp / 2.5  # Коэффициент секущего модуля в вершине диаграммы растяжения

        # Нисходящая ветвь сжатия
        NUM = 50  # Количество участков для вычисления напряжений
        sigmab = np.linspace(sigma1_b_temp * 0.2, sigma1_b_temp, NUM, dtype=float)
        # Вычисляем уровень напряжений
        eta = np.zeros(len(sigmab))
        for i in range(len(sigmab)):
            eta[i] = sigmab[i] / sigma1_b_temp
        # Вычисляем коэффициент секущего модуля
        nu0 = 2.05 * nu1_b
        omega1 = 1.95 * nu1_b - 0.138
        nub = np.zeros(len(sigmab))
        for i in range(len(sigmab)):
            nub[i] = nu1_b - (nu0 - nu1_b) * (1 - omega1 * eta[i] - (1 - omega1) * eta[i]**2)**0.5
        
        # Восходящая ветвь сжатия
        NUM = 50  # Количество участков для вычисления напряжений
        sigmab1 = np.linspace(sigma1_b_temp, 0, NUM,dtype=float)
        # Вычисляем уровень напряжений
        eta = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            eta[i] = sigmab1[i] / sigma1_b_temp
        # Вычисляем коэффициент секущего модуля
        nu0 = 1
        omega1 = 2 - 2.5 * nu1_b
        nub1 = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            nub1[i] = nu1_b + (nu0 - nu1_b) * (1 - omega1 * eta[i] - (1 - omega1) * eta[i]**2)**0.5
        
        # Объединяем восходящую и нисходящую ветвь сжатия
        sigmab = np.hstack([sigmab, np.delete(sigmab1, 0)])
        nub = np.hstack([nub, np.delete(nub1, 0)])

        # Восходящая ветвь растяжения
        NUM = 50  # Количество участков для вычисления напряжений
        sigmab1 = np.linspace(0, sigma1_bt_temp, NUM, dtype=float)
        # Вычисляем уровень напряжений
        eta = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            eta[i] = sigmab1[i] / sigma1_bt_temp
        # Вычисляем коэффициент секущего модуля
        nu0 = 1
        omega1 = 2 - 2.5 * nu1_bt
        nub1 = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            nub1[i] = nu1_bt + (nu0 - nu1_bt) * (1 - omega1 * eta[i] - (1 - omega1) * eta[i]**2)**0.5
        
        # Объединяем массивы
        sigmab = np.hstack([sigmab, np.delete(sigmab1, 0)])
        nub = np.hstack([nub, np.delete(nub1, 0)])

        # Нисходящая ветвь растяжения
        NUM = 50  # Количество участков для вычисления напряжений
        sigmab1 = np.linspace(sigma1_bt_temp, sigma1_bt_temp * 0.1, NUM, dtype=float)
        # Вычисляем уровень напряжений
        eta = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            eta[i] = sigmab1[i] / sigma1_bt_temp
        # Вычисляем коэффициент секущего модуля
        nu0 = 2.05 * nu1_bt
        omega1 = 1.95 * nu1_bt - 0.138
        nub1 = np.zeros(len(sigmab1))
        for i in range(len(sigmab1)):
            nub1[i] = nu1_bt - (nu0 - nu1_bt) * (1 - omega1 * eta[i] - (1 - omega1) * eta[i]**2)**0.5
        
        # Объединяем массивы
        sigmab = np.hstack([sigmab, np.delete(sigmab1, 0)])
        nub = np.hstack([nub, np.delete(nub1, 0)])

        # Вычисляем относительные деформации
        epsb = np.zeros(len(sigmab))
        for i in range(len(sigmab)):
            epsb[i] = sigmab[i] / (Eb * beta_temp_E * nub[i])

        sigmab_func = interpolate.interp1d(epsb, sigmab, kind = "linear", fill_value='extrapolate')
        epsb_func = interpolate.interp1d(sigmab, epsb, kind = "linear", fill_value='extrapolate')

        return sigmab_func
    

# Задаем классы бетона
B20 = ConcreteClass(20.0, 27500.0, 15.0, 1.35, 11.5, 0.9)
B25 = ConcreteClass(25.0, 30000.0, 18.5, 1.55, 14.5, 1.05)
B30 = ConcreteClass(30.0, 32500.0, 22.0, 1.75, 17.0, 1.15)