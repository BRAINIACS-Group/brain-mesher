# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 12:22:25 2023

@author: grife

Module of functions that us create maps and arrays from given mesh data
"""
    
def create_elements_ica_map(elements):
    elementMap = {}
    for elementNo, element in elements.items():
        elementMap[elementNo] = [int(node.number) for node in element.ica]
    return elementMap

def create_node_coords_map(nodes):
    nodeMap = {}
    for nodeNo, node in nodes.items():
        nodeMap[nodeNo] = node.getCoords()
    return nodeMap

def create_node_to_elem_map(elementICAMap):
    "Creating node to element connectivity"
    nodeToElemMap = {}
    for e,ica in elementICAMap.items():        
        for node in ica:
            if nodeToElemMap.get(node,False):
                elements = nodeToElemMap[node]
            else:
                elements = []
            elements.append(e)
            nodeToElemMap[node] = elements  
    return nodeToElemMap

def create_surface_connectivity(boundary_element_ica_map, nodeToBoundaryElementMap):
    ## Create surface connectivity map
    print("Creating node surface connectivty map")
    surfaceNodeConnectivity = {}
    for node,compoundKeys in nodeToBoundaryElementMap.items():
        connectedNodes = []
        for f in compoundKeys:
            faceICA = boundary_element_ica_map[f] 
            idx = faceICA.index(node)
            idx1 = idx + 1 if idx < 3 else 0
            idx2 = idx -1 if idx > 0 else 3
            connectedNodes.append(faceICA[idx1])
            connectedNodes.append(faceICA[idx2])
        surfaceNodeConnectivity[node] = list(set(connectedNodes))
    return surfaceNodeConnectivity


    
    
  

