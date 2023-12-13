import voxel_data.voxel_data_utils as bm
from voxel_data.void_filler import Maze, InverseMaze, Maze_Solver
from abc import ABC, abstractmethod
from voxel_data import PreProcessingActions as pp
from voxel_data.csf_functions import CSFFunctions
from random import randint
from scipy.stats import qmc
import numpy as np


class PreprocessConfigData(object):
    pass


class IPreprocessor(ABC):

    def __init__(self, starting_data, label):
        self.ventricle_label = label
        self.data = starting_data
        self.layers = 0
        self.csfFunction = None
        self.csf_configured = False

    @abstractmethod
    def preprocess_data(self):
        raise NotImplementedError

    def coarsen(self, VOXEL_SIZE=2):
        print("########## Coarsening data ##########")
        self.data = bm.coarsen(VOXEL_SIZE, self.data)

    def clean_data(self):
        bm.clean_region(self.data, self.ventricle_label)
        bm.clean_voxel_data(self.data)

    def remove_disconnected_regions(self):
        change = True
        iteration_count = 0
        while change and iteration_count < 10:
            iteration_count += 1
            # Find and fill erroneous voids within model
            print("########## Removing voids from data ##########")
            print("### Iteration number " + str(iteration_count))
            maze = Maze.Maze(self.data)
            solver = Maze_Solver.Maze_Solver(maze)
            voids_to_fill = solver.find_voids()
            solver.fill_voids(voids_to_fill)

            print("########## Removing disconnected regions from data ##########")
            cont_data = bm.create_binary_image(self.data)
            cont_data = cont_data - 1
            cont_data = cont_data * (-1)

            maze2 = InverseMaze.InverseMaze(cont_data)
            solver2 = Maze_Solver.Maze_Solver(maze2)
            voids_to_fill = solver2.find_voids()

            for key in voids_to_fill:
                [x, y, z] = [int(x) for x in key.split("-")]
                self.data[x, y, z] = 0

            change = bm.clean_voxel_data(self.data)

    def set_ventricle_label(self,ventricle_label):
        self.ventricle_label = ventricle_label

    def set_csf_data(self, layers, csfFunction):
        self.layers = layers
        self.csfFunction = csfFunction
        self.csf_configured = True

    def add_csf(self, layers, csfFunction):
        if csfFunction is not None:
            assert callable(csfFunction)
            print("########## Adding layers of CSF ##########")
            csfFunction(self.data, layers=layers)

            print("########## Checking for voids in csf data ##########")
            csf_maze = Maze.Maze(self.data)
            solver3 = Maze_Solver.Maze_Solver(csf_maze)
            voids_to_fill = solver3.find_voids()
            solver3.fill_voids(voids_to_fill)

class PreprocessorBasic(IPreprocessor):

    def preprocess_data(self):
        super().coarsen()
        super().clean_data()
        super().remove_disconnected_regions()

        if self.csf_configured:
            super().add_csf(self.layers, self.csfFunction)
        else:
            print("CSF not added.")
        return self.data


class PreprocessorSimple(IPreprocessor):

    def preprocess_data(self):
        super().coarsen()
        super().clean_data()
        super().remove_disconnected_regions()
        return self.data


class PreprocessorLesion(IPreprocessor):

    def __init__(self, starting_data, ventricle_label, lesion_label):
        super().__init__(starting_data, ventricle_label)
        self.lesion_label = lesion_label
        self.edemic_layers = 1
        self.config = None

    def set_lesion_label(self, label, edemic_layers):
        self.lesion_label = label
        self.edemic_layers = edemic_layers

    def add_config(self, config_file):
        self.config = config_file

    def insert_lesion(self):
        ventricle_data = bm.create_binary_image(self.data, search=4)
        ventricle_bounding_box = bm.get_bounding_box(ventricle_data)

        # 2. left use maxX ritgh use minX both : use zmin and z max
        brain_data = bm.create_binary_image(self.data)
        brain_bounding_box = bm.get_bounding_box(brain_data)
        brain_bounding_box_minimums = [x + 30 for x in brain_bounding_box[3:]]
        brain_bounding_box_maximums = [x - 30 for x in brain_bounding_box[:3]]

        center = []
        for d in range(3):
            center.append((brain_bounding_box_maximums[d] + brain_bounding_box_minimums[d]) / 2.)
        # 3.
        corpus_callosum_data = bm.create_binary_image(self.data, search=251)
        corpus_callosum_bounding_box = bm.get_bounding_box(corpus_callosum_data)

        # Extra: determine left or right: Create random number if divisible by 2 == right
        num = randint(0, 9999)
        right = True if (num % 2 == 0) else False

        # Answer
        x_limits = [center[0] if right else brain_bounding_box_minimums[0],
                    brain_bounding_box_maximums[0] if right else center[0]]
        y_limits = [ventricle_bounding_box[4], corpus_callosum_bounding_box[1]]
        z_limits = [brain_bounding_box_minimums[2] + 40, brain_bounding_box_maximums[2] - 40]

        npara = int(3)
        nsamp = int(20)
        l_bound = [x_limits[0], y_limits[0], z_limits[0]]
        u_bound = [x_limits[1], y_limits[1], z_limits[1]]

        # Latin hypercube 20 points within region
        sampler = qmc.LatinHypercube(d=npara)
        sample = sampler.random(n=nsamp)
        lub = qmc.scale(sample, l_bound, u_bound)
        lub = np.array([[int(a) for a in arr] for arr in lub])
        count = 0
        for lesion_loc in lub:
            count += 1
            # 4. Get surrounding data and check for ventricles
            surrounding_data = self.data[lesion_loc[0] - 5:lesion_loc[0] + 6,
                                         lesion_loc[1] - 5:lesion_loc[1] + 6,
                                         lesion_loc[2] - 5:lesion_loc[2] + 6]
            labels_in_data = list(np.unique(surrounding_data))
            if not labels_in_data.count(4):
                print("Lesion location {} suitable".format(count))
                self.config.write_to_config("Lesion location", [str(x) for x in lesion_loc])
                lesion_size = 3
                for x in range(lesion_loc[0] - lesion_size, lesion_loc[0] + lesion_size + 1):
                    for y in range(lesion_loc[1] - lesion_size, lesion_loc[1] + lesion_size + 1):
                        for z in range(lesion_loc[2] - lesion_size, lesion_loc[2] + lesion_size + 1):
                            self.data[x, y, z] = 25
                return
        return

    def preprocess_data(self):
        self.insert_lesion()
        super().coarsen()
        super().clean_data()

        # Clean lesion
        pp.CleanLesion(self.lesion_label).performAction(self.data)
        # Add edemic Tissue number of layers of tissue around lesion
        pp.AddEdemicTissue(lesion_label=self.lesion_label, layers=self.edemic_layers).performAction(self.data)

        super().remove_disconnected_regions()
        if self.csf_configured:
            super().add_csf(self.layers, self.csfFunction)
        else:
            print("CSF not added.")
        return self.data


class PreProcessorFactory:

    @staticmethod
    def get_preprocessor(config_data, data):

        ventricle_label = config_data.get_material_value("ventricle")
        if ventricle_label < 0:
            ventricle_label = config_data.get_material_value("ventricles")
        if ventricle_label < 0:
            ventricle_label = 4

        if config_data.get('model_type') == 'lesion':

            lesion_label = config_data.get_material_value("lesion")
            if lesion_label < 0:
                lesion_label = config_data.get_material_value("lesions")
            if lesion_label < 0:
                lesion_label = 25

            preprocessor = PreprocessorLesion(data, ventricle_label, lesion_label)
            preprocessor.set_lesion_label(lesion_label, config_data.get('lesion_layers'))
            preprocessor.add_config(config_data)
        else:
            preprocessor = PreprocessorBasic(data, ventricle_label)

        assert isinstance(preprocessor, IPreprocessor)
        if config_data.get('add_csf'):
            config_data.MATERIAL_LABELS.updateLabelInMap("csf", 24)
            csf_function = CSFFunctions.get_csf_function(config_data.get('csf_type'))
            preprocessor.set_csf_data(config_data.get('csf_layers'), csf_function)

        preprocessor.set_ventricle_label(ventricle_label)
        return preprocessor
