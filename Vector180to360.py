import os
import subprocess
import sys

inFile = sys.argv[1]
print "processing:", inFile
ogr2ogrFile = r"C:\Program Files\QGIS Essen\bin\ogr2ogr.exe"

# function that sends command to console
def check_output(command,console):
    if console == True:
        process = subprocess.Popen(command)
    else:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output,error = process.communicate()
    returncode = process.poll()
    return returncode,output 

# process shapefile
part1 = inFile.split(os.extsep)[0] + "_pt1.shp"
part2 = inFile.split(os.extsep)[0] + "_pt2.shp"
part2shifted = inFile.split(os.extsep)[0] + "_pt2s.shp"
outFile = inFile.split(os.extsep)[0] + "_360.shp"
if not os.path.exists(outFile):
    # clip part 1
    args = []
    args.append('"'+ogr2ogrFile+'"')
    args.append('-f')
    args.append('"ESRI Shapefile"')
    args.append('"'+part1+'"')
    args.append('"'+inFile+'"')
    args.append('-clipsrc 0 -90 180 90')
    args.append('-skipfailures')
    args.append('-progress')
    #args.append('-nlt POINT')
    command = " ".join(args)
    print command
    returncode,output = check_output(command, True)
    print output
    # clip part 2
    args = []
    args.append('"'+ogr2ogrFile+'"')
    args.append('-f')
    args.append('"ESRI Shapefile"')
    args.append('"'+part2+'"')
    args.append('"'+inFile+'"')
    args.append('-clipsrc -180 -90 0 90')
    args.append('-skipfailures')
    args.append('-progress')
    #args.append('-nlt POINT')
    command = " ".join(args)
    print command
    returncode,output = check_output(command, True)
    print output
    # shift part 2 by -360
    args = []
    args.append('"'+ogr2ogrFile+'"')
    args.append('-f')
    args.append('"ESRI Shapefile"')
    args.append('"'+part2shifted+'"')
    args.append('"'+part2+'"')
    args.append('-dialect sqlite -sql "SELECT ShiftCoords(Geometry,360,0), * FROM')
    args.append(os.path.basename(part2).split(os.extsep)[0] + '"')
    args.append('-progress')
    command = " ".join(args)
    print command
    returncode,output = check_output(command, True)
    print output
    # write part 1 to output
    args = []
    args.append('"'+ogr2ogrFile+'"')
    args.append('-f')
    args.append('"ESRI Shapefile"')
    args.append('"'+outFile+'"')
    args.append('"'+part1+'"')
    args.append('-progress')
    command = " ".join(args)
    print command
    returncode,output = check_output(command, True)
    print output
    # write part 2 to output
    args = []
    args.append('"'+ogr2ogrFile+'"')
    args.append('-f')
    args.append('"ESRI Shapefile"')
    args.append('-update -append')
    args.append('"'+outFile+'"')
    args.append('"'+part2shifted+'"')
    args.append('-progress')
    command = " ".join(args)
    print command
    returncode,output = check_output(command, True)
    print output
    # delete temporary files
    for f in [os.path.basename(f) for f in [part1, part2, part2shifted]]:
        for g in os.listdir(os.path.dirname(inFile)):
            if g.split(os.extsep)[0] == f.split(os.extsep)[0]:
                if os.path.exists(os.path.join(os.path.dirname(inFile), g)):
                    os.remove(os.path.join(os.path.dirname(inFile), g))
