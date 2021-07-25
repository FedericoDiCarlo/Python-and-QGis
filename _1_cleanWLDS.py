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

#Setting the path where QGis will store temporal data when running the model:

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

# set paths to inputs and outputs
# Cambiar YOUR PATH por el directorio.
mainpath = "YOUR PATH"
# Archivo shape que vamos a usar (input)
wldsin = "{}/langa.shp".format(mainpath)
# Carpeta donde se van a guardar los outputs
outpath = "{}/_output/".format(mainpath)
# Archivo shape que vamos a crear/exportar (output)
wldsout = "{}/wlds_cleaned.shp".format(outpath)

# Si la carpeta de output no existe, la crea.
if not os.path.exists(outpath):
	os.mkdir(outpath)

#########################################################
# Fix geometries
#########################################################
# En consola, "avisa" lo que está haciendo.
print('fixing geometries')
fixgeo_dict = {
    'INPUT': wldsin,
    'OUTPUT': 'memory:'
}
# De processing, processing.run corre un algoritmo. Sintaxis: processing.run(name_of_the_algorithm, parameters).
# En el caso de fixgeometries, los parámetros son un diccionario que se debe haber creado previamente (línea 56).
# Como el output está en la memoria, fix_geo es el diccionario que resulta de aplicar fixgeometries (en vez de guardarlo como otra capa u otra base, lo guarda en la memoria).
fix_geo = processing.run('native:fixgeometries', fixgeo_dict)['OUTPUT']    

#######################################################################
# Add autoincremental field
#######################################################################
# Cuando termina el algoritmo anterior, comienza con el próximo o termina (print('DONE!')). En este caso, comienza con el próximo.
print('adding autoincremental id-field')

# Define un diccionario.
aaicf_dict = {
    'FIELD_NAME': 'GID',
    'GROUP_FIELDS': None,
    'INPUT': fix_geo,
    'SORT_ASCENDING': True,
    'SORT_EXPRESSION': '',
    'SORT_NULLS_FIRST': False,
    'START': 1,
    'OUTPUT': 'memory:'
}
# Al igual que antes, usa el method .run para correr el algoritmo nativo (en QGIS) 'addautoincrementalfield'. También lo guarda en la memoria, en una variable llamada autoinc_id.
# Para este algoritmo necesita como parámetros a:
#	1 nombre que se le pondrá a la variable que autoincrementa (GID),
#	2 que haga el agrupamiento por alguna variable, o no (ejemplo: agrupar por ID cuando hay datos en panel), 
#	3 definir qué base se va a usar,
#	4 si es ascendente,
#	5 que los ordene por alguna variable (vacío aquí),
#	6 que los ordene poniendo primero los missing values,
#	7 el número donde empieza a incrementarse.
#	8 dónde guardar la salida.

autoinc_id = processing.run('native:addautoincrementalfield', aaicf_dict)['OUTPUT'] 

#########################################################
# Field calculator
#########################################################
# Antes que esto, se crea una layer con el nombre length. En field calculator, se crea una variable llamada length que mide la cantidad de caracteres con el nombre del lenguaje 'NAME_PROP'.
# Después, con el algoritmo feature filter, se queda con aquellas que tienen length menor a 11.

# Mismos tres pasos que antes: 1 avisa lo que hace, 2 crea un diccionario con los parámetros que necesita el algoritmo, 3 corre el algoritmo.
print('copying language name into a field with shorter attribute name')
fc_dict = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'lnm',
    'FIELD_PRECISION': 0,
    'FIELD_TYPE': 2,
    'FORMULA': ' attribute($currentfeature, \'NAME_PROP\')',
    'INPUT': autoinc_id,
    'NEW_FIELD': True,
    'OUTPUT': 'memory:'
}
# Parámetros del algortimo:
#	1 Largo del campo a crear.
#	2 Nombre del campo a crear.
#	3 Precisión del campo.
#	4 Tipo: si va a ser string, float, integer o date. 2 indica que es string.
#	5 Fórmula: clona la variable NAME_PROP en una que se llama lnm.
#	6 Toma la última base que estábamos trabajando.
#	7 Crea un campo nuevo.
#	8 Lo guarda en la memoria.

field_calc = processing.run('qgis:fieldcalculator', fc_dict)['OUTPUT']

#########################################################
# Drop field(s)
#########################################################
print('dropping fields except GID, ID, lnm')
# getting all attribute fields

# Crea tres listas con los nombres de las variables.
# Lista de todos los nombres.
allfields = [field.name() for field in field_calc.fields()]
# Lista de los nombres de las variables que se quiere dejar.
keepfields = ['GID', 'ID', 'lnm']
# Lista de los nombres de las variables que se quiere borrar. Es decir, las que están en allfields y no están en keepfields.
dropfields = [field for field in allfields if field not in keepfields]

# Crea un diccionario que tiene como columnas a los dropfields de field_calc y que tendrá un output wldsout.
df3_dict = {
   'COLUMN': dropfields,
   'INPUT': field_calc,
   'OUTPUT': wldsout
}

# Usa el algoritmo deletecolumn para borrar todas las columnas que están en el diccionario y lo guarda en el shape file wldsout.
processing.run('qgis:deletecolumn', df3_dict)

# Terminó de correr el modelo.
print('DONE!')
