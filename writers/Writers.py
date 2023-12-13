# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 08:18:00 2023

@author: grife
"""
from abc import ABC, abstractmethod
from re import sub


class IWriter(ABC):
    
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
    def openWriter(self, filename, path):
        pass
    
    @abstractmethod
    def saveAndClose(self):
        pass
    
    @abstractmethod
    def writeNodes(self, renumber):
        pass
    
    @abstractmethod
    def writeElements(self, renumber):
        pass
    
class BaseWriter():
    
    """
    An base class used to define methods for mesh writers

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
        
    def openWriter(self, filename, path):
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
        
        if len(filename.split('.'))>1:
            filename = filename.split('.')[0]
            filename.replace("/","")
        filenameOUT = filename + "_" + self.__tag__.upper()
        self.__filename__ = filenameOUT
        
        self.f = open(path + filenameOUT + "." + self.__ext__, 'w')

    def saveAndClose(self):        
        """
        Saves and closed file.
        """ 
        self.f.close()
        print("Completed")
        print("New {} file written to ".format(self.__tag__ .upper()) +
              (self.__path__ + self.__filename__).replace("\\", "/"))
        
    def initializeMesh(self, mesh):
        """
        Initialize mesh object to be written
        Parameters
        ----------
        mesh : Mesh
            mesh object to be written
        """
        self.__mesh__ = mesh
        
    def mesh_statistics(self, file=None):
        """
        Prints the number of nodes, elemenst and boundary surfaces in the mesh object.
        """
        if file is None:
            print("MESH STATISTICS: ")
            print("\tNumber of nodes: " + str(len(self.__mesh__.nodes)))
            print("\tNumber of elements: " + str(len(self.__mesh__.elements)))
            if (len(self.__mesh__.boundaryElements)>0):
                print("\tNumber of boundary surfaces: " + str(len(self.__mesh__.boundaryElements)))
        else:
            file.write("MESH STATISTICS: ")
            file.write("\tNumber of nodes: " + str(len(self.__mesh__.nodes)))
            file.write("\tNumber of elements: " + str(len(self.__mesh__.elements)))
            if (len(self.__mesh__.boundaryElements)>0):
                file.write("\tNumber of boundary surfaces: " + str(len(self.__mesh__.boundaryElements)))

    
class ABQWriter(BaseWriter,IWriter):
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
        super().__init__("inp","abq")
        

    def openWriter(self, filename, path):
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
        super().openWriter(filename, path)
        # from datetime import date
        # firstLine = "# UCD SCRIPT\n" \
        #     + "# Inp file created using python script BrainHexMesh\n"\
        #     + "# Script developed by Emma Griffiths ca. 2022\n"\
        #     + "# UCD file created on " + date.today().isoformat() + "\n"
        # self.f.write(firstLine)        
    
    def writeNodes(self,  reNumber):
        """
        Write nodes in the abaqus format: 
            'node number',  coord1,   coord2,...coordn
        Parameters
        ----------
        reNumber : boolean
            deteremines whetheer the node numbers shoudl be renumbered or not.
        """ 
        nodeMap =  self.__mesh__.nodes
        self.f.write("*NODE\n")
        self.oldNumToNewNum = {}
        print("Writing node data")
        count = 0
        for count,n in enumerate(nodeMap.keys()):
            if reNumber:
                nodeNum = count+1
            else:
                nodeNum = n
            self.oldNumToNewNum[n] = nodeNum
            self.f.write(str(nodeNum) + ",\t" + ",\t".join([str(round(i,6)) for i in nodeMap[n].getCoords()])+"\n")
    
    def writeElements(self, reNumber):
        """
        Write elements in the abaqus format: 
            'element number',  node1,   node2,...nodeN
        This method calls the writeMaterialsData.    
        
        Parameters
        ----------
        reNumber : boolean
            deteremines whether the element numbers should be renumbered or not.
        """ 
        elementMap = self.__mesh__.elements
        self.oldELemTonewELem = {}
        self.f.write("*ELEMENT, TYPE=C3D8, ELSET=ALL\n")
        print("Writing element data")
        for count,e in enumerate(elementMap.keys()):
            assert len(elementMap[e].ica) == 8
            if reNumber:
                elemNum = count+1
            else:
                elemNum = e
            self.oldELemTonewELem[e] = elemNum
            self.f.write(str(elemNum) + ",\t" + ", ".join([str(self.oldNumToNewNum[i.number]) for i in elementMap[e].ica])+"\n")           
            
        self.writeMaterialsData()
            
    def writeMaterialsData(self):
        """
        Write materials property of the elements.
        This methods creates element sets of the material properties 
        associated with the elements and writes the elset data to file.
        
        """ 
        elements = self.__mesh__.elements
        materialToElements = {}
        for num,element in elements.items():
            materials = element.getMaterial()
            for material in materials:
                if materialToElements.get(material,False):
                    materialToElements[material].append(num)
                else:
                    materialToElements[material] = [num]
        for elsetName,elset_elements in materialToElements.items():
            print("Writing elset data: E" + str(int(elsetName)).upper())
            self.f.write("*ELSET, ELSET=E" + str(int(elsetName)).upper() + '\n')
            elset_elements.sort()
            for x in range(0,len(elset_elements),15):
                str_to_write = ", ".join([str(self.oldELemTonewELem[y]) for y in elset_elements[x:x+15]])
                self.f.write(str_to_write)
                self.f.write("\n")
        pass
    
class VTKWriter(BaseWriter,IWriter):
    """
    A class to write data in a format suitable for Paraview usinf vtk version 2.0.
    This class inherits methods from the Base writer class.
    This class implents the Iwriter interface

    Methods
    -------
    openWriter(filename, path)
        open a file using the given path and filename
    saveAndClose()
        save and close the file
    """
    
    def __init__(self):
        super().__init__("vtk","vtk")  

    def openWriter(self, filename, path):
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
        super().openWriter(filename, path)        
        from datetime import date
        firstLine = "# vtk DataFile Version 2.0\n" \
        + "VTK file created using python script BrainHexMesh script developed by Emma Griffiths"\
        + " ca. 2022 file created on " + date.today().isoformat() \
        + " to view: https://www.paraview.org/download/\n\n" \
        + "ASCII\n" \
        + "DATASET UNSTRUCTURED_GRID\n\n"
        self.f.write(firstLine)  
    
    def writeNodes(self, renumber):
        """
        Write nodes in the vtk format: 
            coord1 coord2 ... coordn
        Parameters
        ----------
        renumber : boolean
            deteremines whetheer the node numbers shoudl be renumbered or not.
        """ 
        nodeMap = self.__mesh__.nodes
        self.__nodeKeys__ = []
        numNodes = len(nodeMap)
        self.f.write(" ".join(["\nPOINTS",str(numNodes),"float"]) + "\n")
        nodeKeys = nodeMap.keys()
        nodeKeys = sorted(nodeKeys)
        count = 0
        self.node_num_map_old_to_new = {}
        for n in nodeKeys:
            nodeNum = count 
            self.__nodeKeys__.append(n)
            self.node_num_map_old_to_new[n] = nodeNum
            self.f.write(" ".join([str(float(coord)) for coord in nodeMap[n].getCoords()]) + "\n")
            count += 1
    
    def writeElements(self, renumber):
        """
        Write elements in the vtk format:
            - First line defining the total number elements and the 
            total number of int to be written.
            
            - numnodes  node1   node2 ... nodeN
            
            - list fo cell types (12 for hex, 9 for quad)
        This method calls the writeMaterialsData.    
        
        Parameters
        ----------
        renumber : boolean
            deteremines whether the element numbers should be renumbered or not.
        """ 
        elementMap = self.__mesh__.elements
        boundaryElementMap = self.__mesh__.boundaryElements
        # Writing cell data
        numHexElements = len(elementMap)
        numQuadElements = len(boundaryElementMap)
        num_elements = numHexElements + numQuadElements
        self.f.write(" ".join(["\nCELLS",str(num_elements),
                          str(int(numHexElements*9) + int(numQuadElements*5))]) + "\n")
        # element_count = 0
        for element in elementMap.values():
            # element_count += 1
            # elements = list(elements[:4]) + list(elements[4:])        
            # elementNum = element_count
            renumber_ica = []
            
            for ica_node in element.ica:
                renumber_ica.append(self.node_num_map_old_to_new[ica_node.number])

            
            self.f.write("8 " + " ".join([str(node) for node in renumber_ica]) + "\n")
        # element_count = 0
        for element in boundaryElementMap.values():
            # element_count += 1
            # elements = list(elements[:4]) + list(elements[4:])        
            # elementNum = element_count
            renumber_ica = []    
            
            for ica_node in element.ica:
                renumber_ica.append(self.node_num_map_old_to_new[ica_node.number])
            
            self.f.write("4 " + " ".join([str(node) for node in renumber_ica]) + "\n")
            
        #Writing cell types
        self.f.write("\nCELL_TYPES " + str(num_elements) + "\n")
        for cell in range(numHexElements):
            self.f.write("12\n")    
        for cell in range(numQuadElements):
            self.f.write("9\n")
        
        self.writeMaterialsData()
    
    def writeMaterialsData(self):
        """
        Write materials property of the elements as scalar cell data.
        
        This methods calls the 'writePointData' method
        
        """ 
        elementMap = self.__mesh__.elements
        boundaryElementMap = self.__mesh__.boundaryElements
        numHexElements = len(elementMap)
        numQuadElements = len(boundaryElementMap)
        num_elements = numHexElements + numQuadElements
        
        hexElemKeys = elementMap.keys()
        hexElemKeys = sorted(hexElemKeys)
        #Writing cell data
        self.f.write("\nCELL_DATA " + str(num_elements) + "\n")
        self.f.write("SCALARS material int 1\n")
        self.f.write("LOOKUP_TABLE default\n")
        for num,e in elementMap.items():
            material = e.getMaterial()[0]
            self.f.write(str(int(material)) + "\n")
        for num,e in boundaryElementMap.items():
            material = e.getMaterial()[0]
            self.f.write(str(int(material)) + "\n")            
        
        self.writeCellData()
        self.writePointData()
        
    def writeCellData(self):
        elementMap = self.__mesh__.elements
        cell_data = self.__mesh__.cellData
        if len(cell_data)>0:
            self.f.write("FIELD FieldData {}\n".format(len(cell_data)))
        for d in cell_data: 
            data = elementMap[list(elementMap.keys())[0]].properties.get(d,False)
            if (data):
                dataSize = len(data)
                self.f.write("{} {} {} float\n".format(d, dataSize, len(elementMap)))
                for num,e in elementMap.items():
                    data = e.properties.get(d,[0]*dataSize)
                    line = sub("[\[\]\(\),]*", '', str(data))
                    self.f.write(line + "\n")


    def writePointData(self):
        """ 
        This method writes any data stored at the nodes
        """
        nodes = self.__mesh__.nodes
        nodeKeys = self.__nodeKeys__
        dataToWrite = self.__mesh__.dataToWrite
        
        #Writing point data
        for d in dataToWrite:
            dataSize = len(nodes[list(nodes.keys())[0]].data.get(d))
            self.f.write("\nPOINT_DATA " + str(len(nodes)) + "\n")
            self.f.write("FIELD FieldData {} \n".format(len(dataToWrite)))
            self.f.write("{} {} {} float\n".format(d, dataSize, len(nodes)))
            for nodeNum in nodeKeys:
                n = nodes[nodeNum]
                data = n.data.get(d,[0]*dataSize)
                line = sub("[\[\]\(\),]*", '', str(data))
                self.f.write(line + "\n")

class UCDWriter(BaseWriter,IWriter):
    """
    A class to write data in a format suitable for dealii import.
    This class inherits methods from the Base writer class.
    This class implents the Iwriter interface

    Methods
    -------
    openWriter(filename, path)
        open a file using the given path and filename
    saveAndClose()
        save and close the file
    """
    
    def __init__(self):
        super().__init__("inp","ucd") 

    def openWriter(self, filename, path):
        """Open file to be written to given path and filename as defined
        by the super class BaseWriter. The first line of this 
        file is also written as well as the lien summarizing the number of 
        nodes and elements

        Parameters
        ----------
        filename : string
            filename of writer
        path : string
            path to filename
        """ 
        super().openWriter(filename, path)
    
    def writeNodes(self, renumber):
               
        """
        Write nodes in the ucd format: 
            nodenum   coord1   coord2   ...   coordn
        Parameters
        ----------
        renumber : boolean
            deteremines whetheer the node numbers shoudl be renumbered or not.
        """ 
        
        from datetime import date
        firstLine = "# UCD SCRIPT\n" \
            + "# Inp file created using python script BrainHexMesh\n"\
            + "# Script developed by Emma Griffiths ca. 2022\n"\
            + "# UCD file created on " + date.today().isoformat() + "\n"
        self.f.write(firstLine)
        numNodes = len(self.__mesh__.nodes)
        numElements = len(self.__mesh__.elements)+ len(self.__mesh__.boundaryElements)
        self.f.write("\t".join([str(numNodes),str(numElements),'0','0','0']) + "\n") # Data summary row
        
        nodeMap = self.__mesh__.nodes
        nodeKeys = nodeMap.keys()
        nodeKeys = sorted(nodeKeys)
        count = 0
        self.node_num_map_old_to_new = {}
        for n in nodeKeys:
            nodeNum = count       
            self.node_num_map_old_to_new[n] = nodeNum
            self.f.write(str(nodeNum) + "\t" + "\t".join([str(node) for node in nodeMap[n].getCoords()]) + "\n")
            count += 1
        
    
    def writeElements(self, renumber):
        """
        Writes hex elements in the ucd format:
            - element_num   material_num   hex   node1   node2 ... nodeN
        This method calls the writeBoundaryElements.    
        
        Parameters
        ----------
        renumber : boolean
            deteremines whether the element numbers should be renumbered or not.
        """ 
        element_count = 0
        
        for e in self.__mesh__.elements.values():
            element_count += 1
            material = material = e.getMaterial()[0]
                    
            ica = [int(n.number) for n in e.ica]
            ica = list(ica[:4]) + list(ica[4:])  
            renumber_ica = []
            for ica_node in ica:
                renumber_ica.append(self.node_num_map_old_to_new[ica_node])
                
                
            self.f.write(str(e.num) + "\t" + str(int(material)) + "\t " + "hex" + "\t")
            self.f.write("\t".join([str(n) for n in renumber_ica])+ "\n")
            
        self.writeBoundaryElements(renumber)
    
    def writeBoundaryElements(self,renumber):
        """
        Write boundary elements in the ucd format:
            - element_num   material_num   quad   node1   node2 ... nodeN
        This method calls the writeBoundaryElements.    
        
        Parameters
        ----------
        renumber : boolean
            deteremines whether the element numbers should be renumbered or not.
        """
        element_count = 0
        
        for e in self.__mesh__.boundaryElements.values():
            element_count += 1
            material = material = e.getMaterial()[0] 
            ica = [int(n.number) for n in e.ica]
            renumber_ica = []
            for ica_node in ica:
                renumber_ica.append(self.node_num_map_old_to_new[ica_node])                
                
            self.f.write(str(e.num) + "\t" + str(int(material)) + "\t " + "quad" + "\t")
            self.f.write("\t".join([str(n) for n in renumber_ica])+ "\n")        
    
class Writer(): 
    
    """
    A class to open and write data to a specific the writer as specificed.

    Methods
    -------
    openWriter(filetype, filename,filePath, mesh)
        create a writer object given the filetype specifed.
        open a file using the given path and filename.
    writeMeshData():
        Write node and element data to file.
    saveAndClose()
        save and close the file
    """
    
    def openWriter(self, filetype, filename, filePath):
        """Open file to be written to given path and filename as defined
        by the super class BaseWriter. The first line of this 
        file is also written as well as the lien summarizing the number of 
        nodes and elements

        Parameters
        ----------
        filetype : string
            filetype of writer
        filename : string
            filename of writer
        filePath : string
            path to filename
        
        Raises
        ----------
        Exception raised if unsupported filetype selected
        """ 
        self.fileType = filetype
        if filetype == "abaqus":
            self.writer = ABQWriter()
        elif filetype == "vtk":
            self.writer = VTKWriter()
        elif filetype == "ucd":
            self.writer = UCDWriter()
        else:
            raise Exception("File writer of type {} is unsupported. Please select one from 'ucd','vtk' or 'abaqus'".format(filetype))
        self.writer.openWriter(filename,filePath)
    
    def writeMeshData(self, mesh):
        """
        Writes data of mesh object to file

        Parameters
        ----------
        mesh : Mesh
        """ 
        self.writer.initializeMesh(mesh)
        self.writer.writeNodes(True)
        self.writer.writeElements(True)
        self.writer.mesh_statistics()             
    
    def closeWriter(self):
        """
        Saves and Closes file.
        """
        self.writer.saveAndClose()
        self.writer = None