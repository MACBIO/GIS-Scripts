import os
import netCDF4
import numpy

inFile = r"C:\temp\temperature_cars2009a.nc"
outValueFile = r"C:\temp\temperature_cars2009a_value.tif"
outDepthFile = r"C:\temp\temperature_cars2009a_depth.tif"

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
#depthList.reverse()

# create empty output grid
outValueArray = numpy.zeros((inFileShape[1], inFileShape[2]))
outDepthArray = numpy.zeros((inFileShape[1], inFileShape[2]))

print "processing data"

# find deepest data value
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
        maskEdges = numpy.ma.flatnotmasked_edges(depthProfile)
        if maskEdges != None:
            lastValue = depthProfile[maskEdges[1]]
            outValueArray[y, x] = lastValue
            lastDepth = depthList[maskEdges[1]]
            outDepthArray[y, x] = lastDepth

# flip array along x axis (it is upside-down for some reason)
outValueArray = numpy.flipud(outValueArray)
outDepthArray = numpy.flipud(outDepthArray)
# convert from 64-bit values to 32-bit values
outValueArray = outValueArray.astype("float32")
outDepthArray = outDepthArray.astype("float32")

print "writing output"

# write output files
from osgeo import gdal
from osgeo import osr
print "creating output file"
myOutDrv = gdal.GetDriverByName('GTiff')
myOutDtype = gdal.GDT_Float32 # 32 bit float
myOutValues = myOutDrv.Create(outValueFile, inFileShape[2], inFileShape[1], 1, myOutDtype)
myOutDepths = myOutDrv.Create(outDepthFile, inFileShape[2], inFileShape[1], 1, myOutDtype)
proj = osr.SpatialReference()
proj.SetWellKnownGeogCS("WGS84")
myOutValues.SetProjection(proj.ExportToWkt())
myOutDepths.SetProjection(proj.ExportToWkt())

xmin,ymin,xmax,ymax = [0,-90,360,90]
nrows,ncols = numpy.shape(outValueArray)
xres = (xmax-xmin)/float(ncols)
yres = (ymax-ymin)/float(nrows)
geotransform=(xmin,xres,0,ymax,0, -yres)
myOutValues.SetGeoTransform(geotransform)
myOutDepths.SetGeoTransform(geotransform)
myOutB = myOutValues.GetRasterBand(1)
myOutB.SetNoDataValue(0)
myOutB.WriteArray(outValueArray)
myOutB = myOutDepths.GetRasterBand(1)
myOutB.SetNoDataValue(0)
myOutB.WriteArray(outDepthArray)

del myOutValues
del myOutDepths
