print "loading arcpy"
import arcpy
import os

inFolder = r"C:\temp\shapefiles"
intersectFolder = os.path.join(inFolder, "int")
gridFile = r"C:\Users\Jonah\Documents\ArcGIS\Default.gdb\Grid"
arcpy.env.workspace = r"C:\Users\Jonah\Documents\ArcGIS\Default.gdb"
layerName = r"C:\Users\Jonah\Documents\ArcGIS\Default.gdb\gridLayer"
arcpy.MakeFeatureLayer_management(gridFile, layerName)
if not os.path.exists(intersectFolder):
    os.makedirs(intersectFolder)
for f in os.listdir(inFolder):
    if f.endswith(".shp"):
        print "processing", f
        inFile = os.path.join(inFolder, f)
        intFile = os.path.join(intersectFolder, f)
        if not os.path.exists(intFile):
            try:
                print "intersecting", f
                arcpy.Intersect_analysis([inFile, gridFile], intFile, "ALL")
            except BaseException as e:
                print e
            if "area" not in [field.baseName for field in arcpy.ListFields(intFile)]:
                try:
                    print "adding area field to intersected shapefile"
                    arcpy.AddField_management(intFile, "area", "DOUBLE")
                except BaseException as e:
                    print e
            try:
                gridFilename = os.path.basename(gridFile).split(os.extsep)[0]
                arcpy.CalculateField_management(intFile, "area", "!shape.area!" , "PYTHON_9.3")
            except BaseException as e:
                print e
        oldfieldName = f.split(os.extsep)[0]
        newfieldName = os.path.basename(gridFile).split(os.extsep)[0] + "." + f.split(os.extsep)[0]
        fieldList = [f.baseName for f in arcpy.ListFields(gridFile)]
        if oldfieldName not in fieldList:
            try:
                print "adding shapefile name field to grid"
                arcpy.AddField_management(layerName, oldfieldName, "DOUBLE")
            except BaseException as e:
                print e
            try:
                print "joining shapefile to grid"
                arcpy.AddJoin_management(layerName, "ID", intFile, "ID_1")
            except BaseException as e:
                print e
            try:
                print "calculating proportional area"
                gridFilename = os.path.basename(gridFile).split(os.extsep)[0]
                arcpy.CalculateField_management(layerName, newfieldName, "[" + str(oldfieldName) + ".area]/[" + gridFilename + ".Shape_Area]", "VB")
            except BaseException as e:
                print e
            try:
                print "removing join"
                arcpy.RemoveJoin_management(layerName, oldfieldName)
            except BaseException as e:
                print e
        print ""
