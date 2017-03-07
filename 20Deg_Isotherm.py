import os
import netCDF4
import numpy

inFile = r"C:\temp\temperature_cars2009a.nc"
outFile = r"C:\temp\temperature_cars2009a_isotherm.tif"

print "reading data"

# create netCDF4 object
f = netCDF4.Dataset(inFile)

# read mean temperature variable to numpy array
dataStack = f.variables["mean"][:]
inFileShape = dataStack.shape

# create list of depths with negative values (ascending)
depthList = []
for d in f.variables["depth"][:]:
    depthList.append(int(d * -1))
depthList.reverse()

# create empty output grid
outArray = numpy.zeros((inFileShape[1], inFileShape[2]))

print "processing data"

# find depth of 20 C value
# process each column
for x in range(inFileShape[2]):
    # process each row
    if x % 10 == 0:
        print "processing", str(x), "of", str(inFileShape[2])
    for y in range(inFileShape[1]):
        #print "x:", str(x)
        #print "y:", str(y)
        #example depthProfile = dataStack[:,inFileShape[1]/2,inFileShape[2]/2]
        depthProfile = dataStack[:, y, x]
        isoDepth = numpy.interp(20, depthProfile[::-1], depthList)
        #print isoDepth
        outArray[y, x] = isoDepth

# flip array along x axis (it is upside-down for some reason)
outArray = numpy.flipud(outArray)
# convert from 64-bit values to 32-bit values
outArray = outArray.astype("float32")

print "writing output"

### write output file (gdal)
##from osgeo import gdal
##from osgeo import osr
##print "creating output file"
##myOutDrv = gdal.GetDriverByName('GTiff')
##myOutDtype = "GDT_Int16" # Sixteen bit signed integer
##myOut = myOutDrv.Create(outFile, inFileShape[1], inFileShape[2], 1, myOutDtype)
##proj = osr.SpatialReference()
##proj.SetWellKnownGeogCS("WGS84")
##myOut.SetProjection(proj)
##myOutB = myOut.GetRasterBand(1)
##myOutB.SetNoDataValue(0)
##myOutB.WriteArray(outArray)

# write output file (arcpy)
import arcpy
raster = arcpy.NumPyArrayToRaster(outArray, arcpy.Point(-0.25, -75.25), .5, .5, 0)
raster.save(outFile)

print "finished"
