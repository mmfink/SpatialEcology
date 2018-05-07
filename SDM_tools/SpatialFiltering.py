# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 14:03:49 2018

Author: Michelle M. Fink
Colorado Natural Heritage Program, Colorado State University

License: Creative Commons Attribution 4.0 International (CC BY 4.0)
 http://creativecommons.org/licenses/by/4.0/

Purpose: Functions for spatial filtering of points.
Built on python 2.7.14, geopandas 0.3.0, and pysal 1.14.3

Disclaimer:
See Section 5 of the license for Disclaimer of Warranties and Limitation of
Liability. This disclaimer applies to the author, The Colorado Natural Heritage
Program, Colorado State University, and the State of Colorado.
"""

import os
import pysal
import geopandas as gpd

def filter_duplicates(infile, idfield, rankfield, otherfld=None, epsg=None):
    '''Removes spatial duplicates and returns unique shapes with the maximum
    value of specified rankfield. Output is a geopandas dataframe.

    infile: (string) path, filename, and extension of input geodata file (e.g., shapefile)
    idfield: (string) fieldname that uniquely identifies each record
    rankfield: (string) fieldname of a numeric ranking field
    otherfld: (string, optional) a third field to save in the output, only the
        first encountered value among the duplicates is retained.
    epsg: (string, optional) in the form 'epsg:<number>' representing coordinate
        projection of the geodata.
    '''
    geodf = gpd.read_file(infile)
    if epsg is not None:
        geodf.crs = {'init': epsg}
    geodf['xy'] = geodf['geometry'].apply(lambda x: str(x))
    if otherfld is None:
        fldlist = [idfield, 'xy', rankfield, otherfld, 'geometry']
        flddict = {idfield: 'min', rankfield: 'max', otherfld: 'first'}
    else:
        fldlist = [idfield, 'xy', rankfield, 'geometry']
        flddict = {idfield: 'min', rankfield: 'max'}
    geodf = geodf[fldlist]
    nodups = geodf.dissolve(by='xy', aggfunc=flddict)
    return nodups

def filter_by_distance_rank(infile, dist, rankfield):
    '''Thins out a point geodataset so that the selected points represent
    the maximum rankfield value of all points within the specified distance.
    Output is a geopandas dataframe.

    infile: (string) path, filename, and extension of input geodata file (e.g., shapefile)
    dist: (number, float or integer) minimum distance, in projection units
    rankfield: (string) fieldname of a numeric ranking field
    '''
    indf = pysal.pdio.read_files(infile)
    wdist = pysal.weights.DistanceBand.from_dataframe(indf, dist, silent=True)
    wdw = wdist.weights
    wdn = wdist.neighbors

    for fid in wdist:
        nwpairs = [(k, indf[rankfield][k]) for k in fid[1].iterkeys()]
        newdic = dict(nwpairs)
        wdw.update({fid[0]:newdic.values()})
        wdn.update({fid[0]:newdic.keys()})

    wnew = pysal.W(wdn, wdw, silent_island_warning=True)
    keeplst = []
    procd = []

    for nwfid in wnew:
        idx = nwfid[0]
        if len(nwfid[1].keys()) > 0:
            fdict = nwfid[1]
            iwght = indf[rankfield][idx]
            fdict.update({idx:iwght})
            winner = fdict.keys()[fdict.values().index(max(fdict.values()))]
            if winner not in procd:
                keeplst.append(winner)
                procd = procd + wdn[winner]
                procd.append(winner)
        else:
            keeplst.append(idx)
            procd.append(idx)

    keeplst = list(set(keeplst))
    return indf.iloc[keeplst]

if __name__ == "__main__":
    wd = r"D:\GIS\Projects\WYNDD\Final_inputs"
    infile = "Absence_pts_train_raw.shp"
    outfile = "Absence_pts_train_1km.shp"
    infile = os.path.join(wd, infile)
    outfile = os.path.join(wd, outfile)
    # Filter points
    kpdf = filter_by_distance_rank(infile, 1000, 'QRank')
    pysal.pdio.write_files(kpdf, outfile)

    # Remove duplicates
    #NAD83(2011) / Conus Albers = 'epsg:6350'
    outgdf = filter_duplicates(infile, 'OBJECTID', 'QRank', 'Pres_Abs', 'epsg:6350')
    outgdf.to_file(outfile)
