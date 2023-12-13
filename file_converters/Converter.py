
from readers.Reader import Reader
from writers.Writers import Writer


class Converter:

    @staticmethod
    def convert_file(path, file1, convert_from, convert_to, filename_out=''):
        split_file1 = file1.split(".")
        ext = ""
        if len(split_file1) < 2:
            if convert_from == 'abaqus':
                ext = "inp"
            elif convert_from == 'vtk':
                ext = "vtk"
        else:
            ext = "".join(split_file1[1].split())

        filename = "".join(split_file1[0].split())
        if filename_out == '':
            filename_out = "_".join([filename_out, "converted"])

        reader = Reader(convert_from)
        reader.openReader(filename, path)
        mesh = reader.getMesh()

        writer = Writer()
        new_filename = filename_out
        if convert_to == 'abaqus':
            writer.openWriter('abaqus', new_filename, path)
        elif convert_to == 'vtk':
            writer.openWriter('vtk', new_filename, path)
        elif convert_to == 'ucd':
            writer.openWriter('ucd', new_filename, path)
        else:
            raise NotImplementedError

        writer.writeMeshData(mesh)
        writer.closeWriter()


if __name__ == "__main__":
    pathout = "C:/Users/grife/OneDrive/Documents/PostDoc/BrainModels/PythonScripts/BrainMesher/Atrophy"
    filename = "OAS1_0004_MR1"
    Converter.convert_file(pathout, filename + "_VTK","vtk","ucd", filename)

