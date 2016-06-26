import os
import subprocess
import sys

inFolder = sys.argv[1]
outFolder = os.path.join(os.path.dirname(inFolder), 'Clipped')

ulx = -180
uly = 0
lrx = -165
lry = -30

ogr2ogrFile = r"C:\Program Files\QGIS Lyon\bin\ogr2ogr.exe"
gdal_translateFile = r"C:\Program Files\QGIS Lyon\bin\gdal_translate.exe"

# function that sends command to console
def check_output(command,console):
    if console == True:
        process = subprocess.Popen(command)
    else:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output,error = process.communicate()
    returncode = process.poll()
    return returncode,output 

# create list of shapefiles
fileList = []
for root, dirs, files in os.walk(inFolder):
    for f in files:
        if f.endswith('.shp'):
            fileList.append(os.path.join(root, f))

# process each shapefile
for f in fileList:
    inFile = f
    outTail = inFile.split(os.path.basename(inFolder))[1]
    outFile = outFolder + outTail
    if not os.path.exists(os.path.dirname(outFile)):
        os.makedirs(os.path.dirname(outFile))
    if not os.path.exists(outFile):
        args = []
        args.append('"'+ogr2ogrFile+'"')
        args.append('-skipfailures')
        args.append('-progress')
        args.append('"'+outFile+'"')
        args.append('"'+inFile+'"')
        args.append('-clipsrc')
        args.append(str(ulx))
        args.append(str(lry))
        args.append(str(lrx))
        args.append(str(uly))
        command = " ".join(args)
        print command
        returncode,output = check_output(command, True)
        print output
    
# create list of tiffs
fileList = []
for root, dirs, files in os.walk(inFolder):
    for f in files:
        if f.endswith('.tif'):
            fileList.append(os.path.join(root, f))

# process each tiff
for f in fileList:
    inFile = f
    outTail = inFile.split(os.path.basename(inFolder))[1]
    outFile = outFolder + outTail
    if not os.path.exists(os.path.dirname(outFile)):
        os.makedirs(os.path.dirname(outFile))
    if not os.path.exists(outFile):
        args = []
        args.append('"'+gdal_translateFile+'"')
        args.append('-projwin')
        args.append(str(ulx))
        args.append(str(uly))
        args.append(str(lrx))
        args.append(str(lry))
        args.append('"'+inFile+'"')
        args.append('"'+outFile+'"')
        command = " ".join(args)
        print command
        returncode,output = check_output(command, True)
        print output
