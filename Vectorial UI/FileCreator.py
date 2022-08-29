#Program to create a .yaml file from the data structure CurrentUIRun.
#Uses a nested dict data type to write the file.
#
#Author: Jacob Duffy
#Version: 8/25/2022

import os
import yaml
from datetime import datetime

#Method to create a dictionary
#Returns the completed dictionary
def createDictionary(CurrentUIRun):
    #Creates the production dictionary
    if(CurrentUIRun.TimeVariationType == 'sine wave'):
        params = {'amplitude' : CurrentUIRun.SinAmp, 'period' : CurrentUIRun.SinPer,
        'delta' : CurrentUIRun.SinDelta}
        production = {'base_q' : CurrentUIRun.BaseQ,
        'time_variation_type' : CurrentUIRun.TimeVariationType, 'params' : params}
    elif(CurrentUIRun.TimeVariationType == 'gaussian'):
        params = {'amplitude' : CurrentUIRun.GausAmp, 'std_dev' : CurrentUIRun.GausSTD,
        't_max' : CurrentUIRun.GausT_Max}
        production = {'base_q' : CurrentUIRun.BaseQ,
        'time_variation_type' : CurrentUIRun.TimeVariationType, 'params' : params}
    elif(CurrentUIRun.TimeVariationType == 'square pulse'):
        params = {'amplitude' : CurrentUIRun.SquareAmp, 'duration' : CurrentUIRun.SquareDur,
        't_start' : CurrentUIRun.SquareT_Start}
        production = {'base_q' : CurrentUIRun.BaseQ,
        'time_variation_type' : CurrentUIRun.TimeVariationType, 'params' : params}
    else:
        production = {'base_q' : CurrentUIRun.BaseQ,
        'time_variation_type' : CurrentUIRun.TimeVariationType}   

    #Creates the parent dictionary
    parent = {'name' : CurrentUIRun.ParentName, 
    'v_outflow' : CurrentUIRun.VOutflow, 
    'tau_d' : CurrentUIRun.TauD, 'sigma' : CurrentUIRun.Sigma, 
    'T_to_d_ratio' : CurrentUIRun.TtoDRatio}

    #Creates the fragment dictionary
    fragment = {'name' : CurrentUIRun.FragmentName, 
    'v_photo' : CurrentUIRun.VPhoto, 
    'tau_T' : CurrentUIRun.TauT}

    #Creates the comet dictionary
    comet = {'name' : CurrentUIRun.CometName, 'rh' : CurrentUIRun.Rh, 
    'delta' : CurrentUIRun.CometDelta, 
    'transform_method' : CurrentUIRun.TransformMethod, 
    'transform_applied' : CurrentUIRun.ApplyTransforMethod}

    #Creates the grid dictionary
    grid = {'radial_points' : CurrentUIRun.RadialPoints, 
    'angular_points' : CurrentUIRun.AngularPoints, 
    'radial_substeps' : CurrentUIRun.RadialSubsteps}

    #Creates the etc dictionary
    etc = {'print_binned_times' : True, 'print_column_density' : True, 
    'print_progress' : True, 'print_radial_density' : True,
    'pyv_coma_pickle' : CurrentUIRun.PyvComaPickle,
    'pyv_date_of_run' : datetime.now(), 'show_3d_column_density_centered' : True,
    'show_3d_column_density_off_center' : True, 'show_agreement_check' : True,
    'show_aperture_checks' : True, 'show_column_density_plots' : True,
    'show_fragment_sputter' : True, 'show_radial_plots' : True}

    #Creates the final dictionary and returns it
    dict = {'production' : production, 'parent' : parent, 'comet' : comet,
    'fragment' : fragment, 'grid' : grid, 'etc' : etc}

    return dict

#Creates a new .yaml file called pyvectorial.yaml based on the return val of createDictionary()
def newFileManual(CurrentUIRun):
    with open(r'pyvectorial.yaml', 'w') as file:
        documents = yaml.dump(createDictionary(CurrentUIRun), file)

#Creates a new .yaml file saved to a filePath (including file name) with a given dict imput
def newFileInputs(filePath, dict):
    with open(f'{filePath}', 'w') as file:
        documents = yaml.dump(dict, file)

#Deletes a file named fileName
def removeFile(fileName):
    os.remove(fileName)