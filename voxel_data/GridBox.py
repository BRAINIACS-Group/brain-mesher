# -*- coding: utf-8 -*-
"""
Created on Thu May 25 09:29:49 2023

@author: grife
"""

import numpy as np


class GridBox:
    splitter = "-"
    
    def __init__(self,grid, point):
        self.create_box_from_grid(grid,point)
    
    def create_box_from_grid(self,grid,point):
        current_dimensions = grid.shape
        [x,y,z] = point
        xLower = x-1 if x > 0 else 0
        yLower = y-1 if y > 0 else 0
        zLower = z-1 if z > 0 else 0
        xUpper = x+2 if x < (current_dimensions[0]-1) else (current_dimensions[0])
        yUpper = y+2 if y < (current_dimensions[1]-1) else (current_dimensions[1])
        zUpper = z+2 if z < (current_dimensions[2]-1) else (current_dimensions[2])
        self.gridBox = grid[xLower:xUpper, yLower:yUpper, zLower:zUpper].reshape(-1)
        self.location = (x,y,z)
        self.bounds = (xLower,xUpper,yLower,yUpper,zLower,zUpper)
        
    
    def get_number_non_zeros(self):
        num_non_zero = 0
        # print(self.gridBox)
        for i in self.gridBox:
            if (i != 0):
                num_non_zero += 1
        return num_non_zero
    
    def get_location_key(self):
        return GridBox.create_location_key(self.location);
    
    @classmethod
    def create_location_key(self,location):
        return GridBox.splitter.join([str(l) for l in location]);
        
    def mode(self):
        [modes, count] = np.unique(self.gridBox, return_counts=True)
        modeIndices, = np.where(count == max(count))
        modeIndex = modeIndices[0]
        replacedValue = modes[modeIndex]
        if 4 in self.gridBox:
            replacedValue = 4 
        elif 251 in self.gridBox:
            replacedValue = 251 
        elif replacedValue == 0:
            if (len(modes)>1):                
                zero_idx = np.where(modes == 0)
                np.delete(modes,zero_idx)
                np.delete(count, zero_idx)
                modeIndices, = np.where(count == max(count))
                modeIndex = modeIndices[0]
                replacedValue = modes[modeIndex]
            if (len(np.unique(self.gridBox)) > 1):
                unique_values = np.unique(self.gridBox)
                zero_idx = np.where(modes == 0)
                unique_values = np.delete(unique_values,zero_idx)
                replacedValue = unique_values[0]                
            else:
                print(modes)
                print(count)
                print(self.gridBox)
                print("***Error replacing value at location: " + ", ".join([str(l) for l in self.location]))
                return replacedValue
        return replacedValue
        
    
    