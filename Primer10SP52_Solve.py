import gmsh
import sys
import ConcreteModule
import RebarModule
import SectionModule
import NdmModule


# Задание исходных данных
Nz = 0 # Продольное усилие, МН
Mx = 82.6/1000  # Изгибающий момент относительно оси Х, МН*м
My = 0  # Изгибающий момент относительно оси Y, МН*м
ConcreteMaterial = ConcreteModule.B25  # Класс бетона
RebarMaterial = RebarModule.A400SP52  # Класс арматуры
deltaMN = 0.001  # Параметр сходимости

# Получаем функции напряжений от относительных деформаций
sigmab_func = ConcreteModule.KarpenkoTemp(ConcreteMaterial, 20, 1).Design()
sigmas_func = RebarModule.Rebar2L(RebarMaterial).Design()

# Импорт сечения
ConcreteTags, ConcreteX, ConcreteY, ConcreteArea, RebarTags, RebarDiam, RebarArea, RebarX, RebarY = SectionModule.getSectionInfo("Primer10SP52.msh")

# Вычисляем координаты элементов относительно заданной системы координат
ConcreteX, ConcreteY, RebarX, RebarY = SectionModule.getXY(-0.04, 0.06, ConcreteX, ConcreteY, RebarX, RebarY)

# Запуск алгоритма НДМ
sigmab, epsb, sigmaS,epsS = NdmModule.NDM(Nz, Mx, My, ConcreteMaterial.Eb, sigmab_func, RebarMaterial.Es, sigmas_func, ConcreteX, ConcreteY, ConcreteArea, RebarX, RebarY, RebarArea, deltaMN)


# Добавление данных в постпроцессор
t = [0, 0, 0, 0, 0, 0, 0, 0]

t[0] = gmsh.view.add("Areas")
gmsh.view.addHomogeneousModelData(
    t[0], 0, gmsh.model.getCurrent(), "ElementData",
    ConcreteTags,  # tags of elements
    ConcreteArea)  # data, per element

t[1] = gmsh.view.add("X coordinates of elements")
gmsh.view.addHomogeneousModelData(
    t[1], 0, gmsh.model.getCurrent(), "ElementData",
    ConcreteTags,  # tags of elements
    ConcreteX)  # data, per element

t[2] = gmsh.view.add("Y coordinates of elements")
gmsh.view.addHomogeneousModelData(
    t[2], 0, gmsh.model.getCurrent(), "ElementData",
    ConcreteTags,  # tags of elements
    ConcreteY)  # data, per element

t[3] = gmsh.view.add("Rebar diameters")
gmsh.view.addHomogeneousModelData(
    t[3], 0, gmsh.model.getCurrent(), "NodeData",
    RebarTags,  # tags of nodes
    RebarDiam)  # data, per node

t[4] = gmsh.view.add("Напряжения в бетоне")
gmsh.view.addHomogeneousModelData(
    t[4], 0, gmsh.model.getCurrent(), "ElementData",
    ConcreteTags,  # tags of elements
    sigmab)  # data, per element

t[5] = gmsh.view.add("Относительные деформации в бетоне")
gmsh.view.addHomogeneousModelData(
    t[5], 0, gmsh.model.getCurrent(), "ElementData",
    ConcreteTags,  # tags of elements
    epsb)  # data, per element

t[6] = gmsh.view.add("Напряжения в арматуре")
gmsh.view.addHomogeneousModelData(
    t[6], 0, gmsh.model.getCurrent(), "NodeData",
    RebarTags,  # tags of nodes
    sigmaS)  # data, per element

t[7] = gmsh.view.add("Относительные деформации в арматуре")
gmsh.view.addHomogeneousModelData(
    t[7], 0, gmsh.model.getCurrent(), "NodeData",
    RebarTags,  # tags of nodes
    epsS)  # data, per element

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