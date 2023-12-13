# -*- coding: utf-8 -*-
"""
Created on Fri May 12 11:02:36 2023

@author: grife
"""

import numpy as np
from scipy import stats
from scipy import ndimage
from voxel_data.GridBox import GridBox
from scipy.spatial import Delaunay

"""
A module of functions to assist with manipulating voxel data
"""

    
def in_hull(p, hull):
    """
    Test if points in `p` are in `hull`

    `p` should be a `NxK` coordinates of `N` points in `K` dimensions
    `hull` is either a scipy.spatial.Delaunay object or the `MxK` array of the 
    coordinates of `M` points in `K`dimensions for which Delaunay triangulation
    will be computed
    """

    if not isinstance(hull,Delaunay):
        hull = Delaunay(hull)

    return hull.find_simplex(p)>=0
    
def check_data_dims(data):        
    if len(data.shape) == 3:
        return True
    else:
        print('Error, data shape not 3 dimensional!')
        return False    
    
def override_voxel_data(new_data,current_data, replacementValue = -1):
    current_dimensions = current_data.shape
    for x in range(current_dimensions[0]):
        if (np.sum(new_data[x,:,:]) > 0):
            for y in range(current_dimensions[1]):
                if (np.sum(new_data[x,y,:]) > 0):
                    for z in range(current_dimensions[2]):
                        if (new_data[x,y,z] != 0):
                            if replacementValue == -1:
                                current_data[x, y, z] = new_data[x, y, z]
                            else:
                                current_data[x,y,z] = replacementValue
    
def coarsen(new_voxel_size, original_data):
    print("Coarsening mesh by a factor of " + str(new_voxel_size))
    current_dimensions = original_data.shape
    new_dimensions = [int(p) for p in np.floor(np.array(current_dimensions)/new_voxel_size)];
    newData = np.zeros(new_dimensions, int)
    for x in np.arange(0,(current_dimensions[0]-1),new_voxel_size):
        top_x = x+new_voxel_size
        if (np.sum(original_data[x:top_x,:,:]) > 0):
            for y in np.arange(0,(current_dimensions[1]-1),new_voxel_size):
                top_y = y+ new_voxel_size
                if (np.sum(original_data[x:top_x,y:top_y,:]) > 0):
                    for z in np.arange(0,(current_dimensions[2]-1),new_voxel_size):
                        top_z = z+new_voxel_size
                        gridBox = original_data[x:top_x, y:top_y, z:top_z].reshape(-1)
                        if (np.sum(gridBox) > 0):
                            unique, counts = np.unique(gridBox, return_counts=True)
                            num_values = dict(zip(unique, counts))
                            if num_values.get(251, False):
                                replacedValue = 251
                            elif num_values.get(4, False):
                                replacedValue = 4
                            else:
                                [modes, count] = stats.find_repeats(gridBox)
                                modeIndices, = np.where(count == max(count))
                                modeIndex = modeIndices[0]
                                replacedValue = modes[modeIndex]
                                if (len(modes)>1) and (len(modeIndices)>1):
                                    if (modeIndices[0]==0) or (modeIndices[1]==0):
                                        if (modeIndices[0]==0):
                                            replacedValue = modes[modeIndices[1]]
                                        elif (modeIndices[1]==0):
                                            replacedValue = modes[modeIndices[0]]
                                    else:
                                        xbot = x-1 if x>0 else 0
                                        ybot = y-1 if y>0 else 0
                                        zbot = z-1 if z>0 else 0
                                        gridBox = original_data[xbot:top_x, ybot:top_y, zbot:top_z].reshape(-1)
                                        [modes,count] = stats.find_repeats(gridBox)
                                        modeIndices, = np.where(count == max(count))
                                        modeIndex = modeIndices[0]
                                        replacedValue = modes[modeIndex]
                                
                                
                            newData[int(x/new_voxel_size),int(y/new_voxel_size),int(z/new_voxel_size)] = replacedValue
    return newData        

def create_binary_image(current_data, search=-1):
    current_dimensions = current_data.shape
    newData = np.zeros(current_dimensions, int)
    for x in range(current_dimensions[0]):
        if (np.sum(current_data[x,:,:]) > 0):
            for y in range(current_dimensions[1]):
                if (np.sum(current_data[x,y,:]) > 0):
                    for z in range(current_dimensions[2]):
                        if (search== -1) and (current_data[x,y,z] != 0):
                            newData[x,y,z] = 1
                        elif (search != -1) and (current_data[x,y,z] == search):
                            newData[x,y,z] = 1
                            
    return newData


def clean_voxel_data(start_data):  
    print("Performing cleaning operations on data")
    cleaned = create_binary_image(start_data)
    start = np.sum(cleaned)
    structure = ndimage.generate_binary_structure(3, 3)
    print("Filling in holes")
    cleaned = fill_in_holes(cleaned, structure)
    print("Hit and miss cleaning")
    __hit_and_miss_2d(cleaned)
    __hit_and_miss(cleaned) 
    print("Filling in holes")
    cleaned = fill_in_holes(cleaned, structure)  
    end = np.sum(cleaned)      
    print("Complete")        
    assign_materials_labels(start_data, cleaned)
    return start != end


def clean_region(data, label):
    print("Cleaning ventricles")
    ventricles_og = create_binary_image(data, search=label)
    ventricles = binary_dilation(ventricles_og)
    ventricles = binary_erosion(ventricles)
    dimensions = ventricles.shape
    for x in range(dimensions[0]):
        if np.sum(ventricles[x, :, :]) > 0 or list(np.unique(data[x, :, :])).count(label):
            for y in range(dimensions[1]):
                if (np.sum(ventricles[x, y, :]) > 0 or
                        list(np.unique(data[x, y, :])).count(label)):
                    for z in range(dimensions[2]):
                        if ventricles[x, y, z] == 1:
                            data[x, y, z] = label
                        elif ventricles_og[x, y, z] == 1 and ventricles[x, y, z] != 1:
                            box = GridBox(data, [x, y, z])
                            box.gridBox = np.delete(box.gridBox, np.where(box.gridBox == label))
                            replacement_value = box.mode()
                            if replacement_value is None:
                                data[x, y, z] = 0
                            else:
                                data[x, y, z] = replacement_value


def __hit_and_miss(data):
    
    hit_structureA_Z = np.ones((2,2,2))
    hit_structureA_Z[0,1,0] = 0
    hit_structureA_Z[1,0,0] = 0
    hit_structureA_Z2 = np.rot90(hit_structureA_Z,)
    hit_structureA_Z3 = np.rot90(hit_structureA_Z, k=2, axes=(1,2))
    hit_structureA_Z4 = np.rot90(hit_structureA_Z2, k=2, axes=(1,2))
    hit_structures_A_Z = [hit_structureA_Z, hit_structureA_Z2, hit_structureA_Z3, hit_structureA_Z4]

    hit_structureA_Y = np.ones((2,2,2))
    hit_structureA_Y[0,0,1] = 0
    hit_structureA_Y[1,0,0] = 0
    hit_structureA_Y2 = np.rot90(hit_structureA_Y, axes=(0,2))
    hit_structureA_Y3 = np.rot90(hit_structureA_Y, k=2, axes=(0,1))
    hit_structureA_Y4 = np.rot90(hit_structureA_Y2, k=2, axes=(0,1)) 
    hit_structures_A_Y = [hit_structureA_Y, hit_structureA_Y2, hit_structureA_Y3, hit_structureA_Y4]

    hit_structureA_X = np.ones((2,2,2))
    hit_structureA_X[0,0,1] = 0
    hit_structureA_X[0,1,0] = 0
    hit_structureA_X2 = np.rot90(hit_structureA_X, axes=(1,2))
    hit_structureA_X3 = np.rot90(hit_structureA_X, k=2, axes=(0,1))
    hit_structureA_X4 = np.rot90(hit_structureA_X2, k=2, axes=(0,1))
    hit_structures_A_X = [hit_structureA_X, hit_structureA_X2, hit_structureA_X3, hit_structureA_X4]                
    
    hit_structureB = np.ones((2,2,2))
    hit_structureB[0,0,0] = 0
    hit_structureB[1,1,1] = 0
    hit_structureB_2 = np.rot90(hit_structureB, axes=(1,2))
    hit_structureB_3 = np.rot90(hit_structureB, k=2, axes=(1,2))
    hit_structureB_4 = np.rot90(hit_structureB_2, k=2, axes=(1,2))
    hit_structures_B = [hit_structureB, hit_structureB_2, hit_structureB_3, hit_structureB_4]
    
    
    hit_structureD = np.ones((2,2,2))
    hit_structureD[0,0,0] = 0
    hit_structureD[1,0,0] = 0
    hit_structureD[0,1,0] = 0
    hit_structureD[1,1,1] = 0
    hit_structureD[1,0,1] = 0
    hit_structureD[0,1,1] = 0
    hit_structureD_2 = np.rot90(hit_structureD)
    hit_structureD_3 = np.rot90(hit_structureD, k=2)
    hit_structureD_4 = np.rot90(hit_structureD, k=3)
    
    count = 1
    total_count = 0
    iterations = 0
    while (count > 0 and iterations<10):
        count = 0
        iterations += 1
        for structure in hit_structures_A_X+hit_structures_A_Y+hit_structures_A_Z:
            count += hit_and_miss_3d_2x2x2(data,structure, fill=1);
            
        for structure in hit_structures_B:
            count += hit_and_miss_3d_2x2x2(data,structure);
                
        count += hit_and_miss_3d_2x2x2(data,hit_structureD);
        count += hit_and_miss_3d_2x2x2(data,hit_structureD_2);
        count += hit_and_miss_3d_2x2x2(data,hit_structureD_3);
        count += hit_and_miss_3d_2x2x2(data,hit_structureD_4);
        
        total_count += count
    print("Hit and miss 3D: " + str(total_count) + " in " + str(iterations) + " iterations")
    
def hit_and_miss_3d_2x2x2(data, hit_structure, fill=0):
    count = 0
    test = ndimage.binary_hit_or_miss(data, structure1=hit_structure).astype(int)
    xh,yh,zh = np.where(test == 1)
    for [xs,ys,zs] in np.column_stack((xh,yh,zh)):
        count += 1
        data[xs-1:xs+1,ys-1:ys+1,zs-1:zs+1] = np.ones((2,2,2))*fill
    return count
    
    
def __hit_and_miss_2d(data):
    total_count = 0
    count = 1
    iteration= 0        
    hit_structure1 = np.ones((2,2))
    hit_structure1[0,0] = 0
    hit_structure1[1,1] = 0
    hit_structure2 = np.rot90(hit_structure1)
    hit_structure3 = np.zeros((3,3))
    hit_structure3[1,1] = 1
    hit_structure4 = np.zeros((3,4))
    hit_structure4[1,1] = 1
    hit_structure4[1,2] = 1
    hit_structure4b = np.rot90(hit_structure4)
    while (count >0 and iteration<10):
        iteration += 1
        count = 0
        for x in np.arange(0,(data.shape[0])):
            if (np.sum(data[x,:,:]) > 0): 
                old = data[x,:,:]
                test1 = ndimage.binary_hit_or_miss(old, structure1=hit_structure1).astype(int)
                xh,yh = np.where(test1 == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[x,xs-1:xs+1,ys-1:ys+1] = np.zeros((2,2))
                    count += 1
                    
                test2 = ndimage.binary_hit_or_miss(old, structure1=hit_structure2).astype(int)
                xh,yh = np.where(test2 == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[x,xs-1:xs+1,ys-1:ys+1] = np.zeros((2,2))
                    count += 1
                    
                test3 = ndimage.binary_hit_or_miss(old, structure1=hit_structure3).astype(int)
                xh,yh = np.where(test3 == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[x,xs,ys] = 0
                    count += 1
                 
                test4a = ndimage.binary_hit_or_miss(old, structure1=hit_structure4).astype(int)
                xh,yh = np.where(test4a == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[x,xs-1:xs+2,ys-2:ys+2] = np.zeros((3,4))
                    count += 1                     
                       
                test4b = ndimage.binary_hit_or_miss(old, structure1=hit_structure4b).astype(int)
                xh,yh = np.where(test4b == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[x,xs-2:xs+2,ys-1:ys+2] = np.zeros((4,3))
                    count += 1
                    
        for y in np.arange(0,(data.shape[1])):
            if (np.sum(data[:,y,:]) > 0): 
                old = data[:,y,:]
                test1 = ndimage.binary_hit_or_miss(old, structure1=hit_structure1).astype(int)
                xh,yh = np.where(test1 == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[xs-1:xs+1,y,ys-1:ys+1] = np.zeros((2,2))
                    count += 1
                    
                test2 = ndimage.binary_hit_or_miss(old, structure1=hit_structure2).astype(int)
                xh,yh = np.where(test2 == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[xs-1:xs+1,y,ys-1:ys+1] = np.zeros((2,2))
                    count += 1
                    
                test3 = ndimage.binary_hit_or_miss(old, structure1=hit_structure3).astype(int)
                xh,yh = np.where(test3 == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[xs,y,ys] = 0
                    count += 1
                 
                test4a = ndimage.binary_hit_or_miss(old, structure1=hit_structure4).astype(int)
                xh,yh = np.where(test4a == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[xs-1:xs+2,y,ys-2:ys+2] = np.zeros((3,4))
                    count += 1                     
                       
                test4b = ndimage.binary_hit_or_miss(old, structure1=hit_structure4b).astype(int)
                xh,yh = np.where(test4b == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[xs-2:xs+2,y,ys-1:ys+2] = np.zeros((4,3))
                    count += 1
                    
        for z in np.arange(0,(data.shape[2])):
            if (np.sum(data[:,:,z]) > 0): 
                old = data[:,:,z]
                
                test1 = ndimage.binary_hit_or_miss(old, structure1=hit_structure1).astype(int)
                xh,yh = np.where(test1 == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[xs-1:xs+1,ys-1:ys+1,z] = np.zeros((2,2))
                    count += 1
                    
                test2 = ndimage.binary_hit_or_miss(old, structure1=hit_structure2).astype(int)
                xh,yh = np.where(test2 == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[xs-1:xs+1,ys-1:ys+1,z] = np.zeros((2,2))
                    count += 1 
                    
                test3 = ndimage.binary_hit_or_miss(old, structure1=hit_structure3).astype(int)
                xh,yh = np.where(test3 == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[xs,ys,z] = 0
                    count += 1
                 
                test4a = ndimage.binary_hit_or_miss(old, structure1=hit_structure4).astype(int)
                xh,yh = np.where(test4a == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[xs-1:xs+2,ys-2:ys+2,z] = np.zeros((3,4))
                    count += 1                     
                       
                test4b = ndimage.binary_hit_or_miss(old, structure1=hit_structure4b).astype(int)
                xh,yh = np.where(test4b == 1)
                for [xs,ys] in np.column_stack((xh,yh)):
                    data[xs-2:xs+2,ys-1:ys+2,z] = np.zeros((4,3))
                    count += 1
                
        total_count += count
    print("Hit and miss 2D: " + str(total_count) + " in " + str(iteration) + " iterations")
    
    
def fill_in_holes( data, structure = None):
    if np.any(structure == None):
        structure = create_structure()
    return ndimage.binary_fill_holes(data, structure=structure).astype(int)

def binary_dilation( data, structure=None, iterations=1):
    if np.any(structure == None):
        structure = create_structure()
    return ndimage.binary_dilation(data, structure=structure, iterations=iterations).astype(int)

def binary_erosion( data, structure=None, iterations=1):
    if np.any(structure == None):
        structure = create_structure()
    return ndimage.binary_erosion(data, structure=structure, iterations=iterations).astype(int)

def create_structure():       
    structure = ndimage.generate_binary_structure(3,3)
    return structure

# def two_d_cleaning(start_data):
#     print("Performing 2D cleaning operations on data")
#     cleaned = create_binary_image(start_data)
#     two_d_fill(cleaned)
#     assign_materials_labels(start_data,cleaned)

# def two_d_fill(cleaned):
#     hit_structure = np.ones((3,3))
#     hit_structure[1,1] = 0
#     hit_structureA = np.ones((2,2))
#     hit_structureA[0,0] = 0
#     hit_structureA[1,1] = 0
#     hit_structureB = np.ones((2,2))
#     hit_structureB[1,0] = 0
#     hit_structureB[0,1] = 0
    
#     for x in np.arange(0,(cleaned.shape[0])):
#         if (np.sum(cleaned[x,:,:]) > 0): 
#             old = cleaned[x,:,:]
#             g = ndimage.binary_hit_or_miss(old, structure1=hit_structure).astype(int)
#             loc = np.where(g == 1)
#             for r in range(len(loc[0])):
#                 px = loc[0][r]
#                 py = loc[1][r]
#                 cleaned[x,px,py] = 1
            
#             g = ndimage.binary_hit_or_miss(old, structure1=hit_structureA).astype(int)
#             loc = np.where(g == 1)
#             for r in range(len(loc[0])):
#                 px = loc[0][r]
#                 py = loc[1][r]
#                 cleaned[x,px,py-1] = 0
            
#             g = ndimage.binary_hit_or_miss(old, structure1=hit_structureB).astype(int)
#             loc = np.where(g == 1)
#             for r in range(len(loc[0])):
#                 px = loc[0][r]
#                 py = loc[1][r]
#                 cleaned[x,px,py] = 0
                
#     for y in np.arange(0,(cleaned.shape[1])):
#         if (np.sum(cleaned[:,y,:]) > 0): 
#             old = cleaned[:,y,:]
#             g = ndimage.binary_hit_or_miss(old, structure1=hit_structure).astype(int)
#             loc = np.where(g == 1)
#             for r in range(len(loc[0])):
#                 px = loc[0][r]
#                 py = loc[1][r]
#                 cleaned[px,y,py] = 1
            
#             g = ndimage.binary_hit_or_miss(old, structure1=hit_structureA).astype(int)
#             loc = np.where(g == 1)
#             for r in range(len(loc[0])):
#                 px = loc[0][r]
#                 py = loc[1][r]
#                 cleaned[px,y,py-1] = 0
            
#             g = ndimage.binary_hit_or_miss(old, structure1=hit_structureB).astype(int)
#             loc = np.where(g == 1)
#             for r in range(len(loc[0])):
#                 px = loc[0][r]
#                 py = loc[1][r]
#                 cleaned[px,y,py] = 0
                
#     for z in np.arange(0,(cleaned.shape[2])):
#         if (np.sum(cleaned[:,:,z]) > 0): 
#             old = cleaned[:,:,z]
#             g = ndimage.binary_hit_or_miss(old, structure1=hit_structure).astype(int)
#             loc = np.where(g == 1)
#             for r in range(len(loc[0])):
#                 px = loc[0][r]
#                 py = loc[1][r]
#                 cleaned[px,py,z] = 1
            
#             g = ndimage.binary_hit_or_miss(old, structure1=hit_structureA).astype(int)
#             loc = np.where(g == 1)
#             for r in range(len(loc[0])):
#                 px = loc[0][r]
#                 py = loc[1][r]
#                 cleaned[px,py-1,z] = 0
            
#             g = ndimage.binary_hit_or_miss(old, structure1=hit_structureB).astype(int)
#             loc = np.where(g == 1)
#             for r in range(len(loc[0])):
#                 px = loc[0][r]
#                 py = loc[1][r]
#                 cleaned[px,py,z] = 0
    
   
def assign_materials_labels(labelled_data, end_data):
    assert labelled_data.shape == end_data.shape
    dimensions = labelled_data.shape;
    for x in range(dimensions[0]):
        for y in range(dimensions[1]):
            for z in range(dimensions[2]):
                if (labelled_data[x,y,z] == 0) and (end_data[x,y,z] != 0):
                    box = GridBox(labelled_data,[x,y,z])
                    replacement_value = box.mode() 
                    if replacement_value == None:
                        labelled_data[x,y,z] = 0
                    else:
                        labelled_data[x,y,z] = replacement_value                              
                elif (labelled_data[x,y,z] != 0) and (end_data[x,y,z] == 0):
                    labelled_data[x,y,z] = 0; 
            

    
def get_bounding_box(data):
    maxValues = [-100000,-100000,-100000]
    minValues = [100000,100000,100000]
    current_dimensions = data.shape
    for x in range(current_dimensions[0]):
        if (np.sum(data[x,:,:]) > 0):
            for y in range(current_dimensions[1]):
                if (np.sum(data[x,y,:]) > 0):
                    for z in range(current_dimensions[2]):
                        if (data[x,y,z] == 1):
                            coords = [x,y,z]
                            for d in range(3):
                                if (maxValues[d] < coords[d]):
                                    maxValues[d] = coords[d]
                                if (minValues[d] > coords[d]):
                                    minValues[d] = coords[d]
    return maxValues + minValues
                        
def trim_data(data):
    current_dimensions = data.shape
    start = 0
    end = current_dimensions[0]
    for x in range(current_dimensions[0]):
        if np.sum(data[x,:,:]) != 0:
            start = x
            break
    for rev_x in range(1,current_dimensions[0]):
        x = current_dimensions[0]-rev_x
        if np.sum(data[x,:,:]) != 0:
            end = x
            break
    data = data[start-1:end+2,:,:]
    
    start = 0
    end = current_dimensions[1]
    for y in range(current_dimensions[1]):
        if np.sum(data[:,y,:]) != 0:
            start = y
            break
    for rev_y in range(1,current_dimensions[1]):
        y = current_dimensions[1]-rev_y
        if np.sum(data[:,y,:]) != 0:
            end = y
            break
    data = data[:,start-1:end+2,:]
    
    start = 0
    end = current_dimensions[2]
    for z in range(current_dimensions[2]):
        if np.sum(data[:,:,z]) != 0:
            start = z
            break
    for rev_z in range(1,current_dimensions[2]):
        z = current_dimensions[2]-rev_z
        if np.sum(data[:,:,z]) != 0:
            end = z
            break
    data = data[:,:,start-1:end+2]
    
    return data
        
    
    
        
                                        


            
                                
                            
            
        
    
    
    