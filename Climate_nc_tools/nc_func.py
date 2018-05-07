# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31, 2017 Last updated 03/21/2018

Author:  Michelle M. Fink
         Colorado Natural Heritage Program, Colorado State University

License: Creative Commons Attribution 4.0 International (CC BY 4.0)
 http://creativecommons.org/licenses/by/4.0/

Purpose: Helper functions for analyzing netCDF files (climate models)

Disclaimer:
See Section 5 of the license for Disclaimer of Warranties and Limitation of
Liability. This disclaimer applies to the author, The Colorado Natural Heritage
Program, Colorado State University, and the State of Colorado.
"""
import time
import numpy as np
from osgeo import osr, gdal
from netCDF4 import Dataset

gdal.UseExceptions()

def calc_it(data, masks, method):
    """Run basic calculations on a masked array
    Right now method can be either 'sum' or 'mean' along time axis
    data = ndarray
    masks = masks used to group data by years, seasons, month, etc.
    method = string; 'sum' or 'mean'

    output: ndarray reduced by calculation to a time dimension of 1.
    """
    if method == 'sum':
        return np.ma.array([np.ma.sum(np.ma.take(data, aMask, axis=0), axis=0,
                                      dtype=np.float) for aMask in masks])
    elif method == 'mean':
        return np.ma.array([np.ma.mean(np.ma.take(data, aMask, axis=0), axis=0,
                                       dtype=np.float) for aMask in masks])

def reverse(array, axis=0):
    """Flip a 2D array derived from a netCDF upside down (y axis).
    Necessary if the nc does not treat increasing y's as North,
    which happens more often than you might think.
    """
    idx = [slice(None)]*len(array.shape)
    idx[axis] = slice(None, None, -1)
    return array[idx]

def raster2array(ras_name, flip=True):
    """Convert a geoTIFF to a 2D numpy array.
    Defaults to flipping axis 0 (y axis) on assumption that original
    was flipped.
    """
    ras_tif = gdal.Open(ras_name)
    ras_band = ras_tif.GetRasterBand(1)
    ras_data = ras_band.ReadAsArray()
    ras_tif = None
    if flip:
        ras_ary = reverse(ras_data)
    return ras_ary

def array2raster(new_ras_file, array=None, *arglist):
    """Convert a 2D numpy array to a geoTIFF
    new_ras_file = string; full path and name of output tif
    array = the input array
    arglist = list of additional information
        [raster_origin, pixel_width, pixel_height]
        raster_origin = tuple of minimum X and maximum Y
        pixel_width = horizontal size of each pixel in the projected units
        pixel_height = vertical size of each pixel in the projected units
        NOTE - for decimal degrees in W. hemisphere, pixel_height is negative!

    The defaults provided are very specific to Colorado and the datasets I use,
    so it is very likely you do not want to use them.

    output: geoTIFF
    """
    if arglist == ():
        ras_origin = [-109.375, 41.25]
        pwidth = 0.125
        pheight = -0.125
    else:
        ras_origin = arglist[0]
        pwidth = arglist[1]
        pheight = arglist[2]

    cols = array.shape[1]
    rows = array.shape[0]
    origin_x = ras_origin[0]
    origin_y = ras_origin[1]
    driver = gdal.GetDriverByName('GTiff')
    out_ras = driver.Create(new_ras_file, cols, rows, 1, gdal.GDT_Float32)
    out_ras.SetGeoTransform((origin_x, pwidth, 0, origin_y, 0, pheight))
    outband = out_ras.GetRasterBand(1)
    outband.WriteArray(array)
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(4326)
    out_ras.SetProjection(proj.ExportToWkt())
    print 'Finished writing ' + new_ras_file

def new_nc(array, timeslice, yslice, xslice, outname, **kwargs):
    """Save the given ndarray to a new netCDF file
    array = The ndarray containing variable of interest. Must have 3
      dimensions: time, y (usually latitude), and x (usually longitude).
    timeslice = the ndarray containing the temporal values to assign to 'array'
    yslice = the ndarray containing the vertical coordinates for 'array'
    xslice = the ndarray containing the horizontal coordinates for 'array'
    outname = the full path and name of the output nc file.
    kwargs = dictionary of additional information. Keys = varname, timename,
      xname, yname, units (of time), calendar, metadatastr (describe the dataset)

    default kwargs provided in 'argdic'.

    output: a NETCDF4_CLASSIC file
    """
    argdic = {'varname':'var', 'timename':'time', 'xname':'longitude',
              'yname':'latitude', 'units':'days since 1950-01-01 00:00:00',
              'calendar':'gregorian',
              'metadatastr':''}
    #FIXME: right now there is no error checking regarding shape of array
    # (or anything else for that matter). Assumes dimensions are [time, y, x]
    x = array.shape[2]
    y = array.shape[1]
    if kwargs != {}:
        if 'varname' in kwargs:
            argdic['varname'] = kwargs['varname']
        if 'timename' in kwargs:
            argdic['timename'] = kwargs['timename']
        if 'xname' in kwargs:
            argdic['xname'] = kwargs['xname']
        if 'yname' in kwargs:
            argdic['yname'] = kwargs['yname']
        if 'units' in kwargs:
            argdic['units'] = kwargs['units']
        if 'calendar' in kwargs:
            argdic['calendar'] = kwargs['calendar']
        if 'metadatastr' in kwargs:
            argdic['metadatastr'] = kwargs['metadatastr']
    out_ds = Dataset(outname, 'w', format='NETCDF4_CLASSIC')
    out_ds.createDimension(argdic['timename'], None)
    out_ds.createDimension(argdic['yname'], y)
    out_ds.createDimension(argdic['xname'], x)
    time_var = out_ds.createVariable(argdic['timename'], 'f8', (argdic['timename'],))
    lat_var = out_ds.createVariable(argdic['yname'], 'f4', (argdic['yname'],))
    lon_var = out_ds.createVariable(argdic['xname'], 'f4', (argdic['xname'],))
    cvar = out_ds.createVariable(argdic['varname'], 'f4',
                                 (argdic['timename'], argdic['yname'],
                                  argdic['xname'],))
    time_var[:] = timeslice
    lon_var[:] = xslice
    lat_var[:] = yslice
    cvar[:] = array
    ds_att = {u'description': argdic['metadatastr'],
              u'history': 'Created ' + time.ctime(time.time())}
    time_att = {u'units': argdic['units'], u'calendar': argdic['calendar']}
    out_ds.setncatts(ds_att)
    time_var.setncatts(time_att)
    out_ds.sync()
    out_ds.close()
    print 'Created ' + outname
