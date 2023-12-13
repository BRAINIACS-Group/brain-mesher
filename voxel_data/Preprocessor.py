import voxel_data.voxel_data_utils as bm
from voxel_data.void_filler import Maze, InverseMaze, Maze_Solver
from abc import ABC, abstractmethod
from voxel_data.csf_functions import CSFFunctions


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


class PreProcessorFactory:

    @staticmethod
    def get_preprocessor(config_data, data):

        ventricle_label = config_data.get_material_value("ventricle")
        if ventricle_label < 0:
            ventricle_label = config_data.get_material_value("ventricles")
        if ventricle_label < 0:
            ventricle_label = 4

        preprocessor = PreprocessorBasic(data, ventricle_label)

        assert isinstance(preprocessor, IPreprocessor)
        if config_data.get('add_csf'):
            config_data.MATERIAL_LABELS.updateLabelInMap("csf", 24)
            csf_function = CSFFunctions.get_csf_function(config_data.get('csf_type'))
            preprocessor.set_csf_data(config_data.get('csf_layers'), csf_function)

        preprocessor.set_ventricle_label(ventricle_label)
        return preprocessor
