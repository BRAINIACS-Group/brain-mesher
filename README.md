# BrainMesher

Create a 3D brain mesh from mri images using only hexahedral elements.

1. Import aseg.mgz from freesurfer output (after performing ,recon-all' on mri images)
2. Convert voxel image to point cloud
3. Optional: Add cerebrospinal fluid
4. Convert point cloud to mesh of cube elements
5. Use laplacian smothing on the surface and boundaries

Run **'Brain_creation.py'** to create a brain model as:
* UCD file (to be imported in to dealii via the  GridIn::read_ucd function)
* VTK file (to be viewed in Paraview)
* Abaqus file (can be imported by selecting File->Import->Model)

Edit **'model_config.ini'** only if needed.

Code tested using Python 3.6  
Required packages:
- numpy~=1.25.2
- vtk~=9.2.6
- nibabel~=5.1.0
- scipy~=1.11.2
- pyvista~=0.42.1
- python-dotenv~=1.0.0

