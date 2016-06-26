from osgeo import gdal
import os
import sys
import numpy

#inFolder = r'C:\temp\test'
inFolder = sys.argv[1]
outFile = os.path.join(inFolder, "MEAN.tif")

# delete output file if it exists
if os.path.isfile(outFile):
    os.remove(outFile)

# create list of tif files
fileList = []
for f in os.listdir(inFolder):
    if f.endswith('.tif'):
        fileList.append(os.path.join(inFolder, f))
print str(len(fileList)), 'files found'

# Get information about input files
layers = []
ds0 = gdal.Open(fileList[0], gdal.GA_ReadOnly)
band0 = ds0.GetRasterBand(1)
dataType = ds0.GetRasterBand(1).DataType
NDV0 = ds0.GetRasterBand(1).GetNoDataValue()
calc = band0.ReadAsArray()
layers.append(calc)
dimensions = [ds0.RasterYSize, ds0.RasterXSize]
myNDVs = numpy.zeros(dimensions)
myNDVs = 1 * numpy.logical_or(myNDVs==1, calc==NDV0)
del calc

# set up output file
print "creating output file"
myOutDrv = gdal.GetDriverByName('GTiff')
myOut = myOutDrv.Create(outFile, dimensions[1], dimensions[0], 1, dataType)
myOut.SetGeoTransform(ds0.GetGeoTransform())
myOut.SetProjection(ds0.GetProjection())
myOutB = myOut.GetRasterBand(1)
myOutB.SetNoDataValue(NDV0)

# find block size to chop grids into bite-sized chunks
# use the block size of the first layer to read efficiently
myBlockSize = [256, 256]
# store these numbers in variables that may change later
nXValid = myBlockSize[0]
nYValid = myBlockSize[1]
# find total x and y blocks to be read
nXBlocks = (int)((dimensions[1] + myBlockSize[0] - 1) / myBlockSize[0])
nYBlocks = (int)((dimensions[0] + myBlockSize[1] - 1) / myBlockSize[1])
myBufSize = myBlockSize[0]*myBlockSize[1]

# variables for displaying progress
ProgressCt = -1
ProgressMk = -1
ProgressEnd = nXBlocks * nYBlocks

################################################################
# start looping through blocks of data
################################################################

# loop through X-lines
for X in range(0, nXBlocks):

    # change the block size of the final piece
    if X == nXBlocks - 1:
        nXValid = dimensions[1] - X * myBlockSize[0]
        myBufSize = nXValid*nYValid

    # find X offset
    myX=X*myBlockSize[0]

    # reset buffer size for start of Y loop
    nYValid = myBlockSize[1]
    myBufSize = nXValid*nYValid

    # loop through Y lines
    for Y in range(0,nYBlocks):
        print "processing:", str(X), "of", str(nXBlocks), ",",str(Y), "of", str(nYBlocks)
        
        ProgressCt += 1
        if 10 * ProgressCt / ProgressEnd %10 != ProgressMk:
            ProgressMk = 10 * ProgressCt / ProgressEnd %10
            print 10 * ProgressMk, ".."

        # change the block size of the final piece
        if Y == nYBlocks - 1:
            nYValid = dimensions[0] - Y * myBlockSize[1]
            myBufSize = nXValid*nYValid

        # find Y offset
        myY = Y * myBlockSize[1]

        # create empty buffer to mark where nodata occurs
        myNDVs=numpy.zeros(myBufSize)
        myNDVs.shape=(nYValid,nXValid)

        # fetch data for each input layer
        rasterStack = []
        for i in range(1, len(fileList)):
            ds = gdal.Open(fileList[i], gdal.GA_ReadOnly)
            band = ds.GetRasterBand(1)
            myval = band.ReadAsArray(xoff=myX, yoff=myY, win_xsize=nXValid, win_ysize=nYValid)
            myval = numpy.ma.masked_equal(myval, NDV0)
            rasterStack.append(myval)

        # create an array of values for this block
        rStack = numpy.ma.dstack(rasterStack)            
        myval = numpy.ma.MaskedArray.mean(rStack, axis=2)

        # count nodata values for each cell
        NDVcount = numpy.ma.count_masked(rStack, axis=2)

        # add nodata mask where at least half of the files have nodata
        NDVmask = 1*(NDVcount > (len(fileList)/10))
        numpy.ma.set_fill_value(myval, NDV0)
        myval = numpy.ma.filled(myval)
        #myval = ((1*(NDVmask==0))*myval) + (NDV0*NDVmask)

        # write to output file
        myOutB.WriteArray(myval, xoff=myX, yoff=myY)

# close files
myOut = None
