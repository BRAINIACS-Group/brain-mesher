from enum import Enum
from common.brain_regions import BRAINREGIONNUMBERS, NINEREGIONNUMBERS

class Heterogeneity(Enum):
    ONER = 1
    TWOR = 2
    FOURR = 4
    NINER = 9
    NINETEENR = 19


class MaterialsConverter:

    def __init__(self):
        self.converter = {}
        self.materials = [e.value for e in BRAINREGIONNUMBERS]

    def add_conversion(self, original_values, new_value):
        try:
            list(original_values)
        except TypeError:
            original_values = [original_values]
        for n in original_values:
            if not (self.converter.get(n), False):
                self.converter[n] = new_value
            else:
                print("This value already exists in converter")

    def get_converter_list_for_value(self,value):
        return self.converter.get(value,-1)

    def convert_materials_labels(self, mesh):
        for e in mesh.elements.values():
            curr_mats = e.getMaterial()
            new_mats = []
            for m in curr_mats:
                new_mats.append(self.converter[m])
            e.setMaterial(new_mats)

    def brain_stem_converter(self, number):
        for n in self.materials:
            if 173 <= n <= 178:
                self.converter[n] = number

    def basal_ganglia_converter(self, number):
        for n in self.materials:
            if 11 <= n <= 13:
                self.converter[n] = number

    def cortex_converter(self, number):
        for n in self.materials:
            if n > 1000:
                self.converter[n] = number

class NineRegionConverter(MaterialsConverter):

    values = [2, 3, 7, 10, 26, 16, 17, 18, 24, 251]

    def __init__(self):
        super().__init__()
        super().basal_ganglia_converter(NINEREGIONNUMBERS.BG.value)
        super().cortex_converter(NINEREGIONNUMBERS.C.value)
        super().brain_stem_converter(NINEREGIONNUMBERS.BS.value)
        for n in self.materials:
            if not self.converter.get(n, False):
                self.converter[n] = n


class NineteenRegionsConverter(MaterialsConverter):

    values = [18, 3, 26, 16, 175, 174, 173, 178, 2, 251, 11, 12, 13, 7, 10, 17, 4, 1028, 1024, 1029, 1030,
              1011, 1026, 1035]

    def __init__(self):
        super().__init__()
        for n in self.materials:
            if not self.converter.get(n, False):
                self.converter[n] = n

class HomogenousConverter(MaterialsConverter):

    values = [3]

    def __init__(self):
        super().__init__()
        super().basal_ganglia_converter(NINEREGIONNUMBERS.C.value)
        super().cortex_converter(NINEREGIONNUMBERS.C.value)
        super().brain_stem_converter(NINEREGIONNUMBERS.C.value)
        for n in self.materials:
            if not self.converter.get(n, False):
                if n == 24:
                    self.converter[n] = 24
                else:
                    self.converter[n] = NINEREGIONNUMBERS.C.value



class TwoRegionConverter(MaterialsConverter):

    values = [2, 3]

    def __init__(self):
        super().__init__()
        super().basal_ganglia_converter(NINEREGIONNUMBERS.CR.value)
        super().cortex_converter(NINEREGIONNUMBERS.C.value)
        super().brain_stem_converter(NINEREGIONNUMBERS.CR.value)
        white_matter = [2,7,10,26,16,17,18,251]
        for n in self.materials:
            if not self.converter.get(n, False):
                if n == NINEREGIONNUMBERS.CR.value:
                    self.converter[n] = NINEREGIONNUMBERS.C.value
                elif white_matter.count(n):
                    self.converter[n] = NINEREGIONNUMBERS.CR.value
                else:
                    self.converter[n] = 24


class FourRegionConverter(MaterialsConverter):

    values = [2, 3, 7, 251]

    def __init__(self):
        super().__init__()
        super().basal_ganglia_converter(NINEREGIONNUMBERS.CB.value)
        super().cortex_converter(NINEREGIONNUMBERS.C.value)
        super().brain_stem_converter(NINEREGIONNUMBERS.CB.value)
        sub_cortical = [7,10,26,16,17,18]
        for n in self.materials:
            if not self.converter.get(n, False):
                if n == NINEREGIONNUMBERS.C.value:
                    self.converter[n] = NINEREGIONNUMBERS.C.value
                elif n == NINEREGIONNUMBERS.CR.value:
                    self.converter[n] = NINEREGIONNUMBERS.CR.value
                elif n == NINEREGIONNUMBERS.CC.value:
                    self.converter[n] = NINEREGIONNUMBERS.CC.value
                elif sub_cortical.count(n):
                    self.converter[n] = NINEREGIONNUMBERS.CB.value
                else:
                    self.converter[n] = 24


class MaterialsConverterFactory:

    @staticmethod
    def get_converter(converter_type):
        """Returns homogeneity converter

        Parameters
        ----------
        converter_type : Heterogeneity
            Enum of heterogeneity type. Options : ONER | TWOR | FOURR | NINER
        """
        if converter_type == Heterogeneity.ONER:
            return HomogenousConverter()
        elif converter_type == Heterogeneity.TWOR:
            return TwoRegionConverter()
        elif converter_type == Heterogeneity.FOURR:
            return FourRegionConverter()
        elif converter_type == Heterogeneity.NINETEENR:
            return NineteenRegionsConverter()
        else:
            return NineRegionConverter()








