#########################################################################################
#########################################################################################
######### Preliminary setup to use when not running the model within QGis################
# Hay que importar las librerías si no corrés en QGIS. Importante tener en cuenta para buscar built-in functions o methods.

# print('preliminary setup')
# import sys
# import os

# Importando comandos para correr el shapefile:
# from qgis.core import (
#     QgsApplication
# )

# from qgis.analysis import QgsNativeAlgorithms

#Estableciendo el directorio donde se van a guardar los datos temporales cuando se corra el modelo:	
# QgsApplication.setPrefixPath('C:/OSGeo4W64/apps/qgis', True)
# qgs = QgsApplication([], False)
# qgs.initQgis()  
# sys.path.append('C:/OSGeo4W64/apps/qgis/python/plugins')

# Estableciendo el processing framework
# import processing
# from processing.core.Processing import Processing
# Processing.initialize()
# QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#########################################################################################
#########################################################################################

# set paths to inputs and outputs
# Cambiar YOUR PATH por el directorio.
mainpath = "YOUR PATH"
# Carpeta donde se van a guardar los outputs
outpath = "{}/_output/".format(mainpath)
# Archivo shape que vamos a utilizar
greg = "{}/greg_cleaned.shp".format(outpath)
# Archivo shape que vamos a utilizar
wlds = "{}/wlds_cleaned.shp".format(outpath)
# Archivo shape que vamos a utilizar
admin = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)
#Exportar la base como csv.
outcsv = "{}/nlangs_country.csv".format(outpath)

#########################################################################
#########################################################################
# 1) number of languages per country
#########################################################################
#########################################################################

#########################################################
# Fix geometries
#########################################################
# Para corregir la geografía utiliza el diccionario fix geometries en los lenguajes
print('fixing geometries, languages')
fg1_dict = {
    'INPUT': wlds,
    'OUTPUT': 'memory:'
}
# De processing, processing.run corre el algoritmo para corregir la geografía y lo guarda como fixgeo_wlds.
fixgeo_wlds = processing.run('native:fixgeometries', fg1_dict)['OUTPUT']

#########################################################
# Fix geometries
#########################################################
# Para corregir la geografía utiliza el diccionario fix geometries en los países.
print('fixing geometries, countries')
fg2_dict = {
    'INPUT': admin,
    'OUTPUT': 'memory:'
}
# De processing, processing.run corre el algoritmo para corregir la geografía y lo guarda como fixgeo_countries.
fixgeo_countries = processing.run('native:fixgeometries', fg2_dict)['OUTPUT']

#########################################################
# Intersection
#########################################################
#Aqui lo que hace es combinar las bases de datos eligiendo las variables GID y ADMIN de wlds y countries respectivamente. Utiliza el diccionario intersection superponiendo countries en wlds.
print('intersecting')
int_dict = {
    'INPUT': fixgeo_wlds,
    'INPUT_FIELDS': 'GID',
    'OVERLAY': fixgeo_countries,
    'OVERLAY_FIELDS': 'ADMIN',
    'OUTPUT': 'memory:'
}
# Usa el algoritmo intersection para combinar las bases y lo guarda como intersection.
intersection = processing.run('native:intersection', int_dict)['OUTPUT']

#########################################################
# Statistics by categories
#########################################################
#Aqui lo que se hace es ver para cada país cuantos idiomas hay. Para esto se utiliza el diccionario statistics by categories donde se utiliza la intersección generada previamente y se categoriza por ADMIN, es decir, país.
print('statistics by categories')        
sbc_dict = {
    'CATEGORIES_FIELD_NAME': 'ADMIN',
    'INPUT': intersection,
    'VALUES_FIELD_NAME': None,
    'OUTPUT': outcsv
}
# Usa el algoritmo statistics by categories para agrupar por país y lo guarda como outcsv layer.
processing.run('qgis:statisticsbycategories', sbc_dict)
#Termina de correr el modelo
print('DONE!')
