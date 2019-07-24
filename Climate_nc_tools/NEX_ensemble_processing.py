# -*- coding: utf-8 -*-
"""
Use NEX-DCP30 ensemble averages (https://cds.nccs.nasa.gov/nex/),
 RCP8.5 & Historical datasets to create seasonal temperature and precip metrics
 within the NPS Midwest region.

 This file is an example of using the nc_func and watyrcalcs modules.

*** Notes on the data used ***
 historical = 1970-2000 (actually 12/1999)
 future = 2036-2065

 ppt units are kg m-2 s-1:     1 kg m-2 s-1 = 2600000 mm/month
 temperature units are Kelvin: C = K - 273.15
******

@author: Michelle M. Fink, michelle.fink@colostate.edu
         Colorado Natural Heritage Program, Colorado State University
Created on Jan 25 10:59:32 2018 - Built on python 2.7.14, numpy 1.13.3, netcdf4 1.4.0

Code licensed under the GNU General Public License version 3.
This script is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see https://www.gnu.org/licenses/ 
"""

import os
import numpy as np
from netCDF4 import MFDataset, num2date
import nc_func
import watyrcalcs

session_dir = r'Path\To\ensemble_ave\netCDFs'
outFolder = 'MidwesternRegion'
outdir = os.path.join(session_dir, outFolder)
if not os.path.exists(outdir):
    os.makedirs(outdir)
#%%#
lstVar = ['pr', 'tasmax', 'tasmin']
lstRCP = ['historical', 'rcp85']
#minX, minY, maxX, maxY for NPS Midwestern Region
clipExtent = [-104.06, 33.01, -80.5, 49.39]
#slice index values for the clip extent - NOTE max values = index + 1
clipIndex = [2516, 1074, 5343, 3040]
pixelWidth = 0.00833333333
pixelHeight = -0.00833333333
arglist = [(clipExtent[0], clipExtent[3]), pixelWidth, pixelHeight]
#%%#
#Compile the individual netCDFs for each time period,
# clip to area, and convert to usuable units (not in that order).
for var in lstVar:
    if var == 'pr':
        meta = 'Monthly Precipitation in mm, derived from ensemble average 800m ' \
        'Downscaled NEX CMIP5 Climate Projections for the Continental US'
    elif var == 'tasmax':
        meta = 'Maximum Monthly Temperature in C, derived from ensemble average 800m ' \
        'Downscaled NEX CMIP5 Climate Projections for the Continental US'
    else:
        meta = 'Minimum Monthly Temperature in C, derived from ensemble average 800m ' \
        'Downscaled NEX CMIP5 Climate Projections for the Continental US'
    for rcp in lstRCP:
        print var, rcp
        outnc = '_'.join([var, 'NEXDCP', 'ens_avg', rcp])
        outnc = os.path.join(outdir, outnc + '.nc')
        if os.path.isfile(outnc):
            msg = 'The output ' + outnc + ' already exists.' + \
            '\nMoving on.\n'
            print msg
        else:
            #Compile the individual nc files
            strSearch = var + '_ens-avg_amon_' + rcp + '*nc'
            ncMF = MFDataset(session_dir + '\\' + strSearch)
            vVar = ncMF.variables[var]  #[lon,lat,time]
            #Clip to area of interest
            clipData = vVar[:, clipIndex[1]:clipIndex[3], clipIndex[0]:clipIndex[2]]
            vLon = ncMF.variables['lon']
            lnSlice = vLon[clipIndex[0]:clipIndex[2]]
            vLat = ncMF.variables['lat']
            ltSlice = vLat[clipIndex[1]:clipIndex[3]]
            #Convert the units
            if var == 'pr':
                convData = np.multiply(clipData, 2600000)
            else:
                convData = np.subtract(clipData, 273.15)
            vTime = ncMF.variables['time']
            tData = vTime[:] #Using the full time dimension
            tUnits = vTime.units
            tCalen = vTime.calendar
            ncMF.close()
            #Save as new netCDF
            kwargs = {'varname': var, 'units': tUnits, 'calendar': tCalen,
                      'metadatastr': meta}
            nc_func.new_nc(convData, tData, ltSlice, lnSlice, outnc, **kwargs)
#%%#
#Now get seasonal metrics and deltas
pptnc = os.path.join(outdir, 'pr_NEXDCP_ens_avg_*.nc')
txnc = os.path.join(outdir, 'tasmax_NEXDCP_ens_avg_*.nc')
tnnc = os.path.join(outdir, 'tasmin_NEXDCP_ens_avg_*.nc')
hYrs = range(1971, 1999, 1)
fYrs = range(2037, 2065, 1)

pptDS = MFDataset(pptnc)
tVar = pptDS.variables['time']
pVar = pptDS.variables['pr']
pData = pVar[:]
tData = tVar[:]
tUnits = tVar.units
tCalen = tVar.calendar
vLon = pptDS.variables['longitude']
lnData = vLon[:]
vLat = pptDS.variables['latitude']
ltData = vLat[:]
dateRng = num2date(tData, tUnits, tCalen)
mydates = tData.tolist()
mwargs = {'units': tUnits, 'calen': tCalen}
pptDS.close()
#%%#
for s in range(0, 5):
    print 'Precipitation For season ' + str(s)
    hmask = watyrcalcs.watyrmask(dateRng, mydates, hYrs, s, **mwargs)
    fmask = watyrcalcs.watyrmask(dateRng, mydates, fYrs, s, **mwargs)
    #Precipitation - historic & future means, and percent change
    prefix = watyrcalcs.clean_name('midwest', s, 'pr')
    ftif = os.path.join(outdir, prefix + '_2050.tif')
    htif = os.path.join(outdir, prefix + '_1985.tif')
    chgtif = os.path.join(outdir, prefix + '_pctchange.tif')
    pharray = nc_func.calc_it(pData, hmask, 'sum')
    pfarray = nc_func.calc_it(pData, fmask, 'sum')
    phist_mn = np.mean(pharray, axis=0)
    phist_x = np.where(phist_mn == 0, 0.01, phist_mn) #avoid divide by zero
    pfut_mn = np.mean(pfarray, axis=0)
    pctchg = np.multiply(np.divide(np.subtract(pfut_mn, phist_mn), phist_x), 100)
    phflip = nc_func.reverse(phist_mn)
    pfflip = nc_func.reverse(pfut_mn)
    chgflip = nc_func.reverse(pctchg)
    #Save as geotiffs
    nc_func.array2raster(htif, phflip, *arglist)
    nc_func.array2raster(ftif, pfflip, *arglist)
    nc_func.array2raster(chgtif, chgflip, *arglist)
    #This is a lot to hold in memory, deleting as I go
    del phist_x

del pData
#%%#
txDS = MFDataset(txnc)
tnDS = MFDataset(tnnc)
txVar = txDS.variables['tasmax']
tnVar = tnDS.variables['tasmin']
cols = txVar.shape[2]
rows = txVar.shape[1]
depth = txVar.shape[0]
txData = txVar[:]
txDS.close()
tnData = tnVar[:]
tnDS.close()
mxChunk = np.split(txData, depth)
mnChunk = np.split(tnData, depth)
del txData
del tnData
#Get the mean temperature a chunk at a time so as not to run out of memory
for i in range(depth):
    rawChunk = np.concatenate((mxChunk[i], mnChunk[i]), axis=0)
    aveChunk = np.mean(rawChunk, axis=0, keepdims=True)
    addChunk = np.reshape(aveChunk, (-1, rows, cols))
    if i == 0:
        tmean = np.array(addChunk)
    else:
        tmean = np.concatenate((tmean, addChunk), axis=0)
del mxChunk
del mnChunk

for s in range(0, 5):
    print 'Temperature For season ' + str(s)
    #Mean Temperature - historic & future means, and absolute change (delta)
    prefix = watyrcalcs.clean_name('midwest', s, 'tmean')
    ftif = os.path.join(outdir, prefix + '_2050.tif')
    htif = os.path.join(outdir, prefix + '_1985.tif')
    chgtif = os.path.join(outdir, prefix + '_delta.tif')
    hmask = watyrcalcs.watyrmask(dateRng, mydates, hYrs, s, **mwargs)
    fmask = watyrcalcs.watyrmask(dateRng, mydates, fYrs, s, **mwargs)
    tharray = nc_func.calc_it(tmean, hmask, 'mean')
    tfarray = nc_func.calc_it(tmean, fmask, 'mean')
    thist_mn = np.mean(tharray, axis=0)
    tfut_mn = np.mean(tfarray, axis=0)
    tdelta = np.subtract(tfut_mn, thist_mn)
    thflip = nc_func.reverse(thist_mn)
    tfflip = nc_func.reverse(tfut_mn)
    deltflip = nc_func.reverse(tdelta)
    #Save as geotiffs
    nc_func.array2raster(htif, thflip, *arglist)
    nc_func.array2raster(ftif, tfflip, *arglist)
    nc_func.array2raster(chgtif, deltflip, *arglist)

print 'Completed'
