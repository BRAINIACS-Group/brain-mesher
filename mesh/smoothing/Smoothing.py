# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 09:41:58 2023

@author: grife
"""
import numpy as np
from math import acos,pi
from numpy.linalg import norm, det, inv

def calculateQualityMetric(coords, UCD_Values=False):

    if UCD_Values:
        coords = np.concatenate((coords[-4:],coords[:4]))
    J = 0
    neighbours = [[1,3,4],
            [2,0,5],
            [3,1,6],
            [0,2,7],
            [7,5,0],
            [4,6,1],
            [5,7,2],
            [6,4,3]]     
    for i in range(8):
        neighbourNodes = neighbours[i]
        vertexNodeCoords = coords[i]
        A = np.zeros([3,3])
        for count,n in enumerate(neighbourNodes):
            neighbourNodeCoords = coords[n]
            A[count] = neighbourNodeCoords - vertexNodeCoords
        if (det(A) > 0):
            inv_A = inv(A)
            kTk = norm(A)*norm(inv_A)
            J += (kTk/3)*(kTk/3)
        else:
            # print("Error: determinant is negative! Element Tangled" ) 
            return -100000
    J = J/8
    J = 1/J
    return J

def calculateAngles(coords):
    coords =  np.concatenate((coords[-4:],coords[:4]))
    neighbours = [[1,3,4],
            [2,0,5],
            [3,1,6],
            [0,2,7],
            [7,5,0],
            [4,6,1],
            [5,7,2],
            [6,4,3]]
    angles = np.zeros([8,3])
    for i in range(8):
        neighbourNodes = neighbours[i];
        vertexNodeCoords = coords[i];
        points = [0,1,2,1,2]
        for count in range(3):
            A = neighbourNodes[points[count]]
            vertexA = coords[A]
            vertexB = vertexNodeCoords
            C = neighbourNodes[points[count + 1]]
            vertexC = coords[C]
            ab = vertexA-vertexB
            cb = vertexC - vertexB
            norm_ab = np.linalg.norm(ab)
            norm_cb = np.linalg.norm(cb)            
            quotient = np.dot(ab,cb)/(norm_ab*norm_cb)
            angle = acos(quotient)*180/pi
            angles[i,count]= angle
    return angles
        
def calculateCurvature(coords,currentNodeCoords):
    dim = 3
    curvature = [0]*dim
    for coord in coords:
       for i in range(dim):
          curvature[i] += (coord[i]/len(coords))
    for i in range(dim):
        curvature[i] = curvature[i] - currentNodeCoords[i]
    return curvature

def value_in_square_bounds(n_coords, bounds, inside=True):
    """
    Determines in 3D coordinates are within the given square bounds

    Parameters
    ----------
    n_coords : array(float)
        3D coordinates.
    bounds : array(float)
        3D square bounds.
    inbounds : bool, optional
        determine is check is for inside bounds given or outside bounds given.

    Returns
    -------
    bool
        Confirmation of in bounded square or not.

    """
    if inside:
        if ( (n_coords[0] > bounds[0]) and (n_coords[0] < bounds[1]) and
                (n_coords[1] > bounds[2]) and (n_coords[1] < bounds[3]) and
                (n_coords[2] > bounds[4]) and (n_coords[2] < bounds[5]) ):
                return True
    else:
        if ( ((n_coords[0] < bounds[0]) or (n_coords[0] > bounds[1])) or
                ((n_coords[1] < bounds[2]) or (n_coords[1] > bounds[3])) or
                ((n_coords[2] < bounds[4]) or (n_coords[2] > bounds[5])) ):
                return True
    return False

def perform_smoothing(iteration, coeffs, surfaceNodeConnectivity, nodeMap, elementICAMap, nodeToElemMap,
                      bounds=None, inBounds=False):
    print("Iteration: " + str(iteration+1))
    newNodePositions = {}
    badElements, tangled_elements, nodesUnsmoothed = [],[],[]
    coeff = coeffs[iteration%2]
    for node, connected in surfaceNodeConnectivity.items():
        currentNodeCoords = nodeMap[node].getCoords()
        if bounds is None or value_in_square_bounds(currentNodeCoords, bounds, inside=inBounds):
            coords = [nodeMap[n].getCoords() for n in connected]
            curvature = calculateCurvature(coords, currentNodeCoords)
            newCoords = np.array(currentNodeCoords) + coeff*np.array(curvature)
            newNodePositions[node] = newCoords
            for e_num in nodeToElemMap[node]:
                e_ica = elementICAMap[e_num]
                elemCoords = np.zeros([8, 3])
                for count, n_num in enumerate(e_ica):
                    elemCoords[count] = newNodePositions.get(n_num, nodeMap[n_num].getCoords())
                metric = calculateQualityMetric(elemCoords)
                if metric < 0.2:
                    newNodePositions.pop(node)
                    if metric < -10000:
                        tangled_elements.append(e_num)
                    else:
                        badElements.append(e_num)
                        nodesUnsmoothed.append(node)
                    break
                    
    badElements = list(set(badElements))
    nodesUnsmoothed= list(set(nodesUnsmoothed))
    print("Number of unsmoothed nodes: " + str(len(nodesUnsmoothed)))
    print("Number of elements affected: " + str(len(badElements)))
    print("Number of tangled elements: " + str(len(tangled_elements)))
    for node, newcoords in newNodePositions.items():
        changedNode = nodeMap[node]
        changedNode.setCoords(newcoords)
