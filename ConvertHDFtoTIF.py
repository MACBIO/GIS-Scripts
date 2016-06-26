from osgeo import gdal
from osgeo import osr
from datetime import datetime
import os
import sys
import numpy as np

inFolder = sys.argv[1]
#inFolder = r"D:\Workfolders\MACBIO\MARINE_SPATIAL_PLANNING\GIS\Regional\Datasets\Oceanography\AquaModis\Chlorophyll"

# create list of hdf files
fileList = []
for f in os.listdir(inFolder):
    if f.endswith(".hdf"):
        fileList.append(os.path.join(inFolder, f))

# convert each file
for i in range(len(fileList)):
    print "processing", str(i + 1), 'of', str(len(fileList))
    f = fileList[i]
    outname = f.replace(".hdf", ".tif")
    g = gdal.Open(f)
    
    arr = g.ReadAsArray()
    arr = np.array(arr)
    [cols, rows] = arr.shape
    
    outdata = gdal.GetDriverByName("GTiff")
    
    dst_ds = outdata.Create(outname, rows, cols, 1, gdal.GDT_Float32, options = [ 'TILED=YES' ])
    
    band = dst_ds.GetRasterBand(1)
    NDV = g.GetMetadataItem('FILL')
    band.SetNoDataValue(float(NDV))
    dst_ds.SetGeoTransform([-180.0, 0.04166666791, 0.0, 90.0, 0.0, -0.04166666791])
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(4326) 
    dst_ds.SetProjection(proj.ExportToWkt())
    dst_ds.SetMetadataItem('SENSOR', 'AQUA_MODIS')
    dst_ds.SetMetadataItem('RESOLUTION', '4km')
    dst_ds.SetMetadataItem('DATA START DAY', g.GetMetadataItem('Period Start Day'))
    dst_ds.SetMetadataItem('DATA END DAY', g.GetMetadataItem('Period End Day'))
    dst_ds.SetMetadataItem('DATA START YEAR', g.GetMetadataItem('Period Start Year'))
    dst_ds.SetMetadataItem('DATA END YEAR', g.GetMetadataItem('Period End Year'))
    date = datetime.now()
    date = date.strftime('%Y-%m-%d')
    dst_ds.SetMetadataItem('DOWNLOAD_DATE', date)
    dst_ds.SetMetadataItem('DOWNLOAD_FROM', 'NASA OCEANCOLOUR')
    dst_ds.SetMetadataItem('PROCESSING_TIME',g.GetMetadataItem('Processing Time'))
    dst_ds.SetMetadataItem('PROCESSING_VERSION',g.GetMetadataItem('Processing Version'))
    dst_ds.SetMetadataItem('PARAMETER', g.GetMetadataItem('Parameter'))
    dst_ds.SetMetadataItem('UNITS', g.GetMetadataItem('Units'))
    dst_ds.SetMetadataItem('NODATA VALUE', str(NDV))
    dst_ds.SetMetadataItem('YEAR', g.GetMetadataItem('Start Year'))
    band.WriteArray(arr)
    
    g = None
    outdata = None
    dst_ds = None

print "finished processing"
