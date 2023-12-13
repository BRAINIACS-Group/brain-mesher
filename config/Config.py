# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 13:55:28 2023

@author: grife
"""
import warnings

from config.Material_Label import Material_Label
from writers.HeterogeneityConverter import Heterogeneity
import configparser
import os


class ConfigFile:
    """
    A class used to set up preferences for brain creation.
    """

    def __init__(self, file_in_path, file_in_name, file_out_path, file_out_name,
                 configFilePath="./IOput/model_config.ini", model_type=''):
        self.MATERIAL_LABELS = None
        self.f = None
        self.data = []
        self.config_dict = {}

        config = configparser.ConfigParser()
        config.read(configFilePath)
        curr_config = config['DEFAULT']

        # Material converter preference
        material_converter = curr_config.get('converter_type')
        if material_converter == '1R':
            self.converter_type = Heterogeneity.ONER
        elif material_converter == '2R':
            self.converter_type = Heterogeneity.TWOR
        elif material_converter == '4R':
            self.converter_type = Heterogeneity.FOURR
        else:
            self.converter_type = Heterogeneity.NINER

        self.MATERIAL_LABELS = Material_Label()
        # Material labels (PRESET)
        self.MATERIAL_LABELS.addLabelToMap('brainStem', 16)
        self.MATERIAL_LABELS.addLabelToMap('greymatter', [3, 42])  # Left, Right
        self.MATERIAL_LABELS.addLabelToMap('whitematter', [2, 41, 77])  # Left, Right, WM-hypointensities
        self.MATERIAL_LABELS.addLabelToMap('corpuscallosum', [251, 252, 253, 254,
                                                              255])  # CC_Posterior, CC_Mid_Posterior, CC_Central,
        # CC_Mid_Anterior, CC_Anterior
        self.MATERIAL_LABELS.addLabelToMap('basalganglia', [11, 50, 12, 51, 13, 52, 26, 58, 62,
                                                            30])  # Caudate(L&R), Putamen(L&R), Palladium(L&R),
        # Accumbens Area(L&R), vessel(L&R)
        self.MATERIAL_LABELS.addLabelToMap('cerebellum', [7, 46, 8, 47])  # WM(L&R), GM(L&R)
        self.MATERIAL_LABELS.addLabelToMap('thalamus', [10, 49, 28, 60])  # Thalamus(L&R), Ventral DC(L&R)
        self.MATERIAL_LABELS.addLabelToMap('hippocampus', [17, 53])  # Left, Right
        self.MATERIAL_LABELS.addLabelToMap('amygdala', [18, 54])  # Left, Right
        self.MATERIAL_LABELS.addLabelToMap('ventricles',
                                           [4, 5, 43, 44, 14, 15])  # Lateral(L&R), 3rd, 4th, Inf-Lat-Vent(L&R)

        # File settings
        # Read Settings
        self.config_dict['read_file'] = True
        file_in_path = file_in_path.replace("\\", "/")
        while file_in_path[-1] == "/":
            file_in_path = file_in_path[:-1]
        self.config_dict['file_in_path'] = file_in_path
        self.config_dict['file_in'] = file_in_name

        # Write settings
        self.config_dict['write_to_file'] = True
        file_out_path = file_out_path.replace("\\", "/")
        while file_out_path[-1] == "/":
            file_out_path = file_out_path[:-1]

        files_to_create = []
        file_out_path_split = file_out_path.split("/")
        while not os.path.exists(file_out_path):
            files_to_create.append(file_out_path_split.pop())
            file_out_path = "/".join(file_out_path_split)

        files_to_create.reverse()
        for file in files_to_create:
            file_out_path = "/".join([file_out_path, file])
            os.mkdir(file_out_path)

        self.config_dict['file_out_path'] = file_out_path
        file_out_name = "unnamed_test" if file_out_name == '' else file_out_name
        self.config_dict['fileout'] = file_out_name

        types_string = curr_config.get('fileout_types')
        types = [x.strip() for x in types_string.split(",")]
        for t in types:
            assert ['ucd', 'vtk', 'abaqus'].count(t), "OUTPUT TYPE {} NOT SUPPORTED".format(t)
        self.config_dict['fileout_types'] = types  # 'ucd' | 'vtk' | 'abaqus'

        # # preprocessing options
        self.config_dict['model_type'] = model_type
        if model_type in config:
            curr_config = config[model_type]

        # CSF options
        self.config_dict['add_csf'] = curr_config.getboolean('add_csf', False)
        if self.get('add_csf'):
            self.config_dict['csf_type'] = curr_config.get('csf_type', 'full').lower()  # 'none' | 'full' | 'partial'
            self.config_dict['csf_layers'] = curr_config.getint('csf_layers', 1)

        # Smoothing features
        self.config_dict['smooth'] = curr_config.getboolean('smooth', False)

        if self.config_dict['smooth']:
            self.config_dict['iterations'] = curr_config.getint('iterations')
            smooth_co_effs = curr_config.get('co_effs')
            self.config_dict['co_effs'] = [float(x.strip()) for x in smooth_co_effs.split(",")]

            smooth_regions = curr_config.get('smooth_regions')
            if smooth_regions == '':
                self.config_dict['smooth_regions'] = []
            else:
                self.config_dict['smooth_regions'] = [x.strip() for x in smooth_regions.split(",")]

            region_iterations = curr_config.get('region_iterations')
            if region_iterations == '':
                self.config_dict['region_iterations'] = []
            else:
                self.config_dict['region_iterations'] = [int(x.strip()) for x in region_iterations.split(",")]

            region_co_effs_tmp = curr_config.get('region_co_effs')
            if region_co_effs_tmp == '':
                self.config_dict['region_co_effs'] = []
            else:
                region_co_effs_tmp = [x.strip() for x in
                                      region_co_effs_tmp.replace("[", "").replace("]", "").split(",")]
                region_co_effs = []
                assert (len(region_co_effs_tmp) % 2 == 0)
                for r_count in range(0, len(region_co_effs_tmp), 2):
                    region_co_effs.append([float(region_co_effs_tmp[r_count]), float(region_co_effs_tmp[r_count + 1])])
                self.config_dict['region_co_effs'] = region_co_effs

            self.config_dict['smooth_regions'].reverse()
            self.config_dict['region_iterations'].reverse()
            self.config_dict['region_co_effs'].reverse()

    def get(self, key):
        result = self.config_dict.get(key, None)
        if result is None:
            warnings.warn("There is no configuration setting with the name:" + key)
            return False
        return result

    def set(self, key, value):
        result = self.config_dict.get(key, None)
        if result is None:
            warnings.warn("There is no configuration setting with the name:" + key)
        self.config_dict.update({key: value})

    def set_materials_label(self, newLabels):
        self.MATERIAL_LABELS = newLabels

    def get_material_value(self, name):
        name = name.lower()
        all_labels = self.MATERIAL_LABELS.get_homogenized_labels_map()
        return all_labels.get(name, -1000)

    def open_config_file(self):
        """
        Opens and write data to config log file

        """
        self.f = open("/".join([self.get('file_out_path'), self.get('fileout')]) + ".txt", 'w')

    def write_preamble(self):
        self.f.write("Input file: " + self.get('file_in_path') + self.get('file_in') + "\n")
        self.f.write("Write output to file: " + str(self.config_dict.get('write_to_file', False)) + "\n")
        if self.config_dict.get('write_to_file', False):
            self.f.write("Output written to: " + self.config_dict.get('file_out_path') + self.get('fileout') + "\n")
            self.f.write("Output file types: " + ", ".join(self.config_dict.get('fileout_types')) + "\n")

        self.f.write("Coarsen: " + str(self.config_dict.get('coarsen', False)) + "\n")

        self.f.write("model type configuration settings: " + str(self.get('model_type')) + "\n")

        self.f.write("Add CSF: " + str(self.get('add_csf')) + "\n")
        if self.config_dict.get('add_csf'):
            self.f.write("Type of CSF added: " + str(self.get('csf_type')) + "\n")
            self.f.write("Layers of CSF: " + str(self.get('csf_layers')) + "\n")

        self.f.write("Smooth global mesh: " + str(self.get('smooth')) + "\n")
        if self.get('smooth'):
            self.f.write(
                "Iterations: " + str(self.get('iterations')) + ", co_effs: " + ", ".join(
                    [str(x) for x in self.get('co_effs')]) + "\n")
            for count, r in enumerate(self.get('smooth_regions')):
                self.f.write("Smooth region: " + r + "\n")
                self.f.write("Iterations: " + str(self.get('region_iterations')[count]) + ", co_effs: " + \
                             ", ".join([str(x) for x in self.get('region_co_effs')[count]]) + "\n")

    def write_to_config(self, name, value):
        """
        Write additional key-value pair data to config file.

        Parameters
        ----------
        name : string
            key string.
        value : string
            value string.

        """
        self.f.write("{}: {}\n".format(name, str(value)))

    def close_config_file(self):
        """
        Closes config log file

        """
        self.write_to_config("Regions included", "")
        for r, values in self.MATERIAL_LABELS.labelsMap.items():
            self.write_to_config("\t", r + ": " + ", ".join([str(x) for x in values]))
        self.f.write("COMPLETE\n")
        self.f.close()
