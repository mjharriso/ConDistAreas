#Coded by Matthew Harrison, July, 2015.
#Read ESRI shapefiles and calculate district areas
#Using Albers Equal Area Projection for North America
#Including Alaska and Hawaii

from mpl_toolkits.basemap import Basemap
from pyproj import Proj
from shapely.geometry import LineString, Point, shape
import fiona
from fiona import collection
import numpy as np
import pandas
import argparse

#Shapefiles should have been downladed from
#http://cdmaps.polisci.ucla.edu/
#and unzipped in the current directory.
for con in np.arange(106,114):
    fnam='districtShapes/districts'+str(con)+'.shp'
    districts=fiona.open(fnam)
    lat1=districts.bounds[1]
    lat2=districts.bounds[3]
    m = Proj(proj='aea',lat_1=lat1,lat_2=lat2,lat_0=np.mean((lat1,lat2)))

    Districts=[]
    for pol in fiona.open(fnam):
# Polygons
        coords=pol['geometry']['coordinates']
        if  pol['geometry']['type'] == 'Polygon':
            lons=[];lats=[]
            for c in coords[0]:
                lons.append(c[0])
                lats.append(c[1])
            try:
                x,y=m(lons,lats)
            except:
                print pol['properties']
                print pol['geometry']['type']
                raise
            poly={'type':'Polygon','coordinates':[zip(x,y)]}
            Districts.append({'STATENAME':pol['properties']['STATENAME'],
            'DISTRICT':pol['properties']['DISTRICT'],
            'COUNTY':pol['properties']['COUNTY'],
            'ID':pol['properties']['ID'],'area':shape(poly).area})
        elif  pol['geometry']['type'] == 'MultiPolygon':
# Multiple Polygons
            for p in coords:
                lons=[];lats=[]
                for c in p[0]:
                    lons.append(c[0])
                    lats.append(c[1])
                try:
                    x,y=m(lons,lats)
                except:
                    print pol['properties']
                    print pol['geometry']['type']
                    raise
                poly={'type':'Polygon','coordinates':[zip(x,y)]}
                Districts.append({'STATENAME':pol['properties']['STATENAME'],
                'DISTRICT':pol['properties']['DISTRICT'],
                'COUNTY':pol['properties']['COUNTY'],
                'ID':pol['properties']['ID'],'area':shape(poly).area})

    Districts=sorted(Districts,key=lambda d:(d['STATENAME'],int(d['DISTRICT'])))
# Write Areas to csv
    filenam='areas'+str(con)+'.txt'
    f=open(filenam,'w')
    pr=None
    for d in Districts:
        if pr is not None:
            if d['STATENAME'] != pr['STATENAME']:
                print d['STATENAME']
            if d['DISTRICT']==pr['DISTRICT']:
                a=a+d['area']
            else:
                line=pr['ID'],pr['DISTRICT'],str(a/1.e6),pr['STATENAME']+'\n'
                f.write(','.join(line))
                a=d['area']
                pr=d.copy()
        else:
            pr=d.copy()
            a=d['area']

    line=pr['ID'],pr['DISTRICT'],str(a/1.e6),pr['STATENAME']+'\n'
    f.write(','.join(line))
    f.close()




