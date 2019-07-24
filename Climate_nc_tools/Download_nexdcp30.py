# -*- coding: utf-8 -*-
"""
Batch download of netCDF files from NEX Amazon AWS bucket
(nasanex.s3.amazonaws.com)

@author: Michelle M. Fink, michelle.fink@colostate.edu
         Colorado Natural Heritage Program, Colorado State University
Created on 05/17/2018 - Built on Python 2.7.14

*IMPORTANT* This script requires wget. On Windows, it needs to be run through
the MinGW shell (or equivalent) in order for the wget command to be recognized.

You must edit the variables below to match the data you want to download.
The code assumes you will always want the historic as well as the future
projected versions of each model.

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
import subprocess
import sys
import os

### Edit these variables as needed
OUTDIR = r"Path\To\Download\Folder"
NEX_URL = "http://nasanex.s3.amazonaws.com/NEX-DCP30/BCSD/$(rcp)/mon/atmos/$(var)" \
    + "/r1i1p1/v1.0/CONUS/$(var)_amon_BCSD_$(rcp)_r1i1p1_CONUS_$(model)_$(date_range).nc"
MODEL_RCP = {"CNRM-CM5": "rcp45", "CESM1-BGC": "rcp85", "HadGEM2-ES": "rcp85"}
NEX_VAR = ["tasmin", "tasmax", "pr"]
HIST_RNG = ["195001-195412", "195501-195912", "196001-196412", "196501-196912",
            "197001-197412", "197501-197912", "198001-198412", "198501-198912",
            "199001-199412", "199501-199912", "200001-200412"]
FUT_RNG = ["202101-202512", "202601-203012", "203101-203512", "203601-204012",
           "204101-204512", "204601-205012", "205101-205512", "205601-206012",
           "206101-206512", "206601-207012", "207101-207512", "207601-208012",
           "208101-208512", "208601-209012", "209101-209512", "209601-209912"]
###

whichModel = MODEL_RCP.viewkeys()
for d in whichModel:
    modURL = NEX_URL.replace("$(model)", d)
    #get historic first
    rcp = "historical"
    rcpURL = modURL.replace("$(rcp)", rcp)
    for var in NEX_VAR:
        varURL = rcpURL.replace("$(var)", var)
        for date_range in HIST_RNG:
            finURL = varURL.replace("$(date_range)", date_range)
            outFile = finURL.rsplit("/", 1)
            outFname = os.path.join(OUTDIR, outFile[1])
            print "Starting download of " + outFile[1]
            try:
                cmd = ["wget", "--passive-ftp", "--retr-symlinks",
                       "--limit-rate=50m", finURL, "-O", outFname]
                subprocess.call(cmd)
                print "Finished downloading " + outFname
            except Exception, e:
                # If an error occurred, print line number and error message
                tb = sys.exc_info()[2]
                print "***ERROR: Line %i" % tb.tb_lineno
                print e.message
    #Now on to projected
    rcp = MODEL_RCP[d]
    rcpURL = modURL.replace("$(rcp)", rcp)
    for var in NEX_VAR:
        varURL = rcpURL.replace("$(var)", var)
        for date_range in FUT_RNG:
            finURL = varURL.replace("$(date_range)", date_range)
            outFile = finURL.rsplit("/", 1)
            outFname = os.path.join(OUTDIR, outFile[1])
            print "Starting download of " + outFile[1]
            try:
                cmd = ["wget", "--passive-ftp", "--retr-symlinks",
                       "--limit-rate=50m", finURL, "-O", outFname]
                subprocess.call(cmd)
                print "Finished downloading " + outFname
            except Exception, e:
                # If an error occurred, print line number and error message
                tb = sys.exc_info()[2]
                print "***ERROR: Line %i" % tb.tb_lineno
print "All done!"
