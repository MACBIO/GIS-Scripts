import os
import subprocess
import sys

inFile = sys.argv[1]
gdal_translateFile = r"C:\OSGeo4W64\bin\gdal_translate.exe"
gdal_warpFile = r"C:\OSGeo4W64\bin\gdalwarp.exe"

# function that sends command to console
def check_output(command,console):
    if console == True:
        process = subprocess.Popen(command)
    else:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output,error = process.communicate()
    returncode = process.poll()
    return returncode,output 

# process raster
part1 = inFile.split(os.extsep)[0] + "_pt1.tif"
part2 = inFile.split(os.extsep)[0] + "_pt2.tif"
outFile = inFile.split(os.extsep)[0] + "_360.tif"
if not os.path.exists(outFile):
    # clip part 1
    args = []
    args.append('"'+gdal_translateFile+'"')
    args.append('-projwin -180 90 0 -90')
    args.append('-a_ullr 180 90 360 -90')
    args.append('"'+inFile+'"')
    args.append('"'+part1+'"')
    command = " ".join(args)
    print command
    returncode,output = check_output(command, True)
    print output
    # clip part 2
    args = []
    args.append('"'+gdal_translateFile+'"')
    args.append('-projwin 0 90 180 -90')
    args.append('-a_ullr 0 90 180 -90')
    args.append('"'+inFile+'"')
    args.append('"'+part2+'"')
    command = " ".join(args)
    print command
    returncode,output = check_output(command, True)
    print output
    # merge 2 parts together
    args = []
    args.append('"'+gdal_warpFile+'"')
    args.append('"'+part1+'"')
    args.append('"'+part2+'"')
    args.append('"'+outFile+'"')
    command = " ".join(args)
    print command
    returncode,output = check_output(command, True)
    print output

# delete temporary files
for f in [part1, part2]:
    if os.path.exists(f):
        os.remove(f)
