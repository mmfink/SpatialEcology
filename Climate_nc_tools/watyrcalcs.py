# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 10:54:06 2017 Last updated 03/21/2018

Author:  Michelle M. Fink
         Colorado Natural Heritage Program, Colorado State University

License: Creative Commons Attribution 4.0 International (CC BY 4.0)
 http://creativecommons.org/licenses/by/4.0/

Purpose: Create seasonal summarized climate metrics that follow a 'water year.'
The idea here is to make sure that Winter includes the December from the year *before*

Disclaimer:
See Section 5 of the license for Disclaimer of Warranties and Limitation of
Liability. This disclaimer applies to the author, The Colorado Natural Heritage
Program, Colorado State University, and the State of Colorado.
"""

import numpy as np
from netCDF4 import date2num

SEASONS_LU = {1:1, 2:1, 12:1, 3:2, 4:2, 5:2, 6:3, 7:3, 8:3, 9:4, 10:4, 11:4}
WATERYR_LU = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:-1, 11:-1, 12:-1}
ANN_LU = {1:0, 2:0, 12:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0}

def clean_name(inmodel, inseason, invar):
    """Create a clean naming prefix for output files
    inputs:
    inmodel = string; the name of the climate model, usually from nc filename
      or internal variable value.
    inseason = integer; taken from SEASONS_LU dictionary
    invar = string; the nc variable being analyzed

    output: a string to be used as an output file naming prefix
    """
    modname = inmodel.replace('.1.', '_')
    modname = modname.replace('-', '_')
    if inseason == 1:
        when = "winter"
    elif inseason == 2:
        when = "spring"
    elif inseason == 3:
        when = "summer"
    elif inseason == 4:
        when = "autumn"
    elif inseason == 0:
        when = "annual"
    else:
        when = "monthly"
    namestr = "_".join([modname, when, invar])
    return namestr

def watyrmask(orig_dates, datelist, yrlist, season, **kwargs):
    """Alter the seasonal masks to follow a 'water year' instead of a calendar year
    inputs:
    orig_dates = ndarray; the original time values of the netCDF converted to dates
    datelist = list; the original time values of the netCDF flattened to a list
    yrlist = list; the range of four-digit years of interest
    season = integer; taken from SEASONS_LU dictionary
    kwargs = dictionary; additional variables defining time units and calendar
      defaults: {'units':'days since 1950-01-01 00:00:00', 'calen':'gregorian'}

    output: a new set of masks
    """
    if kwargs == {}:
        kwargs = {'units':'days since 1950-01-01 00:00:00', 'calen':'gregorian'}
    yrs = np.array([a_date.year for a_date in orig_dates], dtype=np.int)
    mths = np.array([a_date.month for a_date in orig_dates], dtype=np.int)
    if season == 0:
        seasons = np.array([ANN_LU[m] for m in mths], dtype=np.int)
    else:
        seasons = np.array([SEASONS_LU[m] for m in mths], dtype=np.int)
    omasks = []
    for a_yr in yrlist:
        omasks.append(np.ma.where(np.ma.logical_and(yrs == a_yr,
                                                    seasons == season))[0])
    water_dates = np.array(
        [a_date.replace(
            year=a_date.year + WATERYR_LU[a_date.month]) for a_date in orig_dates])
    water_slice = date2num(water_dates, kwargs['units'], kwargs['calen'])
    newmasks = []
    for z in omasks:
        newmasks.append([datelist.index(water_slice[a]) for a in z])
    return newmasks
