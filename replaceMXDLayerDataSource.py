import arcpy
import os

templateMXD = r"C:\Workfolders\MACBIO\Fiji\MAPS_of_FIJI\PA_workshop_July2016.mxd"

inFolder = r'C:\Workfolders\MACBIO\Fiji\MAPS_of_FIJI'
inMXDs = []

for f in os.listdir(inFolder):
    if f.endswith(".mxd") and f.startswith("PA_workshop_July2016"):
        inMXDs.append(os.path.join(inFolder, f))

for fixMXD in inMXDs:
    outMXD = fixMXD.split(os.extsep)[0] + "_fixed.mxd"
    layinfo = {}

    MXD = arcpy.mapping.MapDocument(templateMXD)
    for lyr in arcpy.mapping.ListLayers(MXD):
        if lyr.supports("DATASOURCE"):
            layinfo[lyr.name] = lyr.dataSource
    del MXD
    print str(len(layinfo)), "layers found in template MXD"

    MXD = arcpy.mapping.MapDocument(fixMXD)
    for lyr in arcpy.mapping.ListLayers(MXD):
        if lyr.supports("DATASOURCE"):
            print "processing", lyr.name
            if lyr.isFeatureLayer:
                oldlyrds = lyr.dataSource
                oldWkspcPath = os.path.dirname(oldlyrds)
                lyrnm = lyr.name
                if lyrnm in layinfo:
                    newlyrds = layinfo[lyrnm]
                    if not oldlyrds == newlyrds:
                        newWkspcPath = os.path.dirname(newlyrds)
                        newDsName = os.path.basename(newlyrds).split(os.extsep)[0]
                        try:
                            lyr.replaceDataSource(newWkspcPath, "SHAPEFILE_WORKSPACE", newDsName, "validate")
                        except:
                            print arcpy.GetMessages()
                            print lyrnm, "didn't work"
            if lyr.isRasterLayer:
                oldlyrds = lyr.dataSource
                oldWkspcPath = os.path.dirname(oldlyrds)
                lyrnm = lyr.name
                if lyrnm in layinfo:
                    newlyrds = layinfo[lyrnm]
                    if not oldlyrds == newlyrds:
                        newWkspcPath = os.path.dirname(newlyrds)
                        newDsName = os.path.basename(newlyrds).split(os.extsep)[0]
                        try:
                            lyr.replaceDataSource(newWkspcPath, "RASTER_WORKSPACE", newDsName)
                        except:
                            print arcpy.GetMessages()
                            print lyrnm, "didn't work"

    MXD.saveACopy(outMXD)
    del MXD
