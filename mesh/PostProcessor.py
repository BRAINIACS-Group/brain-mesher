from abc import ABC, abstractmethod


class IPostProcessor(ABC):

    def __init__(self, config, mesh):
        self.config = config
        self.mesh = mesh

    @abstractmethod
    def post_process(self):
        raise NotImplementedError


class PostProcessor(IPostProcessor):

    def post_process(self):
        return


class PostProcessorDecorator(IPostProcessor):
    _post_processor: IPostProcessor = None

    def __init__(self, post_processor: IPostProcessor):
        self._post_processor = post_processor
        super().__init__(post_processor.config, post_processor.mesh)

    @property
    def post_processor(self):
        return self._post_processor

    def post_process(self):
        self._post_processor.post_process()


class SmoothMesh(PostProcessorDecorator):

    def __init__(self, post_processor: IPostProcessor, coeffs, iterations, excluded_regions=None):
        super().__init__(post_processor)
        if excluded_regions is None:
            excluded_regions = []
        self.mesh_refiner = None
        self.excluded_regions = excluded_regions
        self.coeffs = coeffs
        self.iterations = iterations

    def post_process(self):
        self.smooth_mesh()
        return super().post_process()

    def smooth_mesh(self):
        # Smooth outer surface of mesh (including CSF)
        print("########## Smoothing mesh excluding elements with material types: {} ##########"
              .format(",".join([str(x) for x in self.excluded_regions])))
        self.mesh.smooth_mesh(self.coeffs, self.iterations, elementsNotIncluded=self.excluded_regions)


class RemoveRegion(PostProcessorDecorator):

    def __init__(self, post_processor: IPostProcessor, region_label):
        super().__init__(post_processor)
        self.region_label = region_label

    def post_process(self):
        self.remove_region()
        return super().post_process()

    def remove_region(self):
        print("########## Removing region {} ##########".format(self.region_label))
        self.mesh.remove_region(self.region_label)
