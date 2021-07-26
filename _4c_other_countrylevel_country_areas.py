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
#     QgsCoordinateReferenceSystem
# )

# from qgis.analysis import QgsNativeAlgorithms

# # See https://gis.stackexchange.com/a/155852/4972 for details about the prefix 
# QgsApplication.setPrefixPath('C:/OSGeo4W64/apps/qgis', True)
# qgs = QgsApplication([], False)
# qgs.initQgis()

# sys.path.append('C:/OSGeo4W64/apps/qgis/python/plugins')

#Setting the path where QGis will store temporal data when running the model:
# import processing
# from processing.core.Processing import Processing
# Processing.initialize()
# QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#########################################################################################
#########################################################################################

# set paths to inputs and outputs
# Cambiar YOUR PATH por el directorio.
mainpath = "YOUR PATH"
#Archivo shape que vamos a utilizar
admin_in = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)

areas_out = "{}/_output/country_areas.csv".format(mainpath)

# defining world cylindrical equal area SR
crs_wcea = QgsCoordinateReferenceSystem('ESRI:54034')

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields')
worldlyr = QgsVectorLayer(admin_in, 'ogr')
# Lista de todos los nombres.
allfields = [field.name() for field in worldlyr.fields()]
# Lista de los nombres de las variables que se quiere dejar.
keepfields = ['ne_10m_adm', 'ADMIN', 'ISO_A3']
# Lista de los nombres de las variables que se quiere borrar. Es decir, las que están en allfields y no están en keepfields.
dropfields = [field for field in allfields if field not in keepfields]
# Crea un diccionario que tiene como columnas a los dropfields de fix_geo y que tendrá un output memory.
drop_dict = {
    'COLUMN': dropfields,
    'INPUT': admin_in,
    'OUTPUT': 'memory:'
}
# Usa el algoritmo deletecolumn para borrar todas las columnas que están en el diccionario.
countries_drop_fields = processing.run('qgis:deletecolumn', drop_dict)['OUTPUT']

##################################################################
# Reproject layer
##################################################################
#Aqui lo que hacen es reproyectar los datos de countries. Esto lo hacen a traves del diccionario reproject layer para que se transforme en cilindrico.  
print('projecting to world cylindical equal area')
reproj_dict = {
    'INPUT': countries_drop_fields,
    'TARGET_CRS': crs_wcea,
    'OUTPUT': 'memory:'
}
# Usa el algoritmo reproject layer para reproyectar countries y lo guarda como countries_reprojected
countries_reprojected = processing.run('native:reprojectlayer', reproj_dict)['OUTPUT']

##################################################################
# Fix geometries
##################################################################
# Para corregir la geometria utiliza el diccionario fix geometries
print('fixing geometries')
fixgeo_dict = {
    'INPUT': countries_reprojected,
    'OUTPUT': 'memory:'
}
# De processing, processing.run corre el algoritmo para corregir la geometria y lo guarda como countries_fix_geo.
countries_fix_geo = processing.run('native:fixgeometries', fixgeo_dict)['OUTPUT']

##################################################################
# Field calculator, output to csv
##################################################################
#Aqui lo que hacen es calcular los kilometros cuadrados de area de los paises. Esto lo hacen mediante field calculator. Divide el area del poligono por 1000000.
print('calculating country areas')
fcalc_dict = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'km2area',
    'FIELD_PRECISION': 3,
    'FIELD_TYPE': 0,
    'FORMULA': 'area($geometry)/1000000',
    'INPUT': countries_fix_geo,
    'NEW_FIELD': True,
    'OUTPUT': areas_out
}
#Corre el algoritmo fieldcalculator para calcular las areas y lo guarda como areas_out
processing.run('qgis:fieldcalculator', fcalc_dict)
#Termina de correr el modelo
print('DONE!')


