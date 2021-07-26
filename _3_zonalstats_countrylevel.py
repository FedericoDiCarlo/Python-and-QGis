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
#Archivos raster de elevation que utilizaremos.
elevation = "D:/backup_school/Research/IPUMS/_GEO/elrug/elevation/alt.bil"
#Archivos de clima y precipitaciones. 
tpbasepath = "D:/backup_school/Research/worldclim/World"
tpath = tpbasepath + "/temperature"
ppath = tpbasepath + "/precipitation"
temp = tpath + "/TOTtmean6090.tif"
prec = ppath + "/TOTprec6090.tif"
#Importamos el .tif que generamos en el model2
landqual = outpath + "/landquality.tif"
#Archivos de población para los diferentes años.
popd1500 = mainpath + "/HYDE/1500ad_pop/popd_1500AD.asc"
popd1990 = mainpath + "/HYDE/1990ad_pop/popd_1990AD.asc"
popd2000 = mainpath + "/HYDE/2000ad_pop/popd_2000AD.asc"
# Shapefile de países que vamos a utilizar.
countries = mainpath + "/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
#Exportar la base como csv.
outcsv = "{}/country_level_zs.csv".format(outpath)
#Definiendo los rasters a utilizar
RASTS = [elevation, temp, prec, landqual, popd1500, popd1990, popd2000]
PREFS = ['elev_', 'temp_', 'prec_', 'lqua_', 'pd15_', 'pd19_', 'pd20_']

#Dado que los rasters son muy pesados, utilizamos los ultimos 4, excluyendo elevation, temperature y precipitation.
RASTS = RASTS[3:]
PREFS = PREFS[3:]

##################################################################
# Fix geometries
##################################################################
# En consola, "avisa" lo que está haciendo.
print('fixing geometries')
fixgeo_dict = {
    'INPUT': countries,
    'OUTPUT': 'memory:'
}
# De processing, processing.run corre el algoritmo para corregir la geografía.
fix_geo = processing.run('native:fixgeometries', fixgeo_dict)['OUTPUT']

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields')
# Lista de todos los nombres.
allfields = [field.name() for field in fix_geo.fields()]
# Lista de los nombres de las variables que se quiere dejar.
keepfields = ['ADMIN', 'ISO_A3']
# Lista de los nombres de las variables que se quiere borrar. Es decir, las que están en allfields y no están en keepfields.
dropfields = [field for field in allfields if field not in keepfields]
# Crea un diccionario que tiene como columnas a los dropfields de fix_geo y que tendrá un output memory.
drop_dict = {
    'COLUMN': dropfields,
    'INPUT': fix_geo,
    'OUTPUT': 'memory:'
}
# Usa el algoritmo deletecolumn para borrar todas las columnas que están en el diccionario.
drop_fields = processing.run('qgis:deletecolumn', drop_dict)['OUTPUT']

# Genera un loop en los rasters. Indexa los raters de 0 a 3, lo usa más tarde. enumerate() en un loop se usa para enumerar objetos https://realpython.com/python-enumerate/
# Este enumerate tiene el problema que solamente guarda 'pd20_' en pref. Probablemente tenga que ver con que se ha ido corriendo el modelo y se han ido desactivando los algoritmos previos. Pareciera que falta un argumento en el loop. Seguro que le falta algo porque está usando solamente idx y no está usando rast.
# Por ejemplo
#for idx, rast in enumerate(RASTS):
#  print(idx,rast)
# Debería dar como resultado
# 0 landqual
# 1 popd1500
# 2 popd1990
# 3 popd2000

for idx, rast in enumerate(RASTS):
	
	pref = PREFS[idx]


###################################################################
# Zonal statistics
###################################################################
#Primero explica lo que va a hacer. Luego crea un diccionario con el raster de calidad de la tierra y con el vector drop_fields creado anteriormente realiza el promedio.
# Acá usa el loop. pref es una variable string con el valor 'pd20_' al que le va a calcular la media con zonalstatistics. Probablemente, se haya querido que pref sea una lista de 4 variables y que le calcule la media a las 4 variables de esa lista
print('computing zonal stats {}'.format(pref))
zs_dict = {
	   'COLUMN_PREFIX': pref,
	   'INPUT_RASTER': rast,
	   'INPUT_VECTOR': drop_fields,
	   'RASTER_BAND': 1,
	   'STATS': [2]
	}
# Usa el algoritmo zonalstatistics para calcular la media del raster de calidad de la tierra.
processing.run('qgis:zonalstatistics', zs_dict)

###################################################################
# write to CSV
###################################################################
#Explica la acción a realizar, exportar la data a csv.
print('outputting the data')
#Guarda los datos de la tabla drop_fields como csv.
with open(outcsv, 'w') as output_file:
    fieldnames = [field.name() for field in drop_fields.fields()]
    line = ','.join(name for name in fieldnames) + '\n'
    output_file.write(line)
    for f in drop_fields.getFeatures():
        line = ','.join(str(f[name]) for name in fieldnames) + '\n'
        output_file.write(line)
	
#Termino de correr el modelo                                        
print('DONE!')
