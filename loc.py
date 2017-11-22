# from osgeo import gdal
# from osgeo import osr

# src = osr.SpatialReference()
# src.SetWellKnownGeogCS("WGS84")
# dataset = gdal.Open("i1.jp2", gdal.GA_ReadOnly)
# projection = dataset.GetProjection()
# dst = osr.SpatialReference(projection)
# ct = osr.CoordinateTransformation(src, dst)

# xy = ct.TransformPoint(21.6172, 44.703);

# print xy

from osgeo import gdal
import numpy as np
import math 

from PIL import Image, ImageDraw
from shapely.geometry import Point
from shapely.geometry import Polygon

# Open tif file
ds = gdal.Open('i1.jp2', gdal.GA_ReadOnly)
# GDAL affine transform parameters, According to gdal documentation xoff/yoff are image left corner, a/e are pixel wight/height and b/d is rotation and is zero if image is north up. 
xoff, a, b, yoff, d, e = ds.GetGeoTransform()

print xoff, yoff, a, b, d, e

def pixel2coord(x, y):
    xp = a * x + b * y + xoff
    yp = d * x + e * y + yoff
    return(xp, yp)

def coord2pixel(xp, yp):
    a1 = np.array([[a,b],[d,e]])
    b1 = np.array([xp-xoff,yp-yoff])
    xy = np.linalg.solve(a1,b1)
    x = math.ceil(xy[0])
    y = math.ceil(xy[1])
    print "Solution is -> ", x, y

def cropPolyFromImg(img, poly):
    im = Image.open(img).convert('RGBA')
    pixels = np.array(im)
    im_copy = np.array(im)

    region = Polygon(poly) 
    
    for index, pixel in np.ndenumerate(pixels):
        row, col, channel = index
        if channel != 0:
            continue
        point = Point(row, col)
        if not region.contains(point):
            im_copy[(row, col, 0)] = 255
            im_copy[(row, col, 1)] = 255
            im_copy[(row, col, 2)] = 255
            im_copy[(row, col, 3)] = 0

    cut_image = Image.fromarray(im_copy)
    cut_image.save('polyCrop.jp2')

def cropPoly2(imgName, poly):
    im = Image.open(imgName).convert("RGBA")

    # convert to numpy (for convenience)
    imArray = np.asarray(im)

    # create mask
    polygon = poly #[(444,203),(623,243),(691,177),(581,26),(482,42)]
    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)
    mask = np.array(maskIm)

    # assemble new image (uint8: 0-255)
    newImArray = np.empty(imArray.shape,dtype='uint8')

    # colors (three first columns, RGB)
    newImArray[:,:,:3] = imArray[:,:,:3]

    # transparency (4th column)
    newImArray[:,:,3] = mask*255

    # back to Image from numpy
    newIm = Image.fromarray(newImArray, "RGBA")
    newIm.thumbnail((9000, 9000), Image.ANTIALIAS)
    newIm.save("out.png")

image = "i1.jp2"
reg = [(30,30), (30,9000), (9000, 9000), (9000,30)]
# cropPolyFromImg(imgage, reg)
cropPoly2(image, reg)

# coord2pixel(500327.53, 4999737.16)

# get columns and rows of your image from gdalinfo
# rows = 0#4949 #36+1
# colms = 0#4988 #34+1

# if __name__ == "__main__":
#     for row in  range(0,rows):
#         for col in  range(0,colms): 
#             print 'Printing column and row ',row, col
#             print pixel2coord(col,row)