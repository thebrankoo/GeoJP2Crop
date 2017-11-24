from osgeo import gdal
import numpy as np
import math 
from PIL import Image, ImageDraw
from shapely.geometry import Point
from shapely.geometry import Polygon
import sys
from osgeo import osr
import json

# jp2dump i2.jp2 > meta.xml

def pixel2coord(x, y):
    xp = a * x + b * y + xoff
    yp = d * x + e * y + yoff
    return(xp, yp)

def coord2pixel(xp, yp):
    ds = gdal.Open('i1.jp2', gdal.GA_ReadOnly)
    xoff, a, b, yoff, d, e = ds.GetGeoTransform()
    a1 = np.array([[a,b],[d,e]])
    b1 = np.array([xp-xoff,yp-yoff])
    xy = np.linalg.solve(a1,b1)
    x = math.ceil(xy[0])
    y = math.ceil(xy[1])
    return [x, y]

def cropPolyFromImage(imgName, poly):
    im = Image.open(imgName).convert("RGBA")

    imArray = np.asarray(im)

    polygon = poly 
    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)
    mask = np.array(maskIm)

    newImArray = np.empty(imArray.shape,dtype='uint8')

    newImArray[:,:,:3] = imArray[:,:,:3]

    newImArray[:,:,3] = mask*255

    newIm = Image.fromarray(newImArray, "RGBA")
    newIm.thumbnail((9000, 9000), Image.ANTIALIAS)
    newIm.save("out.png")

def transformWGS84FromLatLon(lat, lon):
    src = osr.SpatialReference()
    src.SetWellKnownGeogCS("WGS84")
    dataset = gdal.Open("i1.jp2", gdal.GA_ReadOnly)
    projection = dataset.GetProjection()
    dst = osr.SpatialReference(projection)
    ct = osr.CoordinateTransformation(src, dst)
    xy = ct.TransformPoint(lon, lat);
    return xy

def parseJSONFile(jsonLocation):
    json_data = open(jsonLocation).read()
    data = json.loads(json_data)
    return data

def cropCoordinates(x, y, radius):
    r = math.sqrt(2)*radius/10
    return [(math.ceil(x-r), math.ceil(y-r)), (math.ceil(x+r),math.ceil(y-r)),(math.ceil(x+r), math.ceil(y+r)), (math.ceil(x-r),math.ceil(y+r))]

inArgs = sys.argv
jsonData = parseJSONFile(inArgs[1])
xy = transformWGS84FromLatLon(jsonData["lat"],jsonData["lon"])
pix = coord2pixel(xy[0], xy[1])
print 'Pixels x,y ', pix
coordinates = cropCoordinates(pix[0], pix[1], jsonData["radius"])
print 'Coordinates ', coordinates
cropPolyFromImage("i1.jp2", coordinates)




# lon = float(inArgs[1])
# lat = float(inArgs[2])
# print transformWGS84FromLatLon(lat, lon)

# ds = gdal.Open('i1.jp2', gdal.GA_ReadOnly)
# xoff, a, b, yoff, d, e = ds.GetGeoTransform()

# image = "i1.jp2"
# reg = [(30,30), (30,9000), (9000, 9000), (9000,30)]
# cropPolyFromImg(imgage, reg)
# cropPoly2(image, reg)
#print sys.argv
# coord2pixel(500327.53, 4999737.16)

# get columns and rows of your image from gdalinfo
# rows = 0#4949 #36+1
# colms = 0#4988 #34+1

# if __name__ == "__main__":
#     for row in  range(0,rows):
#         for col in  range(0,colms): 
#             print 'Printing column and row ',row, col
#             print pixel2coord(col,row)