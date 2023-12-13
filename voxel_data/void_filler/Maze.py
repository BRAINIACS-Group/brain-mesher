# -*- coding: utf-8 -*-
"""
Created on Wed May 24 09:33:52 2023

@author: grife
"""
from voxel_data.void_filler.Vertex import Vertex
import numpy as np

class Maze():
    
    def __init__(self, grid):
        self.grid = grid
    
    def get_end_point(self,x,y,z):
        current_dimensions = self.grid.shape
        xEnd = 0 if (x < (current_dimensions[0]-x)) else (current_dimensions[0]-1);
        yEnd = 0 if (y < (current_dimensions[1]-y)) else (current_dimensions[1]-1);
        zEnd = 0 if (z < (current_dimensions[2]-z)) else (current_dimensions[2]-1);
        return [xEnd,yEnd,zEnd];        
        
    def find_zero_neighbours(self, x, y, z):
        neighbours = [];
        n = 1;
        gridSize = self.grid.shape
        # Check if x-neighbours are voids or filled
        if (x != (gridSize[0]-1)):
            adjPoint = self.grid[x+1,y,z]
            if (adjPoint == 0):
                newVert = Vertex(x+1,y,z)
                neighbours.append(newVert)
                n += 1;
        if (x != 0):
            adjPoint = self.grid[x-1,y,z]
            if (adjPoint == 0):
                newVert = Vertex(x-1,y,z)
                neighbours.append(newVert)
                n += 1;
        # Check if y-neighbours are voids or filled        
        if (y != (gridSize[1]-1)):
            adjPoint = self.grid[x,y+1,z]
            if (adjPoint == 0):
                newVert = Vertex(x,y+1,z)
                neighbours.append(newVert)
                n += 1;
        if (y != 0):
            adjPoint = self.grid[x,y-1,z]
            if (adjPoint == 0):
                newVert = Vertex(x,y-1,z)
                neighbours.append(newVert)
                n += 1;
        # Check if z-neighbours are voids or filled        
        if (z != (gridSize[2]-1)):
            adjPoint = self.grid[x,y,z+1]
            if (adjPoint == 0):
                newVert = Vertex(x,y,z+1)
                neighbours.append(newVert)
                n += 1;
        if (z != 0):
            adjPoint = self.grid[x,y,z-1]
            if (adjPoint == 0):
                newVert = Vertex(x,y,z-1)
                neighbours.append(newVert)
                n += 1;
        return neighbours
    
    def isExit(self,x,y,z):
        if (( np.sum(self.grid[0:x,y,z]) == 0 ) or
                ( np.sum(self.grid[x:,y,z]) == 0 ) or
                ( np.sum(self.grid[x,0:y,z]) == 0 ) or
                ( np.sum(self.grid[x,y:,z]) == 0 ) or
                ( np.sum(self.grid[x,y,0:z]) == 0 ) or
                ( np.sum(self.grid[x,y,z:]) == 0 )):
            return True
        return False
        