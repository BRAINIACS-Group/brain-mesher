# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 10:14:18 2023

@author: grife
"""
import numpy as np
from voxel_data.void_filler.Maze import Maze

class InverseMaze(Maze):
    
    def __init__(self, grid):
        super().__init__(grid);
        current_dimensions = self.grid.shape
        point = 1;
        count = 0;
        while(point != 0):
            xEnd = int((current_dimensions[0] + count)/2);
            yEnd = int((current_dimensions[1] + count)/2);
            zEnd = int((current_dimensions[2] + count)/2);
            point = self.grid[xEnd,yEnd,zEnd]
        self.end = [xEnd,yEnd,zEnd]
    
    def get_end_point(self,x,y,z):
        [xEnd,yEnd,zEnd] = self.end
        return [xEnd,yEnd,zEnd]; 
    
    def isExit(self,x,y,z):
        [xEnd,yEnd,zEnd] = self.end
        if (xEnd < x):
            if (np.sum(self.grid[xEnd:x,y,z]) == 0):
                return True
        else:
            if (np.sum(self.grid[x:xEnd+1,y,z]) == 0):
                return True
        if (yEnd < y):
            if (np.sum(self.grid[x,yEnd:y,z]) == 0):
                return True
        else:
            if (np.sum(self.grid[x,y:yEnd+1,z]) == 0):
                return True
        if (zEnd < z):
            if (np.sum(self.grid[x,y,zEnd:z]) == 0):
                return True
        else:
            if (np.sum(self.grid[x,y,z:zEnd+1]) == 0):
                return True
        return False
    
    