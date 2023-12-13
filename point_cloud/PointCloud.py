# -*- coding: utf-8 -*-
"""
Created on Wed May 24 14:02:00 2023

@author: grife
"""
import numpy as np
import pyvista as pv


class PointCloud:
    
    def create_point_cloud_from_voxel(self, data):
        current_data = data
        current_dimensions = current_data.shape
        pointCloudData = np.zeros((np.prod(current_dimensions),4));
        count = 0;
        for x in range(current_dimensions[0]):
            if (np.sum(current_data[x,:,:]) > 0):
                for y in range(current_dimensions[1]):
                    if (np.sum(current_data[x,y,:]) > 0):
                        for z in range(current_dimensions[2]):
                            if (current_data[x,y,z] != 0):
                                pointCloudData[count,:] = [x,y,z,current_data[x,y,z]] # co-ordinate data and material type (used in colouring point_cloud)
                                count += 1;
        self.pcd = pointCloudData[0:count,:]
        self.set_colour_map(data)
        return self.pcd
    
    def create_point_cloud_from_mesh(self, elements, nodes):
        pointCloudData = np.zeros((len(elements)+1,4));
        for e in elements.items():
            m = e.properties['mat'][0]
            ica = e.ica
            [x,y,z] = e.calculate_element_centroid(ica, nodes)
            pointCloudData[e.num,:] = [x,y,z,m]
        self.pcd = pointCloudData;
        return self.pcd
            
        
    def view_point_cloud(self, *args, **kwargs):        
        if len(args)>0:
            pointCloudData = args[0]
        else:
            if hasattr(self, "pcd"):
                pointCloudData = self.pcd
            else:
                print("No point cloud data has been created")
                return -1
        point_cloud = pv.PolyData(pointCloudData[:,0:3])
        point_cloud["material_type"] = pointCloudData[:,3:]
        point_cloud.plot(eye_dome_lighting=True)
        return 0
    
    # def view_region_point_cloud(self, material_number):        
    #     if hasattr(self, "pcd"):
    #         pointCloudData = self.pcd
    #     else:
    #         print("No point cloud data has been created")
    #         return -1
    #     # idx, = np.where(np.array(pointCloudData[:,3])==material_number)
    #     # data_to_display = np.delete(np.array(pointCloudData[:,3]),idx)
    #     point_cloud = pv.PolyData(data_to_display)
    #     point_cloud["material_type"] = pointCloudData[:,3:]
    #     point_cloud.plot(eye_dome_lighting=True)
    #     return 0
    
    def add_point_to_cloud(self,p):
        self.pcd = np.append(self.pcd,[p], axis=0)
    
    def view_slice(self, axis, location):
        if (location > 1) and (axis < self.pcd.shape[1]):
            arr = self.pcd[:,axis]
            if (location <= max(arr)):
                indices, = np.where(location == arr)
                points = self.pcd[indices,:]
                point_cloud = pv.PolyData(points[:,0:3])
                point_cloud["material_type"] = points[:,3:]
                point_cloud.plot(render_points_as_spheres=True)
    
    def get_slice(self, axis, location):
        if (location > 1) and (axis < self.pcd.shape[1]):
            arr = self.pcd[:,axis]
            if (location <= max(arr)):
                indices, = np.where(location == arr)
                points = self.pcd[indices,:]
        return points          
        
    
    def set_colour_map(self,d):
        #TODO: Currently NOT functioning. Fix color map problem
        blue = np.array([0, 0, 205 / 256, 1.0])
        black = np.array([11 / 256, 11 / 256, 11 / 256, 1.0])
        grey = np.array([189 / 256, 189 / 256, 189 / 256, 1.0])
        yellow = np.array([255 / 256, 247 / 256, 0 / 256, 1.0])
        red = np.array([1.0, 0.0, 0.0, 1.0])
        green = np.array([0, 255/256, 0, 1.0])
        purple = np.array([139 / 256, 0, 139/256, 1.0])
        orange = np.array([255/256, 165/256, 0, 1.0])
        light_blue = np.array([0, 191/256, 255/256, 1.0])
        white = np.array([245/256, 245/256, 245/256, 1.0])
        pink = np.array([255/256, 105/256, 180/256, 1.0])
        
        colorArray = [red, blue, green,  light_blue, yellow, purple, orange, grey, pink, white, black]
        
        # values_in_data = np.unique(d)
        # values_in_data = values_in_data[values_in_data != 0]
        # newcolors = np.zeros((256, 4))
        # for count, value in enumerate(values_in_data):
        #     newcolors[value,:] = colorArray[count]
        # self.my_colormap = ListedColormap(newcolors)