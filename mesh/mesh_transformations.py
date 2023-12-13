# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 12:26:29 2023

@author: grife

Module of functionf used for mesh transformations
"""
from math import pi, cos, sin
import numpy as np

def rotate_mesh(nodeMap, axis=0, degrees=90):
    deg = degrees*pi/180
    if (axis == 0):
        R = np.array([[1,0,0],[0, cos(deg), -1*sin(deg)],[0, sin(deg), cos(deg)]])      
    if (axis == 1):
        R = np.array([[cos(deg),0,sin(deg)],[0, 1, 0],[-1*sin(deg), 0, cos(deg)]])
    if (axis == 2):
        R = np.array([[cos(deg), -1*sin(deg), 0],[sin(deg), cos(deg), 0],[0, 0, 1]])
    for n in nodeMap.values():
        coords = n.getCoords();
        newCoords = np.matmul(np.array(coords),R)
        coords[0] = round(newCoords[0],3)
        coords[1] = round(newCoords[1],3)
        coords[2] = round(newCoords[2],3)
    
def scale_mesh(nodeMap,scale=[1,1,1],reduce=True):
    if reduce:
        scale[0] = 1/scale[0]
        scale[1] = 1/scale[1]
        scale[2] = 1/scale[2]        
    for n in nodeMap.values():
        coords = n.getCoords();
        coords[0] = coords[0]*scale[0]
        coords[1] = coords[1]*scale[1]
        coords[2] = coords[2]*scale[2]

def translate_mesh(nodeMap,distance=[1,1,1]):        
    for n in nodeMap.values():
        coords = n.getCoords()
        coords[0] = coords[0]+distance[0]
        coords[1] = coords[1]+distance[1]
        coords[2] = coords[2]+distance[2]
