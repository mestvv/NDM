import numpy as np
import gmsh
import sys


def getSectionInfo(file):
    # Инициализация gmsh
    gmsh.initialize()

    # Импорт сечения
    gmsh.open(file)

    # Получаем все элементарные объекты
    entities = gmsh.model.getEntities()

    ConcreteTags = []
    ConcreteX = []
    ConcreteY = []
    ConcreteArea = []

    RebarTags = []
    RebarDiam = []
    RebarArea = []
    RebarX = []
    RebarY = []

    for e in entities:
        dim = e[0]
        tag = e[1]
        # Get the mesh nodes for the entity (dim, tag):
        nodeTags, nodeCoords, nodeParams = gmsh.model.mesh.getNodes(dim, tag)

        # Get the mesh elements for the entity (dim, tag):
        elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements(dim, tag)

        # * Does the entity belong to physical groups?
        physicalTags = gmsh.model.getPhysicalGroupsForEntity(dim, tag)
        if len(physicalTags):
            for p in physicalTags:
                n = gmsh.model.getPhysicalName(dim, p)
                if n == "Concrete":
                    ConcretePG = p
                if n.find("Rebar") > -1:
                    RebarTags = np.append(RebarTags, [nodeTags])
                    diam = float(n[6] + n[7]) / 1000  # Получаем диаметр арматуры из имени физической группы
                    RebarDiam = np.append(RebarDiam, [diam])
                    # Вычисляем площадь арматуры
                    RebarArea = np.append(RebarArea, [(3.14 * diam**2)/4])
                    # Получаем координаты арматур
                    RebarX = np.append(RebarX, nodeCoords[0])
                    RebarY = np.append(RebarY, nodeCoords[1])

    # Получаем теги бетонного сечения
    ConcreteEntity = gmsh.model.getEntitiesForPhysicalGroup(2, ConcretePG)
    ConcreteTags = gmsh.model.mesh.getElements(2, ConcreteEntity[0])[1][0]

    # Цикл по всем элементам сетки бетонного сечения
    for i in ConcreteTags:
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
        # Вычисляем координаты центра тяжести конечного элемента относительно начала координат
        X0 = (X1+X2+X3)/3
        Y0 = (Y1+Y2+Y3)/3
        # Поворачиваем систему координат на 90 градусов
        Y01 = Y0
        Y0 = X0
        X0 = -Y01
        # Вычисляем площадь конечных элементов
        Elem_Area = round(0.5 * abs((X2-X1)*(Y3-Y1)-(X3-X1)*(Y2-Y1)), 8)

        ConcreteX = np.append(ConcreteX, [X0])
        ConcreteY = np.append(ConcreteY, [Y0])
        ConcreteArea = np.append(ConcreteArea, [Elem_Area])


    # Поворачиваем систему координат на 90 градусов
    RebarY1 = RebarY
    RebarY = RebarX
    RebarX = - RebarY1

    # Закрытие gmsh
    gmsh.finalize()

    return ConcreteTags, ConcreteX, ConcreteY, ConcreteArea, RebarTags, RebarDiam, RebarArea, RebarX, RebarY

getSectionInfo('Section.msh')