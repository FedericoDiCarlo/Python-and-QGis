#########################################################################################
#########################################################################################
######### Preliminary setup to use when not running the model within QGis################

# Hay que importar las librerías si no corrés en QGIS. Importante tener en cuenta para buscar built-in functions o methods.

# print('preliminary setup')
# import sys
# import os
# Importing commands in order to run vector layers and shapefiles:

# from qgis.core import (
#     QgsApplication, 
#     QgsVectorLayer,
#     QgsCoordinateReferenceSystem,
# )

# from qgis.analysis import QgsNativeAlgorithms

# # See https://gis.stackexchange.com/a/155852/4972 for details about the prefix 
# QgsApplication.setPrefixPath('C:/OSGeo4W64/apps/qgis', True)
# qgs = QgsApplication([], False)
# qgs.initQgis()  
# sys.path.append('C:/OSGeo4W64/apps/qgis/python/plugins')
# Setting processing framework

# En processing están los algoritmos que usamos para que QGIS haga lo que necesitamos (Fix geometries, Drop fields,...)

# import processing
# from processing.core.Processing import Processing
# Processing.initialize()
# QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#########################################################################################
#########################################################################################

# Cambiar YOUR PATH por el directorio.
mainpath = "YOUR PATH"
#Archivo raster que vamos a utilizar (input)
suitin = "{}/suit/suit/hdr.adf".format(mainpath)
#Carpeta donde se van a guardar los outputs
outpath = "{}/_output/".format(mainpath)
#Archivo GIF que vamos a crear (output)
suitout = "{}/landquality.tif".format(outpath)

# Defining a map projection, EPSG:4326
crs_wgs84 = QgsCoordinateReferenceSystem("epsg:4326")

##################################################################
# Reproyección
##################################################################
# definimos lo que queremos reproyectar, creamos un archivo .prj con la proyección para agriculture suitability usando WGS84.
# De processing, processing.run corre un algoritmo. Sintaxis: processing.run(name_of_the_algorithm, parameters).
print('defining projection for the suitability data')
warp_dict = {
    'DATA_TYPE': 0,
    'EXTRA': '',
    'INPUT': suitin,
    'MULTITHREADING': False,
    'NODATA': None,
    'OPTIONS': '',
    'RESAMPLING': 0,
    'SOURCE_CRS': None,
    'TARGET_CRS': crs_wgs84,
    'TARGET_EXTENT': None,
    'TARGET_EXTENT_CRS': None,
    'TARGET_RESOLUTION': None,
    'OUTPUT': suitout
}
processing.run('gdal:warpreproject', warp_dict)


##################################################################
# Extraer la reproyección
##################################################################
#Extrae el archivo creado previamente (.prj). Utiliza el procedimiento habitual, le avisa lo que va a hacer (extrer el archivo) y lo guarda.
print('extracting the projection for land suitability')
extpr_dict = {
    'INPUT': suitout,
    'PRJ_FILE_CREATE': True
}
processing.run('gdal:extractprojection', extpr_dict)

print('DONE!')
