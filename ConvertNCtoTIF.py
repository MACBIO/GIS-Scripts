from osgeo import gdal
from osgeo import osr
from datetime import datetime
import netCDF4
import os
import sys
import numpy as np

inFolder = sys.argv[1]

# create list of netcdf files
fileList = []
for f in os.listdir(inFolder):
	if f.endswith(".nc"):
		fileList.append(f)
scale_factor = 1.0
add_offset = 0.0
noData = 0.0

# convert each file
for i in range(len(fileList)):
	print "processing", str(i + 1), 'of', str(len(fileList))
	f = os.path.join(inFolder, fileList[i])
	outname = os.path.join(inFolder, fileList[i].replace(".nc", ".tif"))
	if not os.path.exists(outname):

		# open netCDF file
		try:
			ds = netCDF4.Dataset(f)
		except:
			print "coundn't open dataset"
			print
			continue
		if ds == None:
			print "coundn't open dataset"
			print
			continue

		# get variables
		varDict = ds.variables
		varNames = [i for i in varDict]
		varName = ''
		for i in range(len(varNames)):
			if not varNames[i]in ['palette',
								  'lat',
								  'lon']:
				if not varNames[i].startswith('qual'):
					varName = varNames[i]
					print varName
					break

		# read data
		arr = ds.variables[varName][:]

		# set up output dataset
		[cols, rows] = arr.shape        
		outdata = gdal.GetDriverByName("GTiff")
		dst_ds = outdata.Create(outname, rows, cols, 1, gdal.GDT_Float32, options = [ 'TILED=YES' ])
		band = dst_ds.GetRasterBand(1)
		band.SetNoDataValue(float(arr.fill_value))
		dst_ds.SetGeoTransform([ds.geospatial_lon_min,
                                        ds.longitude_step,
                                        0.0,
                                        ds.geospatial_lat_max,
                                        0.0,
                                        -ds.latitude_step])
		proj = osr.SpatialReference()
		proj.ImportFromEPSG(4326) 
		dst_ds.SetProjection(proj.ExportToWkt())

		# write output dataset
		band.WriteArray(arr.filled())

		# cleanup
		g = None
		outdata = None
		dst_ds = None

print "finished processing"
