import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

### CREATE LIST OF SUCCESSFULLY CONVERTED CASES (generated from output of dicom2nifti.py) ###

dicom2nifti_success = Path.cwd().parent / 'dicom2nifti_successful.txt'
successful_conv = dicom2nifti_success.read_text()
successful_conv = successful_conv.split('\n')
successful_conv = list(filter(None, successful_conv)) # For sanity - remove any empty string(s)

### CREATE DIRECTORY STRUCTURE FOR SAVING RESAMPLED CASES ###

root_dir = Path.cwd().parent
root_dir.joinpath('nifti_resampled').mkdir()
path_to_nifti_resampled = Path.cwd().parent / 'nifti_resampled'
path_to_nifti_resampled.joinpath('adc').mkdir()
path_to_nifti_resampled.joinpath('bval').mkdir()
path_to_nifti_resampled.joinpath('ktrans').mkdir()
path_to_nifti_resampled.joinpath('t2').mkdir()

### RESAMPLING CASES ###

# Set paths to original data and resampled folders
nifti_folder = Path.cwd().parent / 'nifti_copy'
nifti_resampled_folder = Path.cwd().parent / 'nifti_resampled'


# Set desired spacing based on EDA
desired_voxel = {'t2':(0.5,0.5,3.0),
                 'adc':(2.0,2.0,3.0),
                 'bval':(2.0,2.0,3.0),
                 'ktrans':(1.5,1.5,4.0)}


def resample_voxel_spacing(successful_conv, path_to_nifti, path_to_resampled, desired_voxel_spacing):
    
    def resample_image(desired_voxel_spacing, source_file_path):
        image = sitk.ReadImage(str(source_file_path))
        original_image_spacing = image.GetSpacing()
        
        if original_image_spacing != desired_voxel_spacing:
            
            ### HOW TO RESAMPLE SITK_IMAGE TO A NEW SPACING ###
            ### SOURCE: https://github.com/SimpleITK/SimpleITK/issues/561 ###
            
            # converting to np array for calculations of new_size
            original_size_array = np.array(image.GetSize(), dtype = np.int)
            original_spac_array = np.array(image.GetSpacing())
            desired_spac_array = np.array(desired_voxel_spacing)
            
            new_size = original_size_array * (original_spac_array / desired_spac_array)
            new_size = np.ceil(new_size).astype(np.int)
            new_size = [int(s) for s in new_size]
            new_size = tuple(new_size)
            
            # create the resample filter
            resample = sitk.ResampleImageFilter()
            resample.SetInterpolator(sitk.sitkLinear) 
            resample.SetSize(new_size)
            resample.SetOutputOrigin(image.GetOrigin()) 
            resample.SetOutputSpacing(desired_voxel_spacing)
            resample.SetOutputDirection(image.GetDirection())
            
            resampled_image = resample.Execute(image)
            
            # print the changes
            print('Resampling:', source_file_path.parts[-3:-1])
            print('original spacing:', image.GetSpacing())
            print('desired spacing:', desired_voxel_spacing)
            print('resampled spacing:', resampled_image.GetSpacing())
            print('original size:', image.GetSize())
            print('resampled size:', resampled_image.GetSize())
            print('\n')
            
        else:
            resampled_image = image
            
        return resampled_image
    
    def write_resampled_image(image, path):
        writer = sitk.ImageFileWriter()
        writer.SetFileName(str(path))
        writer.Execute(image)
        return
    
    patient_folders = [x for x in path_to_nifti.iterdir() if x.is_dir()]
    for patient_folder in patient_folders:
        patient_id = patient_folder.parts[-1]
        if patient_folder.stem in successful_conv:
            subdirectories = [x for x in patient_folder.iterdir() if x.is_dir()]
            for subdirectory in subdirectories:
                if 't2' in str(subdirectory):
                    for file_path in subdirectory.rglob('*.*'):
                        path_to_nifti_resampled_t2 = path_to_resampled.joinpath('t2' + '/' + patient_id + '_t2_resampled.nii.gz')
                        t2_resampled = resample_image(desired_voxel.get('t2'), file_path)
                        write_resampled_image(t2_resampled, path_to_nifti_resampled_t2)
                if 'adc' in str(subdirectory):
                    for file_path in subdirectory.rglob('*.*'):
                        path_to_nifti_resampled_adc = path_to_resampled.joinpath('adc' + '/' + patient_id + '_adc_resampled.nii.gz')
                        adc_resampled = resample_image(desired_voxel.get('adc'), file_path)
                        write_resampled_image(adc_resampled, path_to_nifti_resampled_adc)
                if 'bval' in str(subdirectory):
                    for file_path in subdirectory.rglob('*.*'):
                        path_to_nifti_resampled_bval = path_to_resampled.joinpath('bval' + '/' + patient_id + '_bval_resampled.nii.gz')
                        bval_resampled = resample_image(desired_voxel.get('bval'), file_path)
                        write_resampled_image(bval_resampled, path_to_nifti_resampled_bval)
                if 'ktrans' in str(subdirectory):
                    for file_path in subdirectory.rglob('*.*'):
                        path_to_nifti_resampled_ktrans = path_to_resampled.joinpath('ktrans' + '/' + patient_id + '_ktrans_resampled.nii.gz')
                        ktrans_resampled = resample_image(desired_voxel.get('ktrans'), file_path)
                        write_resampled_image(ktrans_resampled, path_to_nifti_resampled_ktrans)                       

resample_voxel_spacing(successful_conv, nifti_folder, nifti_resampled_folder, desired_voxel)