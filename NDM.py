import numpy as np
import gmsh
import sys
from scipy.linalg import solve
import meshio
import ConcreteModule
import RebarModule


# Задание исходных данных
Nz = -2600/1000  # Продольное усилие, МН
Mx = -250/1000  # Изгибающий момент относительно оси Х, МН*м
My = 200/1000  # Изгибающий момент относительно оси Y, МН*м
ConcreteMaterial = ConcreteModule.B25  # Класс бетона
RebarMaterial = RebarModule.A400  # Класс арматуры

# Задание размеров прямоугольного сечения (X - по горизонту, Y - по вертикали)
a = 0.4  # Размер сечения вдоль оси Х
b = 0.6  # Размер сечения вдоль осу Y

# Задание параметров привязки симметричного армирования
a0 = 0.05 # Привязка арматуры от нижней и верхней граней сечения
a1 = 0.05 # Привязка арматуры от боковых торцов сечения


# Создание сетки
gmsh.initialize()
gmsh.model.add("rc_beam")
lc = 0.05  # Размер конечных элементов
# Создание геометрии opencascade
Concrete = gmsh.model.occ.addRectangle(0, 0, 0, a, b, 1)
# Создание арматурных включений. Нумерация начинается со 101
gmsh.model.occ.addPoint(a1, a0, 0, 0, 101)
gmsh.model.occ.addPoint(a-a1, a0, 0, 0, 102)
gmsh.model.occ.addPoint(a1, b-a0, 0, 0, 103)
gmsh.model.occ.addPoint(a-a1, b-a0, 0, 0, 104)
gmsh.model.occ.addPoint(a1, b/2, 0, 0, 105)
gmsh.model.occ.addPoint(a-a1, b/2, 0, 0, 106)
# Задание размеров конечных элементов
gmsh.model.occ.mesh.setSize(gmsh.model.occ.getEntities(0), lc)
gmsh.model.occ.synchronize()
# Создание физической группы бетона
ConcretePG = gmsh.model.addPhysicalGroup(2, [1], name = "Concrete")
# Создание физической группы арматур
RebarPG = gmsh.model.addPhysicalGroup(0, [101, 102, 103, 104, 105, 106], name = "Rebar")
Rebar_Elem_Num = len(gmsh.model.getEntitiesForPhysicalGroup(0, RebarPG))  # Получаем количество узлов арматуры
# Задаем узлам диаметр арматуры
RebarDiam = np.array([], dtype=float)
RebarArea = np.array([], dtype=float)
# Задание диаметров арматуры согласно нумерации
RebarDiam = np.array([0.032, 0.032, 0.032, 0.032, 0.02, 0.02])
for i in range(Rebar_Elem_Num):
    RebarArea = np.append(RebarArea, np.array([(3.14*RebarDiam[i]**2)/4]))
#gmsh.model.mesh.setTransfiniteAutomatic()  # Генерация прямоугольной сетки
# Генерация сетки
gmsh.model.mesh.generate(2)

# Получение координат центра тяжести сечения
CenterOfGravity = gmsh.model.occ.getCenterOfMass(2, 1)

# Получение данных об узлах арматуры
Rebar_elementList = gmsh.model.mesh.getNodesForPhysicalGroup(0, RebarPG)[0]

RebarX = []
RebarY = []

# Получаем координаты арматуры относительно центра тяжести сечения
for i in Rebar_elementList:
    # Получаем координаты арматуры
    X = float(gmsh.model.mesh.getNode(i)[0][0])
    Y = float(gmsh.model.mesh.getNode(i)[0][1])
    # Вычисляем координаты относительно центра тяжести сечения
    X0 = -round((CenterOfGravity[0] - X), 8)
    Y0 = -round((CenterOfGravity[1] - Y), 8)
    # Поворачиваем систему координат на 90 градусов
    Y01 = Y0
    Y0 = X0
    X0 = -Y01
    RebarX = np.append(RebarX, np.array([X0]))
    RebarY = np.append(RebarY, np.array([Y0]))

# Получение всех элементов бетонного сечения
elementList = gmsh.model.mesh.getElements(2, 1)
# Создание массива для хранения данных конечных элементов
Elem_Info = np.empty((0,4), dtype=float)
# Переменная для кол-ва конечных элементов
Conc_Elem_Num = 0
# Цикл по всем элементам сетки
for i in elementList[1][0]:
    # Получаем номера узлов из которых состоит конечный элемент
    Node1 = gmsh.model.mesh.getElement(i)[1][0]
    Node2 = gmsh.model.mesh.getElement(i)[1][1]
    Node3 = gmsh.model.mesh.getElement(i)[1][2]
    # Получаем координаты узлов из которых состоит конечный элемент
    X1 = float(gmsh.model.mesh.getNode(Node1)[0][0])
    X2 = float(gmsh.model.mesh.getNode(Node2)[0][0])
    X3 = float(gmsh.model.mesh.getNode(Node3)[0][0])
    Y1 = float(gmsh.model.mesh.getNode(Node1)[0][1])
    Y2 = float(gmsh.model.mesh.getNode(Node2)[0][1])
    Y3 = float(gmsh.model.mesh.getNode(Node3)[0][1])
    # Вычисляем координаты центра тяжести конечного элемента
    X0 = (X1+X2+X3)/3
    Y0 = (Y1+Y2+Y3)/3
    # Вычисляем координаты центра тяжести конечного элемента относительно центральных осей
    X0 = -round((CenterOfGravity[0] - X0), 8)
    Y0 = -round((CenterOfGravity[1] - Y0), 8)
    # Поворачиваем систему координат на 90 градусов
    Y01 = Y0
    Y0 = X0
    X0 = -Y01
    # Вычисляем площадь конечных элементов
    Elem_Area = round(0.5 * abs((X2-X1)*(Y3-Y1)-(X3-X1)*(Y2-Y1)), 8)
    Elem_Info = np.append(Elem_Info, np.array([[i, X0, Y0, Elem_Area]]), axis=0)
    Conc_Elem_Num = Conc_Elem_Num + 1
# Сохранение файла сетки
gmsh.write("ConcreteSection.msh")

# НАЧАЛО АЛГОРИТМА РЕАЛИЗАЦИИ НДМ
deltaMN = 0.001  # Параметр сходимости

sigmab_func = ConcreteModule.KarpenkoTemp(ConcreteMaterial, 20, 1).Design()
sigmas_func = RebarModule.Rebar2L(RebarMaterial).Design()

# Функция нелинейной деформационной модели
def NDM(Nz, Mx, My):
    # Коэффициенты упругости
    nub = np.array([])
    nus = np.array([])
    for i in range(Conc_Elem_Num):
        nub = np.append(nub, np.array([1]))
    for i in range(Rebar_Elem_Num):
        nus = np.append(nus, np.array([1]))
    deltaMx = 1
    deltaMy = 1
    deltaNz = 1
    sigmab = np.zeros(Conc_Elem_Num)
    sigmaS = np.zeros(Rebar_Elem_Num)
    while deltaNz >= deltaMN and (deltaMx >= deltaMN and deltaMy >= deltaMN):
        D11 = np.dot(Elem_Info[:, 3], (Elem_Info[:, 1])**2 * nub) * ConcreteMaterial.Eb + np.dot(RebarArea, RebarX**2 * nus) * RebarMaterial.Es
        D22 = np.dot(Elem_Info[:, 3], (Elem_Info[:, 2])**2 * nub) * ConcreteMaterial.Eb + np.dot(RebarArea, RebarY**2 * nus) * RebarMaterial.Es
        D12 = np.dot(Elem_Info[:, 3], (Elem_Info[:, 2]) * Elem_Info[:, 1] * nub) * ConcreteMaterial.Eb + np.dot(RebarArea, RebarX * RebarY * nus) * RebarMaterial.Es
        D13 = np.dot(Elem_Info[:, 3], (Elem_Info[:, 1]) * nub) * ConcreteMaterial.Eb + np.dot(RebarArea, RebarX * nus) * RebarMaterial.Es
        D23 = np.dot(Elem_Info[:, 3], (Elem_Info[:, 2]) * nub) * ConcreteMaterial.Eb + np.dot(RebarArea, RebarY * nus) * RebarMaterial.Es
        D33 = np.dot(Elem_Info[:, 3], nub) * ConcreteMaterial.Eb + np.dot(RebarArea, nus) * RebarMaterial.Es
        A = np.array([[Mx], [My], [Nz]])
        B = np.array([[D11, D12, D13], [D12, D22, D23], [D13, D23, D33]])
        X = solve(B, A)
        rx = 1/X[0]
        ry = 1/X[1]
        eps0 = X[2]
        epsb = eps0 + 1/rx * Elem_Info[:, 1] + 1/ry * Elem_Info[:, 2]
        epsS = eps0 + 1/rx * RebarX + 1/ry * RebarY
        for i in range(len(epsb)):
            sigmab[i] = sigmab_func(epsb[i])
            #if epsb[i] > 0: sigmab[i] = 0
        for i in range(len(epsS)):
            sigmaS[i] = sigmas_func(epsS[i])
        Mxr = np.dot(sigmab * Elem_Info[:, 3], Elem_Info[:, 1]) + np.dot(sigmaS * RebarArea, RebarX)
        Myr = np.dot(sigmab * Elem_Info[:, 3], Elem_Info[:, 2]) + np.dot(sigmaS * RebarArea, RebarY)
        Nzr = np.dot(sigmab, Elem_Info[:, 3]) + np.dot(sigmaS, RebarArea)
        deltaNz = abs((Nz - Nzr)/Nz)
        deltaMx = abs((Mx - Mxr)/Mx)
        deltaMy = abs((My - Myr)/My)
        nub = sigmab / (ConcreteMaterial.Eb * epsb)
        nus = sigmaS / (RebarMaterial.Es * epsS)
    return sigmab, epsb, sigmaS, epsS
sigmab, epsb, sigmaS,epsS = NDM(Nz, Mx, My)

# КОНЕЦ АЛГОРИТМА РЕАЛИЗАЦИИ НДМ

t = [0, 0, 0, 0, 0, 0, 0, 0]

# Добавление в постпроцессор данных
t[0] = gmsh.view.add("Areas")
gmsh.view.addHomogeneousModelData(
    t[0], 0, "rc_beam", "ElementData",
    np.transpose(Elem_Info[:,0]),  # tags of elements
    np.transpose(Elem_Info[:,3]))  # data, per element

t[1] = gmsh.view.add("X coordinates of elements")
gmsh.view.addHomogeneousModelData(
    t[1], 0, "rc_beam", "ElementData",
    np.transpose(Elem_Info[:,0]),  # tags of elements
    np.transpose(Elem_Info[:,1]))  # data, per element

t[2] = gmsh.view.add("Y coordinates of elements")
gmsh.view.addHomogeneousModelData(
    t[2], 0, "rc_beam", "ElementData",
    np.transpose(Elem_Info[:,0]),  # tags of elements
    np.transpose(Elem_Info[:,2]))  # data, per element

RebarNodes = gmsh.model.mesh.getNodesForPhysicalGroup(0, RebarPG)[0]
t[3] = gmsh.view.add("Rebar diameters")
gmsh.view.addHomogeneousModelData(
    t[3], 0, "rc_beam", "NodeData",
    RebarNodes,  # tags of nodes
    RebarDiam)  # data, per node

t[4] = gmsh.view.add("Напряжения в бетоне")
gmsh.view.addHomogeneousModelData(
    t[4], 0, "rc_beam", "ElementData",
    np.transpose(Elem_Info[:,0]),  # tags of elements
    np.transpose(sigmab))  # data, per element

t[5] = gmsh.view.add("Относительные деформации в бетоне")
gmsh.view.addHomogeneousModelData(
    t[5], 0, "rc_beam", "ElementData",
    np.transpose(Elem_Info[:,0]),  # tags of elements
    np.transpose(epsb))  # data, per element

t[6] = gmsh.view.add("Напряжения в арматуре")
gmsh.view.addHomogeneousModelData(
    t[6], 0, "rc_beam", "NodeData",
    np.transpose(RebarNodes),  # tags of nodes
    np.transpose(sigmaS))  # data, per element

t[7] = gmsh.view.add("Относительные деформации в арматуре")
gmsh.view.addHomogeneousModelData(
    t[7], 0, "rc_beam", "NodeData",
    np.transpose(RebarNodes),  # tags of nodes
    np.transpose(epsS))  # data, per element

gmsh.view.option.setNumber(t[6], "ShowScale", 0)
gmsh.view.option.setNumber(t[7], "ShowScale", 0)
gmsh.view.option.setNumber(t[3], "ShowScale", 0)

gmsh.view.option.setNumber(t[6], "IntervalsType", 4)
gmsh.view.option.setNumber(t[7], "IntervalsType", 4)
gmsh.view.option.setNumber(t[3], "IntervalsType", 4)

gmsh.view.option.setNumber(t[6], "ScaleType", 2)
gmsh.view.option.setNumber(t[7], "ScaleType", 2)
gmsh.view.option.setNumber(t[3], "ScaleType", 2)

for i in range(8):
    gmsh.view.option.setNumber(t[i], "Visible", 0)


# Визуализация gmsh
if '-nopopup' not in sys.argv:
    gmsh.fltk.run()


# Закрытие gmsh
gmsh.finalize()