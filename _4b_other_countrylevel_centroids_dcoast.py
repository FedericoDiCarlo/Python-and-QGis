#########################################################################################
#########################################################################################
######### Preliminary setup to use when not running the model within QGis################

# Hay que importar las librerías si no corrés en QGIS. Importante tener en cuenta para buscar built-in functions o methods.

print('preliminary setup')
import sys
import os
# Importando comandos para correr el shapefile:

from qgis.core import (
    QgsApplication
)

from qgis.analysis import QgsNativeAlgorithms

#Estableciendo el directorio donde se van a guardar los datos temporales cuando se corra el modelo:	
QgsApplication.setPrefixPath('C:/OSGeo4W64/apps/qgis', True)
qgs = QgsApplication([], False)
qgs.initQgis() 
sys.path.append('C:/OSGeo4W64/apps/qgis/python/plugins')

# Estableciendo el processing framework
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#########################################################################################
#########################################################################################

# set paths to inputs and outputs
# Cambiar YOUR PATH por el directorio.
mainpath = "YOUR PATH"
# Carpeta donde se van a guardar los outputs
outpath = "{}/_output/".format(mainpath)
junkpath = "{}/junk".format(outpath)
# Archivos shape que vamos a utilizar
coastin = "{}/ne_10m_coastline/ne_10m_coastline.shp".format(mainpath)
adminin = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)

coastout = "{}/coast.shp".format(junkpath)
centroidsout = "{}/centroids.shp".format(junkpath)
distout = "{}/distance.shp".format(junkpath)
nearout = "{}/nearest.shp".format(junkpath)
testout = "{}/testout.shp".format(junkpath)
csvout = "{}/centroids_closest_coast.csv".format(outpath)

if not os.path.exists(junkpath):
    os.mkdir(junkpath)

# #########################################################################
# #########################################################################
# # 2) centroids and distance to coast
# #########################################################################
# #########################################################################

# #########################################################
# # Fix geometries
# #########################################################
# Para corregir la geografía utiliza el diccionario fix geometries en la costa
print('fixing geometries, coast')
 fg1_dict = {
     'INPUT': coastin,
     'OUTPUT': 'memory:'
 }
# De processing, processing.run corre el algoritmo para corregir la geografía y lo guarda como fixgeo_coast.
 fixgeo_coast = processing.run('native:fixgeometries', fg1_dict)['OUTPUT']

# #########################################################
# # Fix geometries
# #########################################################
 print('fixing geometries, countries')
 fg2_dict = {
     'INPUT': adminin,
     'OUTPUT': 'memory:'
 }
 fixgeo_countries = processing.run('native:fixgeometries', fg2_dict)['OUTPUT']

# #########################################################
# # Centroids
# #########################################################
# Usando fixgeo_countries, busca los centroides de cada país y lo guarda en la memoria. Lo guarda en country_centorids
 print('finding country centroids')
 cts_dict = {
     'ALL_PARTS': False,
     'INPUT': fixgeo_countries,
     'OUTPUT': 'memory:'
 }
 country_centroids = processing.run('native:centroids', cts_dict)['OUTPUT']

# #########################################################
# # Add geometry attributes
# #########################################################    
# Agrega las coordenadas de los centroides como puntos: xcoord, ycoord
print('adding co-ordinates to centroids')    
 aga1_dict = {
     'CALC_METHOD': 0,
     'INPUT': country_centroids,
     'OUTPUT': 'memory:'
 }
 centroids_with_coordinates = processing.run('qgis:exportaddgeometrycolumns', aga1_dict)['OUTPUT']


# ##################################################################
# # Drop field(s)
# ##################################################################
# Elimina algunas columnas de coast usando el mismo procedimiento (define una lista con todas las variables, otra con las que quiere conservar, otra que tiene todas las variables en todas las variables, que no están en las que quiere conservar. Borra esas.)
# Lo gurada en coastout.
 print('dropping unnecessary fields, coast')
 allfields = [field.name() for field in fixgeo_coast.fields()]
 keepfields = ['featurecla']
 dropfields = [field for field in allfields if field not in keepfields]

 df1_dict = {
     'COLUMN': dropfields,
     'INPUT': fixgeo_coast,
     'OUTPUT': coastout
 }
 processing.run('qgis:deletecolumn', df1_dict)

# ##################################################################
# # Drop field(s)
# ##################################################################
# Elimina algunas columnas de countries usando el mismo procedimiento (define una lista con todas las variables, otra con las que quiere conservar, otra que tiene todas las variables en todas las variables, que no están en las que quiere conservar. Borra esas.)
# Lo gurada en centroidsout.
 print('dropping unnecessary fields, countries')
 allfields = [field.name() for field in centroids_with_coordinates.fields()]
 keepfields = ['ne_10m_adm', 'ADMIN', 'ISO_A3', 'xcoord', 'ycoord']
 dropfields = [field for field in allfields if field not in keepfields]

 df2_dict = {
     'COLUMN': dropfields,
     'INPUT': centroids_with_coordinates,
     'OUTPUT': centroidsout
 }
 processing.run('qgis:deletecolumn', df2_dict)

##################################################################
# v.distance
##################################################################
# Calcula la mínima distancia del centroide a un punto de la costa. Saca dos outputs: nearout y distout. En near está el punto más cerca y en dist está el segmento que mide la distancia.
print('vector distance')
vd_dict = {
    'from': centroidsout,
    'from_type': [0],
    'to': coastout,
    'to_type': [1],
    'dmax': -1,
    'dmin': -1,
    'upload': [1],
    'column': ['xcoord'],
    'to_column': None,
    'from_output': nearout,
    'output': distout,
    'GRASS_REGION_PARAMETER': None,
    'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
    'GRASS_MIN_AREA_PARAMETER': 0.0001,
    'GRASS_OUTPUT_TYPE_PARAMETER': 0,
    'GRASS_VECTOR_DSCO': '',
    'GRASS_VECTOR_LCO': '',
    'GRASS_VECTOR_EXPORT_NOCAT': False
}
processing.run('grass7:v.distance', vd_dict)


# #########################################################################################################
# #########################################################################################################
# #########################################################################################################
# #########################################################################################################


# ##################################################################
# # Field calculator
# ##################################################################
# Como el segmento que mide la distancia y el punto que está sobre coast están indexados de manera diferentes, hay que reindexar uno de ellos para poder hacer el merge. En este caso, elige nearout y en FORMULA hace una variable nueva que se llama cat (field type 1, entero) que es igual a cat menos 1. Lo guarda en nearest_cat_adjust
 print('adjusting the "cat" field in the nearest centroids to merge with distance lines')
 fc1_dict = {
     'FIELD_LENGTH': 4,
     'FIELD_NAME': 'cat',
     'FIELD_PRECISION': 3,
     'FIELD_TYPE': 1,
     'FORMULA': 'attribute($currentfeature, \'cat\')-1',
    'INPUT': nearout,
     'NEW_FIELD': False,
     'OUTPUT': 'memory:'
 }
 nearest_cat_adjust = processing.run('qgis:fieldcalculator', fc1_dict)['OUTPUT']
# El resultado de lo anterior es que nearout ahora tiene una variable que se llama cat que tiene el mismo índice que coastout.
# ##################################################################
# # Drop field(s)
# ##################################################################
# Limpiamos nearest_cat_adjust sacando las variables de coordenadas porque no son las que queremos. La guardamos en nearest_cat_adjust_dropfields
 print('dropping unnecessary fields, nearest (the co-ordinates get screwed up')
 df3_dict = {
     'COLUMN': ['xcoord', 'ycoord'],
     'INPUT': nearest_cat_adjust,
     'OUTPUT': 'memory:'
 }
 nearest_cat_adjust_dropfields = processing.run('qgis:deletecolumn', df3_dict)['OUTPUT']

# ##################################################################
# # Join attributes by field value
# ##################################################################
# Hace el merge entre centroids out y nearest_cat_adjust_dropfields y le llama centroids_nearest_coast_joined
 print('merging the two tables: nearest and centroids: correct co-ordiantes')
 jafv1_dict = {
     'DISCARD_NONMATCHING': False,
     'FIELD': 'ne_10m_adm',
    'FIELDS_TO_COPY': None,
     'FIELD_2': 'ne_10m_adm',
     'INPUT': centroidsout,
     'INPUT_2': nearest_cat_adjust_dropfields,
     'METHOD': 1,
     'PREFIX': '',
     'OUTPUT': 'memory:'
 }
 centroids_nearest_coast_joined = processing.run('native:joinattributestable', jafv1_dict)['OUTPUT']

# ##################################################################
# # Drop field(s)
# ##################################################################
# Borro las cosas que están demás. Le llama centroids_nearest_coast_joined_dropfields
 print('dropping unnecessary fields, nearest and centroids merge')
 df4_dict = {
     'COLUMN': ['ne_10m_adm_2', 'ADMIN_2', 'ISO_A3_2'],
     'INPUT': centroids_nearest_coast_joined,
     'OUTPUT': 'memory:'
 }
 centroids_nearest_coast_joined_dropfields = processing.run('qgis:deletecolumn', df4_dict)['OUTPUT']

# ##################################################################
# # Join attributes by field value
# ##################################################################
# Hace el merge entre distout y centroids_nearest_coast_joined_dropfields por la variable cat. En la clase usa ISO_A3. Lo guarda en centroids_nearest_coast_distance_joined
 print('merging the two tables: nearest (adjusted) and distance (this adds countries to each centroid-coast line)')
 jafv2_dict = {
     'DISCARD_NONMATCHING': False,
     'FIELD': 'cat',
     'FIELDS_TO_COPY': None,
     'FIELD_2': 'cat',
     'INPUT': distout,
     'INPUT_2': centroids_nearest_coast_joined_dropfields,
     'METHOD': 1,
     'PREFIX': '',
     'OUTPUT': 'memory:'
 }
 centroids_nearest_coast_distance_joined = processing.run('native:joinattributestable', jafv2_dict)['OUTPUT']

# ##################################################################
# # Extract vertices
# ################################################################## 
# Extract vertices toma una capa vectorial y genera una capa de puntos que representa los vértices de las geometrías. Se toman los vértices de centroids_nearest_coast_distance_joined y se guarda en extract_vertices
 print('extracting vertices (get endpoints of each line)')     
 ev_dict = {
     'INPUT': centroids_nearest_coast_distance_joined,
     'OUTPUT': 'memory:'
 }
 extract_vertices = processing.run('native:extractvertices', ev_dict)['OUTPUT']

# ##################################################################
# # Extract by attribute
# ##################################################################
# Aquí lo que hacemos es quedarnos distancias (distance) que sean mayores (operator 2) que cero (value 0) a partir de los vértices. Lo guarda en extract_by_attribute
 print('keeping only vertices on coast')
 eba_dict = {
     'FIELD': 'distance',
     'INPUT': extract_vertices,
     'OPERATOR': 2,
     'VALUE': '0',
     'OUTPUT': 'memory:'
 }
 extract_by_attribute = processing.run('native:extractbyattribute', eba_dict)['OUTPUT']

# ##################################################################
# # Field calculator
# ##################################################################
# Clonamos ycoord en cent_lat. Se guarda en added_field_cent_lat
 print('creating new field: centroid latitude (keep field names straight)')
 fc2_dict = {
     'FIELD_LENGTH': 10,
     'FIELD_NAME': 'cent_lat',
     'FIELD_PRECISION': 10,
     'FIELD_TYPE': 0,
     'FORMULA': 'attribute($currentfeature, \'ycoord\')',
     'INPUT': extract_by_attribute,
     'NEW_FIELD': False,
     'OUTPUT': 'memory:'
 }
 added_field_cent_lat = processing.run('qgis:fieldcalculator', fc2_dict)['OUTPUT']

 # Ahora clonamos xcoord en cent_lon a partir de added_field_cent_lat. Se guarda en added_field_cent_lon
 print('creating new field: centroid longitude (keep field names straight)')
 fc3_dict = {
     'FIELD_LENGTH': 10,
     'FIELD_NAME': 'cent_lon',
     'FIELD_PRECISION': 10,
     'FIELD_TYPE': 0,
     'FORMULA': 'attribute($currentfeature, \'xcoord\')',
     'INPUT': added_field_cent_lat,
     'NEW_FIELD': False,
     'OUTPUT': 'memory:'
 }
 added_field_cent_lon = processing.run('qgis:fieldcalculator', fc3_dict)['OUTPUT']

# ##################################################################
# # Drop field(s)
# ##################################################################
# Dropeamos con los mismos pasos de siempre (línea 108, por ejemplo). Guardamos en centroids_lat_lon_drop_fields
 print('dropping unnecessary fields')
 allfields = [field.name() for field in added_field_cent_lon.fields()]
 keepfields = ['ne_10m_adm', 'ADMIN', 'ISO_A3', 'cent_lat', 'cent_lon']
 dropfields = [field for field in allfields if field not in keepfields]

 df5_dict = {
     'COLUMN': dropfields,
     'INPUT': added_field_cent_lon,
     'OUTPUT': 'memory:'
 }
 centroids_lat_lon_drop_fields = processing.run('qgis:deletecolumn', df5_dict)['OUTPUT']

# #########################################################
# # Add geometry attributes
# #########################################################    
# Vamos a agregar los atributos de geometría a coast usando la capa centroids_lat_lon_drop_fields (input), con el método de cálculo Layer CRS (calc_method = 0) y lo vamos a guardar en add_geo_coast.
 print('adding co-ordinates to coast points')    
 aga2_dict = {
     'CALC_METHOD': 0,
     'INPUT': centroids_lat_lon_drop_fields,
     'OUTPUT': 'memory:'
 }
 add_geo_coast = processing.run('qgis:exportaddgeometrycolumns', aga2_dict)['OUTPUT']

# El resultada hasta aquí es una tabla que tiene los países, sus códigos y los datos de latitud y longitud de los centroides y las coordenadas (xcoord, ycoord) de los puntos de la costa más cercanos al centroide.

# ##################################################################
# # Field calculator
# ##################################################################
# Clonamos ycoord en coast_lat. Se guarda en added_field_coast_lat 
 print('creating new field: centroid latitude (keep field names straight)')
 fc4_dict = {
     'FIELD_LENGTH': 10,
     'FIELD_NAME': 'coast_lat',
     'FIELD_PRECISION': 10,
     'FIELD_TYPE': 0,
     'FORMULA': 'attribute($currentfeature, \'ycoord\')',
     'INPUT': add_geo_coast,
     'NEW_FIELD': False,
     'OUTPUT': 'memory:'
 }
 added_field_coast_lat = processing.run('qgis:fieldcalculator', fc4_dict)['OUTPUT']

 # Ahora clonamos xcoord en coast_lon a partir de added_field_coast_lat. Se guarda en added_field_coast_lon
 print('creating new field: centroid longitude (keep field names straight)')
 fc5_dict = {
     'FIELD_LENGTH': 10,
     'FIELD_NAME': 'coast_lon',
     'FIELD_PRECISION': 10,
     'FIELD_TYPE': 0,
     'FORMULA': 'attribute($currentfeature, \'xcoord\')',
     'INPUT': added_field_coast_lat,
     'NEW_FIELD': False,
     'OUTPUT': 'memory:'
 }
 added_field_coast_lon = processing.run('qgis:fieldcalculator', fc5_dict)['OUTPUT']

# ##################################################################
# # Drop field(s)
# ##################################################################
# Dropeamos xcoord y ycoord.
 print('dropping unnecessary fields')

 df6_dict = {
     'COLUMN': ['xcoord', 'ycoord'],
     'INPUT': added_field_coast_lon,
     'OUTPUT': csvout
 }
 processing.run('qgis:deletecolumn', df6_dict)

#Termino de correr el modelo
print('DONE!')
