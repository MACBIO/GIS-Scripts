import arcpy
import os

inFolder = r'C:\Workfolders\MACBIO\Fiji\MAPS_of_FIJI'
outFolder = r'C:\Workfolders\MACBIO\Fiji\MAPS_of_FIJI'

mapList = []
for f in os.listdir(inFolder):
    if f.startswith("Bioregion") and f.endswith(".mxd"):
        mapList.append(os.path.join(inFolder, f))

for mxdFile in mapList:
    mxd = arcpy.mapping.MapDocument(mxdFile)
    print "processing", os.path.basename(mxdFile)
    outFile = os.path.join(outFolder, os.path.basename(mxdFile).split(os.extsep)[0] + '.png')
    try:
        arcpy.mapping.ExportToPNG(map_document=mxd,
                                  out_png=outFile,
                                  resolution=300)
    except:
        print arcpy.GetMessages()
