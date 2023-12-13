
from abc import ABC, abstractmethod

from mesh.Mesh import Mesh
from mesh.Node import Node
from mesh.Element import HexElement, QuadElement
from readers.vtkReader import readVtk
from vtk import vtkIdList


class IReader(ABC):
    """
    An abstract class used to define methods for mesh writers

    Abstract Methods
    -------
    openWriter(filename, path)
        open a file using the given path and filename
    saveAndClose()
        save and close the file
    writeNodes(renumber)
        write nodes and node data to file
    writeElements(renumber)
        write element and element data to file
    """

    @abstractmethod
    def openReader(self, filename, path):
        pass

    @abstractmethod
    def closeReader(self):
        pass

    @abstractmethod
    def getMesh(self) -> Mesh:
        pass


class BaseReader(ABC):
    """
    A base class used to define methods for mesh writers

    Methods
    -------
    openWriter(filename, path)
        open a file using the given path and filename
    saveAndClose()
        save and close the file
    initializeMesh(mesh)
        Initialize mesh object to be written
    mesh_statistics(renumber)
        print out data for the mesh written
    """

    def __init__(self, ext, tag):
        """
        Parameters
        ----------
        ext : str
            The extension of the file to be written
        tag : str
            The unique tag to identify the type of writer
        """
        self.__ext__ = ext
        self.__tag__ = tag
        self.__filename__ = ''
        self.mesh = Mesh()

    def openReader(self, filename, path):
        """Open file to be written to given path and filename.
        If the path does not end if separtor characters thes are added.
        If file name contains an extension, this is removed and replaced the
        tag of the writer '__tag__' and the correct extension '__ext__'

        Parameters
        ----------
        filename : string
            filename of writer
        path : string
            path to filename
        """
        if (path[-1] != "/"):
            path += "/"
        self.__path__ = path

        self.__filename__ = filename

        self.f = open(path + filename + "." + self.__ext__, 'r')

    def closeReader(self):
        """
        Saves and closed file.
        """
        print("Completed")


    @abstractmethod
    def readNodes(self):
        pass

    @abstractmethod
    def readElements(self):
        pass


class ABQReader(BaseReader, IReader):
    """
    A class to write data in a format suitable for Abaqus.
    This class inherits methos from the Base writer class.
    This class implents the Iwriter interface

    Methods
    -------
    openWriter(filename, path)
        open a file using the given path and filename
    saveAndClose()
        save and close the file
    """

    def __init__(self):
        super().__init__("inp", "abq")
        self.node_lines = []
        self.element_lines = []
        self.elset_lines = {}

    def closeReader(self):
        """
        Saves and closed file.
        """
        self.f.close()
        super().closeReader()

    def getMesh(self) -> Mesh:
        self.readNodes()
        self.readElements()
        return self.mesh

    def openReader(self, filename, path):
        """Open file to be written to given path and filename as defined
        by the super class BaseWriter. The first line of this
        file is also written

        Parameters
        ----------
        filename : string
            filename of writer
        path : string
            path to filename
        """
        super().openReader(filename, path)
        start_nodes = False
        start_elements = False
        start_elsets = False
        elset_name = None
        for line in self.f:
            line = "".join(line.split()).upper()
            if line != '':
                if "**" in line:
                    start_nodes = False
                    start_elements = False
                    start_elsets = False

                elif "*NODE" in line:
                    start_nodes = True
                    start_elements = False
                    start_elsets = False

                elif "*ELEMENT" in line:
                    start_nodes = False
                    start_elements = True
                    start_elsets = False

                elif "*ELSET" in line:
                    start_nodes = False
                    start_elements = False
                    start_elsets = True
                    splitLine = line.split(",")
                    elset_name = splitLine[1].split("=")[1]
                    assert not self.elset_lines.get(elset_name,False), " elset {} already exists".format(elset_name)
                    self.elset_lines[elset_name] = []

                elif start_nodes:
                    self.node_lines.append(line)

                elif start_elements:
                    self.element_lines.append(line)

                elif start_elsets:
                    assert elset_name is not None
                    self.elset_lines[elset_name].append(line)

    def readNodes(self):
        node_map = {}
        for line in self.node_lines:
            split_line = line.split(",")
            node_number = int(split_line[0].strip())
            coords = [float(x) for x in split_line[1:]]
            new_node = Node(node_number, coords)
            node_map[node_number] = new_node
        self.mesh.nodes = node_map

    def readElements(self):
        element_map = {}
        boundary_elements = {}
        for line in self.element_lines:
            split_line = line.split(",")
            element_number = int(split_line[0].strip())
            ica = [int(x) for x in split_line[1:]]
            node_ica = []
            for n in ica:
                node_ica.append(self.mesh.nodes.get(n))
            if len(ica) == 8:
                new_element = HexElement(element_number, node_ica)
                element_map[element_number] = new_element
            elif len(ica) == 4:
                new_element = QuadElement(element_number, node_ica)
                boundary_elements[element_number] = new_element

        self.mesh.elements = element_map
        self.mesh.addBoundaryElements(boundary_elements)

        self.getMaterialsData()

    def getMaterialsData(self):
        for name, lines in self.elset_lines.items():
            mat = int(name.replace("E", ""))
            for line in lines:
                elements = [int(x.strip()) for x in line.split(",")]
                for e in elements:
                    element = self.mesh.elements.get(e, None)
                    if element is not None:
                        element.addMaterial(mat)

class UCDReader(BaseReader,IReader):

    def __init__(self):
        super().__init__("inp", "ucd")
        self.num_elements = None
        self.num_nodes = None
        self.grid = None

    def getMesh(self) -> Mesh:
        self.readNodes()
        self.readElements()
        return self.mesh

    def closeReader(self):
        """
        Saves and closed file.
        """
        self.f.close()
        super().closeReader()

    def openReader(self, filename, path):
        super().openReader(filename, path)
        line = self.f.readline()
        while line.split()[0] == '#':
            line = self.f.readline()
        initial_line = line.split('\t')
        self.num_nodes = int(initial_line[0])
        self.num_elements = int(initial_line[1])


    def readNodes(self):
        """
        Write nodes in the vtk format:
            coord1 coord2 ... coordn
        Parameters
        ----------
        renumber : boolean
            deteremines whetheer the node numbers shoudl be renumbered or not.
        """
        node_map = {}
        for i in range(self.num_nodes):
            node_line = self.f.readline().split("\t")
            number = int(node_line[0])
            coords = [float(x) for x in node_line[1:]]
            new_node = Node(number, coords)
            node_map[number] = new_node
        self.mesh.nodes = node_map

    def readElements(self):
        element_map = {}
        boundary_elements = {}
        for i in range(self.num_elements):
            element_line = self.f.readline().split("\t")
            number = int(element_line[0])
            material = int(element_line[1])
            type = element_line[2].strip()
            ica = [int(x) for x in element_line[3:]]
            node_ica = [self.mesh.nodes[x] for x in ica]
            if type == 'hex':
                new_element = HexElement(number, node_ica, mat=[material])
                element_map[number] = new_element
            elif type == 'quad':
                new_element = QuadElement(number, node_ica, mat=[material])
                boundary_elements[number] = new_element
        self.mesh.elements = element_map
        self.mesh.addBoundaryElements(boundary_elements)


class VTKReader(BaseReader, IReader):

    def __init__(self):
        super().__init__("vtk", "vtk")
        self.grid = None

    def getMesh(self) -> Mesh:
        self.readNodes()
        self.readElements()
        return self.mesh

    def openReader(self, filename, path):
        if (path[-1] != "/"):
            path += "/"
        self.grid = readVtk(path, filename)

    def readNodes(self):
        """
        Write nodes in the vtk format:
            coord1 coord2 ... coordn
        Parameters
        ----------
        renumber : boolean
            deteremines whetheer the node numbers shoudl be renumbered or not.
        """
        num_points = self.grid.GetNumberOfPoints()
        node_map = {}
        for x in range(num_points):
            point = self.grid.GetPoint(x)
            new_node = Node(x, point)
            node_map[x] = new_node
        self.mesh.nodes = node_map


    def readElements(self):
        element_map = {}
        boundary_elements = {}
        for k in range(self.grid.GetNumberOfCells()):
            cellIds = vtkIdList()
            self.grid.GetCellPoints(k, cellIds)
            node_ica = []
            for i in range(cellIds.GetNumberOfIds()):
                pointId = cellIds.GetId(i)
                node_ica.append(self.mesh.nodes[pointId])
            if cellIds.GetNumberOfIds() == 8:
                new_element = HexElement(k,node_ica)
                element_map[k] = new_element
            elif cellIds.GetNumberOfIds() == 4:
                new_element = QuadElement(k,node_ica)
                boundary_elements[k] = new_element
        self.mesh.elements = element_map
        self.mesh.addBoundaryElements(boundary_elements)

        self.readMaterialsData()

    def readMaterialsData(self):
        cell_data = self.grid.GetCellData()
        number_arrays =cell_data.GetNumberOfArrays()
        number_elements = len(self.mesh.elements)
        for i in range(number_arrays):
            arr = cell_data.GetArray(i)
            arr_name = arr.GetName()
            if "material" in arr_name:
                for e in range(arr.GetNumberOfValues()):
                    mat = arr.GetValue(e)
                    element = self.mesh.elements.get(e, None)
                    if element is None:
                        element = self.mesh.boundaryElements.get(e, None)
                    assert element is not None, "Error in reader: Element does not exist in mesh"
                    element.addMaterial(mat)
            else:
                for e in range(arr.GetNumberOfValues()):
                    data = arr.GetValue(e)
                    element = self.mesh.elements.get(e, None)
                    if element is not None:
                        element.addProperty(arr_name, data)
                self.mesh.cellData.append(arr_name)
        self.readPointData()

    def readPointData(self):
        cell_data = self.grid.GetPointData()
        number_arrays = cell_data.GetNumberOfArrays()
        for i in range(number_arrays):
            arr = cell_data.GetArray(i)
            arr_name = arr.GetName()
            for n in range(arr.GetNumberOfValues()):
                data = arr.GetValue(n)
                node = self.mesh.nodes.get(n, None)
                if node is not None:
                    node.addData(arr_name, data)
            self.mesh.dataToWrite.append(arr_name)


class Reader(IReader):

    def __init__(self, file_type):
        self.reader = None
        file_type = file_type.lower()
        if file_type == 'vtk':
            self.reader = VTKReader()
        elif file_type == 'ucd':
            self.reader = UCDReader()
        elif file_type == 'abaqus' or file_type == 'abq':
            self.reader = ABQReader()

    def openReader(self, filename, path):
        filename_split = filename.split(".")
        if len(filename_split) > 1:
            filename = ".".join(filename.split(".")[:-1])
        self.reader.openReader(filename, path)

    def closeReader(self):
        self.reader.closeReader()
        self.reader = None

    def getMesh(self) -> Mesh:
        return self.reader.getMesh()





