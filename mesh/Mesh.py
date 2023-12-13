# -*- coding: utf-8 -*-
"""
Created on Thu May 25 15:39:38 2023

@author: grife
"""
import warnings

from mesh.smoothing import Smoothing as smooth
import mesh.mesh_utils as mu
import mesh.mesh_transformations as mt
from mesh.Node import Node
from mesh.Element import HexElement, QuadElement
import numpy as np


class Mesh:
    """
    A class used to store and manipulate mesh data

    Attributes
    ----------
    elements : Map(int,Element)
        Dictionary of elements. 
        Key: element number
        Value: Element object
    nodes : Map(int,Node)
         Dictionary of nodes. 
         Key: node number
         Value: Node object
    boundaryElements : Map(int,Element)
        Dictionary of elements. 
        Key: element number
        Value: Element object
    elementToPointCloud: Map(int, array(int)
        Dictionary between element numbers and the original point cloud values
        Key: element number
        Value: ARrayof length 4: x-coord, y-coord, z-coord, material
    dataToWrite: Array(string)
        Array of string of data stored at mesh nodes
    nodeToElements: Map(int, array(int))
        Dictionary giving the elements that are connected to one node
        Key: node number
        Value: Array of elements that are connected to it

    Methods
    -------
    addBoundaryElements(boundaryElementsMap)
        merges new boundary element map with existing one
    getBoundingBox()
        get bounding box of mesh
    locate_boundary_element_map(elementsNotIncluded=[])
        gets map of boundary element if elements with material value in 'elementsNotIncluded' are removed
    remove_region(region_value)
        removes elements with material label = region_value
    create_mesh_from_Point_Cloud(pointData, voxel_size)
        creates mesh from point cloud data with elements the size of 'voxel_size'
    clean_mesh(elementsNotIncluded = [], replace=0)
        cleans mesh by removing/replacing elements and nodes that are incorrectely joined. 
        Elements with material value in 'elementsNotIncluded' are not considered. 
        If 'replace' != 0 elements are not removed but thier material is changed to the value of 'replace'
    replace_outer_region(white_matter_label, replace_label, elements_on_boundary)
        replaced any element in 'elements_on_boundary' that have the value 'white_matter_label'
        and are replcaed with 'replace_label'
    __clean_mesh_nodes(elementsNotIncluded = [], replace=0), private
        cleans mesh by removing/replacing elements that are joined by only one node,
        Elements with material value in 'elementsNotIncluded' are not considered. 
        If 'replace' != 0 elements are not removed but their material is changed to the value of 'replace' 
    __clean_mesh_edges(elementsNotIncluded = [], replace=0), private
        cleans mesh by removing/replacing elements that have edges connected to less than 4 other elements,
        Elements with material value in 'elementsNotIncluded' are not considered. 
        If 'replace' != 0 elements are not removed but their material is changed to the value of 'replace'
    delete_element(element_number)
        deletes element 'element_number' from mesh
    replace_element(element_number, replace=24)
        replace element 'element_number' with material specified by 'replace'
    smooth_mesh(coeffs, iterations, boundary_element_map)
        performed Laplacian smoothing on boundary surfaces of elements in 'boundary_element_map'
    __get_edge_without_shared_face(edgesToElements_map), private
        gets edges of elements that do not share a face with an ajoing element, i.e. only joined by edge and not face 
    __calculate_node_coords(elementX,elementY,elementZ,i,size)
        calculates the coordinates of a node given the number of elements in the x, y and z direction, 
        the node number 'i' and the size of the voxels
    center_mesh(region)
        transalte mesh to be centered about teh given region 'region'
    """
    def __init__(self):
        self.elements = {}
        self.nodes = {}
        self.boundaryElements = {}
        self.elementToPointCloud = {}
        self.dataToWrite = []
        self.cellData = []
        self.boundaryNodeToElements = {}
        
    def addBoundaryElements(self, boundaryElementsMap):
        """Merges new boundary element map to existing map.

        Parameters
        ----------
        boundaryElementsMap : Map(int,Element)
            Dictionary of elements. 
            Key: element number
            Value: Element object
        """
        self.boundaryElements = {**self.boundaryElements, **boundaryElementsMap}
        self.boundaryNodeToElements = mu.create_node_to_elem_map(mu.create_elements_ica_map(self.boundaryElements))

    def addElements(self, new_elements):
        self.elements = {**self.elements, **new_elements}

    def addNodes(self, new_nodes):
        self.nodes = {**self.nodes, **new_nodes}
    
    def getBoundingBox(self, regions = -1):
        """Gets the boundign box for the mesh.
        Parameters
        ----------
        region: array[int], Optional
        Optional paremeter to boundary box around selected regions.
        Default is an empty list
        
        Outputs
        ----------
        [maxX,maxY,maxZ,minX,minY,minZ]: array (ints):
            list givign thmax and minimum vlaues fo the bounding box
        """
        if (regions == -1):
            nodeMap = list(self.nodes.values())
        else:
            nodeMap = []
            nodesAdded = []
            for e in self.elements.values():
                if e.getMaterial().count(regions):
                    for n in e.ica:
                       if not nodesAdded.count(n.number):
                           nodeMap.append(n);
                           nodesAdded. append(n.number)
                           
        maxV = [-1000,-1000,-1000]
        minV = [1000,1000,1000]        
        for node in nodeMap:
            n = node.getCoords();
            for d in range(3):
                if maxV[d]<n[d]:
                    maxV[d] = n[d]
                if minV[d]>n[d]:
                    minV[d] = n[d]
        return maxV + minV
    
    def locate_boundary_element_map(self,elementsNotIncluded=[]):
        """Gets the boundary faces of the model if the element with materials values
        in 'elementsNotIncluded' are not considered.
        
        Parameters
        ----------
        elementsNotIncluded : Array(ints), optional
            list of materials values to not be included when looking for boundary elements.
            Default is an empty list
        
        Outputs
        ----------
        Map(string,array(ints))
            Map with a compound key and a list of integers associated with the nodes
            Key: 'quadElement number'-'face number'
            Value: ica of boundary face
        """
        print("Locating boundary elements")
        face_to_elems_map = {}
        surface_face_to_elems_map = {}
        elementToOrderedFaces = {}
        for element in self.elements.values():
            add = self.__element_included(element,elementsNotIncluded)
            if add:
                list_of_faces = element.get_faces(True,True)
                for face_key in list_of_faces:                                             # Create map key 
                    if face_to_elems_map.get(face_key,False):                            # Check if face key already in map
                       face_to_elems_map[face_key].append(element)                    # key already in face so append element to array (NOT surface face)
                       if surface_face_to_elems_map.get(face_key,False):                   # If previously classified as a free surface; remove from this map
                           del surface_face_to_elems_map[face_key]
                    else:
                        face_to_elems_map[face_key] = [element]                                   # If not in map, add to map
                        surface_face_to_elems_map[face_key] = element
                        elementToOrderedFaces[element.num] = list_of_faces
            
        boundary_element_map = {}
        for face_key,e in surface_face_to_elems_map.items():    
            faces = elementToOrderedFaces[e.num]
            for face_num,f in enumerate(faces):
                if f == face_key:
                    compound_key = "-".join([str(e.num),str(face_num)])
                    boundary_element_map[compound_key] = e.get_faces(False,False)[face_num]
                    break    
        
        return boundary_element_map
    
    def __element_included(self,element,elementsNotIncluded):            
        add = True
        for el_types in element.getMaterial():
            if elementsNotIncluded.count(el_types):
                add = False
                break
        return add
     
    def remove_region(self,region_value):
        """Removes an elements with material properties 'region_values'

        Parameters
        ----------
        region_value : int
            material property value of region to be removed
        """
        element_keys = list(self.elements.keys())    
        for element_num in element_keys:
            e = self.elements[element_num]
            if e.getMaterial().count(region_value):
                self.delete_element(element_num)
                    
    def create_mesh_from_Point_Cloud(self, pointData, voxel_size):
        """Creates hexahedral elements from point cloud data.
        Size of the element is deteremined by 'voxel_size'.
        mesh data stored in elements and nodes properties
        
        Uses 'create_node_to_elem_map' and 'create_elements_ica_map' methods
        from MeshUtils module.

        Parameters
        ----------
        pointData : nx4 array
            point data of n points with columns 0:3 specifying coordinates 
            and column 3 giving the material label
        voxel_size : int
            length of edge of the element
        """
        [minX,minY,minZ] = pointData[:,:3].min(axis=0)
        [maxX,maxY,maxZ] = pointData[:,:3].max(axis=0)
        
        elementX = maxX-minX+1
        elementY = maxY+1
        elementZ = maxZ+1
        
        elementNo = 0;
        for p in pointData:
            elementNo += 1
            [x,y,z,m] = p
            startNode = (z+1) + (elementZ+1)*y + ((elementZ+1)*(elementY+1))*x
            element_ica_numbers = [int(startNode+1), int(startNode), int(startNode+(elementZ+1)) ,int(startNode+(elementZ+1)+1)]
            element_ica_tmp = []
            element_ica_nodes = []
            for i in element_ica_numbers:                  
                if not self.nodes.get(i,False):
                    coords = self.__calculate_node_coords(elementX,elementY,elementZ,i,voxel_size)
                    node = Node(i,coords)
                    self.nodes[i] = node
                else:
                    node = self.nodes[i]
                element_ica_nodes.append(node)
                
                newNode = int(i + (elementZ+1)*(elementY+1)) 
                if not self.nodes.get(newNode,False):
                    coords = self.__calculate_node_coords(elementX,elementY,elementZ,newNode,voxel_size)
                    node = Node(newNode,coords);
                    self.nodes[newNode] = Node(newNode,coords)
                else:
                    node = self.nodes[newNode]
                element_ica_tmp.append(node)
                    
            element_ica_nodes += element_ica_tmp
            element = HexElement(elementNo, element_ica_nodes, mat=[m])
            self.elements[int(elementNo)] = element
            self.elementToPointCloud[int(elementNo)] = [x,y,z,m]
        self.nodeToElements = mu.create_node_to_elem_map(mu.create_elements_ica_map(self.elements));
    
    
    def clean_mesh(self, elementsNotIncluded = [], replace=0):
        """
        Cleans mesh by removing poorly connected edges and nodes. 
        This process is done iteratively on the mesh until no more issues are found 
        or max interation number (10) is reached.
        Elements with material property specified in 'elementsNotIncluded' are
        not considered. If 'replace' != 0, the element material property is changed 
        otherwise element is deleted.

        Parameters
        ----------
        elementsNotIncluded : Array(ints), optional
            list of materials values to not be included when looking for boundary elements
            Default is an empty list
        replace : int, optional
            material property to replace elements. If replace = 0, elements are deleted.
            Default is 0
        """
        iteration = 0
        count = 1
        total_count = 0
        while ((count > 0) and (iteration<10)):
            count = 0;
            iteration += 1
            count += self.__clean_mesh_edges(elementsNotIncluded = elementsNotIncluded, replace=replace);
            count += self.__clean_mesh_nodes(elementsNotIncluded = elementsNotIncluded, replace=replace);
            if ((replace != 0) and (iteration == 1)):
                elementsNotIncluded.append(replace);
            total_count += count;
        print(str(total_count) + " elements deleted/replaced due to poor node/edge connectivity in " + str(iteration) + " iterations")
        
    def replace_outer_region(self, incorrect_label, elements_on_boundary):
        """
        Replaced any element in 'elements_on_boundary' list that have the value 'white_matter_label'
        nd are replcaed with 'replace_label'

        Parameters
        ----------
        incorrect_label : int
            material property to be replaced
        replace_label : int
            material property to be used to replace 'white_matter_label'
        elements_on_boundary : Array(ints)
            list of element numbers
        """

        print("Cleaning brain boundary")

        elementICA = mu.create_elements_ica_map(self.elements)
        self.nodeToElements = mu.create_node_to_elem_map(elementICA)
        for elem in elements_on_boundary:
            element = self.elements[elem]
            materials = element.getMaterial()
            if materials.count(incorrect_label):
                connected_elements = []
                for n in element.ica:
                    eles = self.nodeToElements[n.number]
                    connected_elements += eles
                connected_elements = list(set(connected_elements))
                mats = []
                for x in connected_elements:
                    mat = self.elements[x].getMaterial()
                    if not self.elements[x].getMaterial().count(incorrect_label):
                        mats += mat

                if (len(mats)>0):
                    [modes, count] = np.unique(mats, return_counts=True)
                    modeIndices, = np.where(count == max(count))
                    modeIndex = modeIndices[0]
                    replacedValue = modes[modeIndex]
                    materials.remove(incorrect_label)
                    materials.insert(0,replacedValue)
                else:
                    print("materials not replaced")
        
        
    def __clean_mesh_nodes(self, elementsNotIncluded = [], replace=0):
        """
        Private method used to identify elemnts that are joined by only one node.
        These elements are then either deleted (if replace ==0) or the material 
        property of that element is changed to 'replace' (if replace != 0). 
        Elements with material value in 'elementsNotIncluded' are not considered. 
        

        Parameters
        ----------
        elementsNotIncluded : Array(ints), optional
            list of materials values to not be included when looking for boundary elements
            Default is an empty list
            
        replace : int, optional
            material property to replace elements. If replace = 0, elements are deleted
            Default is 0
        """
        cleaned_elements = []
        cleaned_nodes= []
        node_keys = list(self.nodes.keys())
        for key in node_keys:
            if not cleaned_nodes.count(key):
                All_connectedElements = self.nodeToElements[key]
                connectedElements = []
                for conn_element in All_connectedElements:
                    element = self.elements[conn_element]
                    add = self.__element_included(element,elementsNotIncluded)
                    if add:
                        connectedElements.append(conn_element)
                if len(connectedElements) == 2:
                    element1 = self.elements[connectedElements[0]]
                    element2 = self.elements[connectedElements[1]]
                    ele2Ica = [int(n.number) for n in element2.ica]
                    numberSharedNodes = 0
                    for node1 in element1.ica:
                        if ele2Ica.count(node1.number)>0:
                            numberSharedNodes += 1
                    assert numberSharedNodes>0;
                    if numberSharedNodes == 1:
                        if not cleaned_elements.count(element2.num):
                            cleaned_elements.append(element2.num)
                            cleaned_nodes = cleaned_nodes + ele2Ica
                            if (replace != 0) or (len(elementsNotIncluded) != 0):
                                self.replace_element(element2.num,replace=replace)
                            else:
                                self.delete_element(element2.num) 
        # print(str(len(cleaned_elements)) + " element deleted due to poor node connectivity")
        return len(cleaned_elements)
    
    def __clean_mesh_edges(self, elementsNotIncluded = [], replace=0):
        """
        Private method used to identify elemnts that are joined by only one edge,
        i.e. an edge that is connected to less than 4 other elements.
        These elements are then either deleted (if replace ==0) or the material 
        property of that element is changed to 'replace' (if replace != 0). 
        Elements with material value in 'elementsNotIncluded' are not considered.
        
        Uses '__create_edge_to_element_connectivity' method from MeshUtils module.        
        

        Parameters
        ----------
        elementsNotIncluded : Array(ints), optional
            list of materials values to not be included when looking for boundary elements
            Default is an empty list
        replace : int, optional
            material property to replace elements. If replace = 0, elements are deleted.
            Default is 0
        """
        edgesToElementsMap = self.__create_edge_to_element_connectivity(elementsNotIncluded)
        edgesToElements = self.__get_edge_without_shared_face(edgesToElementsMap)
        old_node_to_new = {}
        cleaned_elements = []
        for edge, edgeConnectedElements in edgesToElements.items():
            if not cleaned_elements.count(edgeConnectedElements[0]) and not cleaned_elements.count(edgeConnectedElements[1]):
                nodes = [int(n) for n in edge.split("-")]
                element1 = self.elements[edgeConnectedElements[0]]
                element2 = self.elements[edgeConnectedElements[1]] 
                for n in nodes:
                    nodeNum = n
                    if not old_node_to_new.get(nodeNum,False):                        
                        allConnectedElements = self.nodeToElements[nodeNum] 
                        connectedElements = []
                        for conn_element in allConnectedElements:
                            element = self.elements[conn_element]
                            add = self.__element_included(element,elementsNotIncluded)
                            if add:
                                connectedElements.append(conn_element)
                        if len(connectedElements) <= 4:
                            if not cleaned_elements.count(element2.num):
                                cleaned_elements.append(element2.num)
                                if (replace != 0) or (len(elementsNotIncluded) != 0):
                                    self.replace_element(element2.num,replace=replace)
                                else:                                
                                    self.delete_element(element2.num)
        return len(cleaned_elements)
    
    def __create_edge_to_element_connectivity(self,elementsNotIncluded= []):
        edgesToElements_tmp = {}
        for element in self.elements.values():
            add = self.__element_included(element,elementsNotIncluded)
            if add:
                edges = element.get_edges(stringyfy=True, order=True)
                for edge in edges:
                    connectedElements = []
                    if edgesToElements_tmp.get(edge,False):
                        connectedElements = edgesToElements_tmp[edge]
                    else:
                        edgesToElements_tmp[edge] = connectedElements
                    connectedElements.append(element.num)
        return edgesToElements_tmp
    
    def locate_elements_on_boundary(self, elementsNotIncluded = []):
        print("Locating elements on the boundary")
        face_to_elems_map = {}
        surface_face_to_elems_map = {}
        for e,element in self.elements.items(): 
            add = self.__element_included(element,elementsNotIncluded)
            if add:
                list_of_faces = element.get_faces(True,True)
                for face_key in list_of_faces:                                             # Create map key 
                    if face_to_elems_map.get(face_key,False):                            # Check if face key already in map
                       connected_elements =  face_to_elems_map[face_key]                    # key already in face so append element to array (NOT surface face)
                       connected_elements.append(e)
                       if surface_face_to_elems_map.get(face_key,False):                   # If previously classified as a free surface; remove from this map
                           del surface_face_to_elems_map[face_key]
                    else:
                        face_to_elems_map[face_key] = [e]                                   # If not in map, add to map
                        surface_face_to_elems_map[face_key] = e
            
        elements_on_boundary = []
        for face_key,e in surface_face_to_elems_map.items():    
            if not elements_on_boundary.count(e):
                    elements_on_boundary.append(e) 
        
        return elements_on_boundary

    def delete_element(self, element_number):
        """
        Deletes elements from the mesh. To do this elements are deleted from 
        the element map, nodes that are no longer connected to any elements are deleted
        and these elements and, if applicable, nodes are removed from the nodeToElement connectivity map

        Parameters
        ----------
        element_number : int
            element number to be deleted
        """
        if self.elements.get(element_number, False):
            element = self.elements[element_number]
            for n in element.ica:
                connectedElements = self.nodeToElements[n.number]
                connectedElements.remove(element_number)
                if (len(connectedElements) == 0):
                    self.nodeToElements.pop(n.number)
                    if not (self.boundaryNodeToElements.get(n.number, False)):
                        self.nodes.pop(n.number)
            self.elements.pop(element_number)
        
    def replace_element(self, element_number, replace=24):
        """
        Changes an elements material property to that specified by 'replace'

        Parameters
        ----------
        element_number : int
            element number to be deleted
        replace : int, optional
            new material property.
            Default is 24 (CSF)
        """
        element = self.elements[element_number]
        element.setMaterial(replace)   

    # def create_boundary_elements(self, element_mat_number, elements_not_included=None, boundaryTest=None):
    #
    #     if elements_not_included is None:
    #         elements_not_included = []
    #
    #     boundary_elements_map = {}
    #     boundary_number = max(self.elements.keys()) if len(self.boundaryElements) == 0 else max(
    #         self.boundaryElements.keys())
    #     boundary_elements = self.locate_boundary_element_map(elementsNotIncluded=elements_not_included)
    #
    #     for compoundKey, ica in boundary_elements.items():
    #         boundary_number += 1
    #         ica_nodes = [self.nodes[n] for n in ica]
    #         boundary_element = QuadElement(boundary_number, ica_nodes, mat=[element_mat_number])
    #         [element_num, face] = [int(x) for x in compoundKey.split("-")]
    #         # [xc,yc,zc,m] = e_centroids[element_num]
    #         Boundary = True
    #         if not boundaryTest is None:
    #             Boundary = boundaryTest.validElement(element_num)
    #         if Boundary:
    #             boundary_elements_map[boundary_number] = boundary_element
    #         else:
    #             boundary_number -= 1
    #
    #     self.addBoundaryElements(boundary_elements_map)
    #     return True

    def smooth_mesh(self, coeffs, iterations, elementsNotIncluded=[], bounds = None, inside=False):
        """
        Prepares information and performs Laplacian smoothing the boundary of a mesh
        where the elements with material type given in 'elementsNotIncluded'
        are not included.
        
        Uses 'create_node_to_elem_map', 'create_elements_ica_map' and 'create_surface_connectivity'
        methods from MeshUtils module. 

        Parameters
        ----------
        coeffs : [float,float]
            two Laplacian smoothing coefficients
        iterations : int
            number of iterations of Laplcians smoothing to performed
        elementsNotIncluded : Array(ints), optional
            list of materials values to not be included when looking for boundary elements
            Default is an empty list
        
        Raises
        ----------
        Error raised if morethn or less than 2 coefficeints are given in 'coeffs'
        """
        print("Starting mesh smoothing")
        
        boundary_element_map = self.locate_boundary_element_map(elementsNotIncluded=elementsNotIncluded)
        assert len(coeffs)==2, "Laplacian smoothing requires for two coefficients"
        if len(boundary_element_map) > 0:
            node_to_boundary_element_map = mu.create_node_to_elem_map(boundary_element_map)
            surfaceNodeConnectivity = mu.create_surface_connectivity(boundary_element_map,node_to_boundary_element_map)
            surfaceNodeKeys = list(surfaceNodeConnectivity.keys())
            # This followign loop prevents previously smoothed nodes/regions from being affected by latter smoothed regions
            # as smoothing should be done from most to least important region
            for node_number in surfaceNodeKeys:
                node = self.nodes[node_number]
                touched = node.getData('touched')
                if len(touched) == 0:
                    node.addData('touched', [1])
                else:
                    surfaceNodeConnectivity.pop(node_number)
            elementICAMap = mu.create_elements_ica_map(self.elements)
            nodeToElemMap = mu.create_node_to_elem_map(elementICAMap)
            assert len(coeffs) == 2, "Please provide (only) 2 coefficient, one positive and one negative. Positive value must be greater than absolute fo negative value"
            if coeffs[0] > 0:
                assert coeffs[0] >= abs(coeffs[1]), "First coefficient must be greater than absolute of the second (negative) coefficient"
            elif coeffs[1] > 0:
                assert coeffs[1] >= abs(coeffs[2]), "Second coefficient must be greater than absolute of the first (negative) coefficient"

            for iteration in range(iterations):
                smooth.perform_smoothing(iteration, coeffs, surfaceNodeConnectivity, self.nodes, elementICAMap, nodeToElemMap=nodeToElemMap, bounds=bounds, inBounds=inside)
        else:
            print("No elements selected to smooth")
                           
                
    def __get_edge_without_shared_face(self,edgesToElements_map):
        """
        Locates edges that are have adjacents faces that are not shared between elements.
        I.e. the elements are only joined by one shred edge.

        Parameters
        ----------
        edgesToElements_map : Map(string,array(ints))
            Map of edge icas concatenated into a string and the elemenst to which they are connected.
            Key: string of two nodes making the edge
            Value: list of element to which they are connected
        
        Outputs
        ----------
        edgesToElements : Map(string,array(ints))
            Map of edge icas that do not share a face concatenated into a string 
            and the two elements to which they are connected.
            Key: string of two nodes making the edge
            Value: list of 2 element to which they are connected
        """
        edgesToElements = {}
        for edge, elements in edgesToElements_map.items():
            if len(elements) == 2:
                element1 = elements[0]
                element2 = elements[1]
                faces1 = self.elements[element1].get_faces(order = True, stringyfy = True)
                faces2 = self.elements[element2].get_faces(order = True, stringyfy = True)
                shared_face = False
                for face in faces1:                    
                    if faces2.count(face):
                        shared_face = True
                        break
                if not shared_face:
                    edgesToElements[edge]= list(elements)
        return edgesToElements
    
    def __calculate_node_coords(self,elementX,elementY,elementZ,i,size):
        """
        Calculates the coordinates of a node based on the node number given by 'i'
        and the maximum number of elements in a pointcloud. The characteristic 
        length of the element length is given by 'size'.

        Parameters
        ----------
        elementX : int
            Total number of elements given in the X direction
        elementY : int
            Total number of elements given in the Y direction
        elementZ : int
            Total number of elements given in the Z direction
        i: int
            node number within grid fully populated rectabgular grid
        sezie: float
            characteristic size of an element
        
        Outputs
        ----------
        array(ints)
            Array containing the x,y and z coordinates of a node
        """
        coordx = int((i-1)/((elementZ+1)*(elementY+1)))
        tmp = i - (coordx*((elementZ+1)*(elementY+1)))
        coordy = int((tmp-1)/(elementZ+1))
        coordz = (tmp - (coordy*(elementZ+1)))-1
        return [float(d) for d in [coordx*size, coordy*size, coordz*size]]
    
    def center_mesh_by_region(self, region=None):
        """
        Moves the center of the mesh to the center of the region specified by 'region'
        to the nearest integer.
        Uses 'translate_mesh' method from MeshTransformations module.

        Parameters
        ----------
        region : int
            material property of region about which mesh should be centered
        """
        middle_of_cc = [-1*int(round(x)) for x in self.get_center_of_region(region)]
        # Move mesh
        mt.translate_mesh(self.nodes, distance=middle_of_cc)
        
        
    def get_center_of_region(self,region=None):
        """
        Find center of a region in the mesh

        Parameters
        ----------
        region : int
            Rgeion material type.

        Returns
        -------
        array[float]
            Center of region

        """
        centroid = [0,0,0]
        num_elements = 0
        # Find centroid of corpus callosum
        for e in self.elements.values():
            if region is None or (e.getMaterial()[0] == region):
                e_centroid = e.calculate_element_centroid()
                num_elements += 1
                for d in range(len(e_centroid)):
                  centroid[d] += e_centroid[d];
        return [float(x/num_elements) for x in centroid]
        
    def create_elements_map(self, elementsNotIncluded, elementsIncluded = []):
        """
        Creates a map of element numbers to elements of elements with material propeties not
        included in 'elementsNotIncluded'. If only elements with certain material 
        properties are to be selected these are specified in elementsIncluded.

        Parameters
        ----------
        elements : Map(int, Element)
            Dictionary of element numbers to 
        elementsNotIncluded : TYPE
            DESCRIPTION.
        elementsIncluded : TYPE, optional
            DESCRIPTION. The default is [].

        Returns
        -------
        elementMap : TYPE
            DESCRIPTION.

        """
        elementMap = {}
        for elementNo, element in self.elements.items():
            add = self.__element_included(element, elementsNotIncluded)
            if add:                
                if len(elementsIncluded)>0:
                    for el_types in elementsIncluded:
                        if element.getMaterial().count(el_types):
                            elementMap[elementNo] = element
                else:
                    elementMap[elementNo] = element
        return elementMap

    def create_boundary(self, boundary_test_fx, element_mat_number, excluded_regions=[]):
        boundary_elements_map = {}
        boundary_number = max(self.elements.keys()) if len(self.boundaryElements) == 0 else max(
            self.boundaryElements.keys())
        boundary_elements = self.locate_boundary_element_map(elementsNotIncluded=excluded_regions)
        for compoundKey, ica in boundary_elements.items():
            boundary_number += 1
            ica_nodes = [self.nodes[n] for n in ica]
            boundary_element = QuadElement(boundary_number, ica_nodes, mat=element_mat_number)
            [element_num, face] = [int(x) for x in compoundKey.split("-")]
            # [xc,yc,zc,m] = e_centroids[element_num]
            boundary = True
            if boundary_test_fx is not None:
                boundary = boundary_test_fx.validElement(element_num)
            if boundary:
                boundary_elements_map[boundary_number] = boundary_element
            else:
                boundary_number -= 1
        print("{} boundary elements created with material number {}"
              .format(len(boundary_elements_map), element_mat_number))
        self.addBoundaryElements(boundary_elements_map)
    

        
         
        