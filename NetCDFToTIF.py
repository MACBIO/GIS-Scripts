from osgeo import gdal
import os
import numpy

inFolder = r'C:\temp\Currents\Climatology - COADS'

# create list of netcdf files
fileList = []
for f in os.listdir(inFolder):
    if f.endswith(".nc"):
        fileList.append(os.path.join(inFolder, f))

# process each netcdf file with subdatasets
for f in fileList:
    print "processing", os.path.basename(f)
    # open file
    ds = gdal.Open(f)
    # find subdatasets
    subDs = ds.GetSubDatasets()
    # open each subdataset
    for i in range(len(subDs)):
        sDs = gdal.Open(subDs[i][0])
        sdsName = subDs[i][1].split(' ')[1]
        dimensions = [sDs.RasterYSize, sDs.RasterXSize]
        rasterStack = []
        # read each raster
        for i in range(sDs.RasterCount):
            band = sDs.GetRasterBand(i+1)
            NDV = band.GetNoDataValue()
            dataType = band.DataType
            myval = band.ReadAsArray()
            myval = numpy.ma.masked_equal(myval, NDV)
            rasterStack.append(myval)
        # calculate mean
        rStack = numpy.ma.dstack(rasterStack)
        myval = numpy.ma.MaskedArray.mean(rStack, axis=2)
        # write mean raster
        myOutDrv = gdal.GetDriverByName('GTiff')
        outFile = os.path.join(inFolder, os.path.basename(f).split(os.extsep)[0] + "_" + sdsName + ".tif")
        myOut = myOutDrv.Create(outFile, dimensions[1], dimensions[0], 1, dataType)
        myOut.SetGeoTransform(sDs.GetGeoTransform())
        myOutB = myOut.GetRasterBand(1)
        myOutB.SetNoDataValue(NDV)
        myOutB.WriteArray(myval)
        myOut = None
            
### process each netcdf file without subdatasets
##for f in fileList:
##    print "processing", os.path.basename(f)
##    # open file
##    ds = gdal.Open(f)
##    dimensions = [ds.RasterYSize, ds.RasterXSize]
##    rasterStack = []
##    # read each raster
##    for i in range(ds.RasterCount):
##        band = ds.GetRasterBand(i+1)
##        NDV = band.GetNoDataValue()
##        dataType = band.DataType
##        myval = band.ReadAsArray()
##        myval = numpy.ma.masked_equal(myval, NDV)
##        rasterStack.append(myval)
##    # calculate mean
##    rStack = numpy.ma.dstack(rasterStack)
##    myval = numpy.ma.MaskedArray.mean(rStack, axis=2)
##    # write mean raster
##    myOutDrv = gdal.GetDriverByName('GTiff')
##    outFile = os.path.join(inFolder, os.path.basename(f).split(os.extsep)[0] + ".tif")
##    myOut = myOutDrv.Create(outFile, dimensions[1], dimensions[0], 1, dataType)
##    myOut.SetGeoTransform(ds.GetGeoTransform())
##    myOutB = myOut.GetRasterBand(1)
##    myOutB.SetNoDataValue(NDV)
##    myOutB.WriteArray(myval)
##    myOut = None
