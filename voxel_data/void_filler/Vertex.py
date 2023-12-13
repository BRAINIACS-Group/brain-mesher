# -*- coding: utf-8 -*-
"""
Created on Wed May 24 09:41:33 2023

@author: grife
"""
import numpy as np

class Vertex():
    splitter = "-"
    
    def __init__(self, x,y,z):
        self.key = self.create_key(x, y, z)
        self.adjacentNodes = {}
    
    def addNeighbour(self, vertex):
        if hasattr(vertex, 'key'):
            self.adjacentNodes[vertex.key] = vertex
        else:
            print("Error: this object has not attribute: 'key'. Is this a vertex object?")
    
    def addNeighbours(self, vertices):
        for vertex in vertices:
            if hasattr(vertex, 'key'):
                self.adjacentNodes[vertex.key] = vertex
            else:
                print("Error: this object has not attribute: 'key'. Is this a vertex object?")
    
    def isEqual(self, compareVertex):
        if hasattr(compareVertex, 'key'):
            vertex_location = np.array(self.get_location());
            compare_vertex_location = np.array(compareVertex.get_location());
            if ((vertex_location[0] == compare_vertex_location[0]) and
                (vertex_location[1] == compare_vertex_location[1]) and
                (vertex_location[2] == compare_vertex_location[2])):
                return True  
            return False
        else:
            print("Error: this object has not attribute: 'key'. Is this a vertex object?")
            return None
            
    def create_key(self, x, y, z):
        return str(x) + Vertex.splitter + str(y) + Vertex.splitter + str(z)
    
    @classmethod
    def create_a_key(self, x, y, z):
        return str(x) + Vertex.splitter + str(y) + Vertex.splitter + str(z)
        
    def get_location(self):
        return [int(k) for k in self.key.split(Vertex.splitter)]
        
        