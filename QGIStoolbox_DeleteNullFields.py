##vectorDataset=vector

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

lyr = iface.activeLayer()
lstDelete = []

for idx in lyr.dataProvider().attributeIndexes():
    uv = lyr.dataProvider().uniqueValues( idx )
    if not uv:
        lstDelete.append( idx )

lyr.dataProvider().deleteAttributes( lstDelete )

# Update the layer structure
lyr.updateFields()