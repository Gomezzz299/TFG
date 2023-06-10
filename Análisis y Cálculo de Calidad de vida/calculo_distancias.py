#!/usr/bin/env python
# coding: utf-8

# importar librerías necesarias
import os
import pandas as pd
import geopandas as gpd
import requests
import urllib.parse
import warnings
warnings.simplefilter("ignore")
import time
import random

##### 1. Carga de datos

# establecer directorio de trabajo
os.chdir("C:/Users/aleja/OneDrive - Universidad Politécnica de Madrid/Universidad/Asignaturas/Cuarto/Trabajo de Fin de Grado/")

# cargar datos necesarios
accesos_euc = pd.read_csv("Resultados/accesos_distancia_euc.csv")
accesos = gpd.read_file("Capas/ACCESOS.geojson")
pescaderias = pd.read_csv('Datos/pescaderias.csv')
supermercados = pd.read_csv('Datos/supermercados.csv')
fruterias = pd.read_csv('Datos/fruterias.csv')
alimentacion = pd.read_csv('Datos/alimentacion.csv')
panaderias = pd.read_csv('Datos/panaderias.csv')
carnicerias = pd.read_csv('Datos/carnicerias.csv')
alimentacion_no_especializada = pd.read_csv('Datos/alimentacion_no_especializada.csv')
peluquerias = pd.read_csv('Datos/peluquerias.csv')
areas_descanso = pd.read_csv('Datos/areas_descanso.csv')
mercado_municipal = pd.read_csv('Datos/mercado_municipal.csv')
mercado_ambulante = pd.read_csv('Datos/mercado_ambulante.csv')
electricistas_fontaneros = pd.read_csv('Datos/electricistas_fontaneros.csv')
ferreterias = pd.read_csv('Datos/ferreterias.csv')
electrodomesticos = pd.read_csv('Datos/electrodomesticos.csv')
muebles = pd.read_csv('Datos/muebles.csv')
tiendas_ropa = pd.read_csv('Datos/tiendas_ropa.csv')
floristerias = pd.read_csv('Datos/floristerias.csv')
zapaterias = pd.read_csv('Datos/zapaterias.csv')
lavanderias = pd.read_csv('Datos/lavanderias.csv')
mecanicos = pd.read_csv('Datos/mecanicos.csv')
herboristerias = pd.read_csv('Datos/herboristerias.csv')
tiendas_deportivas = pd.read_csv('Datos/tiendas_deportivas.csv')
lugares_interes = pd.read_csv('Datos/lugares_interes.csv')
bares = pd.read_csv('Datos/bares.csv')
restaurantes = pd.read_csv('Datos/restaurantes.csv')
actividades_recreativas = pd.read_csv('Datos/actividades_recreativas.csv')
parques = pd.read_csv('Datos/parques.csv')
espacios_culturales = pd.read_csv('Datos/espacios_culturales.csv')
exposiciones = pd.read_csv('Datos/exposiciones.csv')
bibliotecas = pd.read_csv('Datos/bibliotecas.csv')
colegios = pd.read_csv('Datos/colegios.csv')
guarderias = pd.read_csv('Datos/guarderias.csv')
institutos = pd.read_csv('Datos/institutos.csv')
otros_centros = pd.read_csv('Datos/otros_centros.csv')
farmacias = pd.read_csv('Datos/farmacias.csv')
residencias = pd.read_csv('Datos/residencias.csv')
cap = pd.read_csv('Datos/cap.csv')
cruz_roja = pd.read_csv('Datos/cruz_roja.csv')
deporte = pd.read_csv('Datos/deporte.csv')
autobus = pd.read_csv('Datos/autobus.csv')
taxi = pd.read_csv('Datos/taxi.csv')
transporte_demanda = pd.read_csv('Datos/transporte_demanda.csv')
correos = pd.read_csv('Datos/correos.csv')
notaria = pd.read_csv('Datos/notaria.csv')
ayuntamiento = pd.read_csv('Datos/ayuntamiento.csv')

##### 2. Limpieza de datos
# accesos
accesos["latitud"] = accesos["geometry"].y
accesos["longitud"] = accesos["geometry"].x
accesos = accesos.drop(columns=['id', 'num_acceso', 'refcat'])

##### 3. Definir funciones

# función para cálculo de distancia manhattan
def distancia_habitante(lat_acceso, lon_acceso, lat_poi, lon_poi):
    url = 'https://www.cartociudad.es/services/api/route?orig={latitud_acceso},{longitud_acceso}&dest={latitud_poi},{longitud_poi}&locale=es&vehicle=CAR'.format(latitud_acceso=lat_acceso, longitud_acceso=lon_acceso, latitud_poi=lat_poi, longitud_poi=lon_poi)
#    url = 'https://graphhopper.com/api/1/route?point={latitud_acceso},{longitud_acceso}&point={latitud_poi},{longitud_poi}&points_encoded=false&vehicle=foot&locale=en&key=f35221ff-5859-42dc-8420-ab65e47ef722'.format(latitud_acceso=lat_acceso, longitud_acceso=lon_acceso, latitud_poi=lat_poi, longitud_poi=lon_poi)
    try:
        response = requests.get(url).json()

        encuentra = response['found']
        if encuentra == 'true':
            dist = float(response['distance'])
        else:
            dist = -1.0
#        dist = response['paths'][0]['distance']
    except:
        dist = -1.0
    #print(response['paths'][0]['distance'])
    return dist

# función que guarda la distancia mínima
def distancia_minima(distancia1, distancia2):
    if distancia1 < distancia2:
        distancia_min = distancia1
    else:
        distancia_min = distancia2
    return distancia_min
    
localizaciones = [supermercados, pescaderias, alimentacion, panaderias, carnicerias, alimentacion_no_especializada, 
                  peluquerias, mercado_municipal, mercado_ambulante, electricistas_fontaneros, ferreterias, 
                  electrodomesticos, muebles, tiendas_ropa, floristerias, lugares_interes, bares, restaurantes, 
                  areas_descanso, parques, espacios_culturales, exposiciones, bibliotecas, colegios, guarderias, institutos,
                  otros_centros, farmacias, residencias, cap, cruz_roja, deporte, autobus, taxi, transporte_demanda, 
                  correos, notaria, ayuntamiento]

for i in range(0, len(localizaciones)):
    accesos[str(i)] = 0

##### 4. Comienzo del proceso
print("Empieza el procesamiento:")

# para almacenar el tiempo en el que comienza
start_t = time.time()

# contador de accesos
j = 0
total_accesos = len(accesos.index)

for acceso in accesos.index:
    for tipo_comercio in range(0, len(localizaciones)):

        # se establece una distancia inicial muy alta para que esta sea superada con el primer punto
        dist_minima = 10000.0
        for comercio in localizaciones[tipo_comercio].index:
            if accesos_euc[str(tipo_comercio)][acceso] < 1500: 
                dist = distancia_habitante(accesos.latitud[acceso], 
                                           accesos.longitud[acceso], localizaciones[tipo_comercio].latitud[comercio], 
                                           localizaciones[tipo_comercio].longitud[comercio])
                if dist > 0 :
                    dist_minima = distancia_minima(dist_minima, dist)
                accesos[str(tipo_comercio)][acceso] = dist_minima

                # se añade una espera para no saturar el servidor
                time.sleep(random.uniform(0.1, 0.3)) # espera en segundos
            
    j += 1

    # para saber por qué acceso va el cálculo
    print("Acceso nº:", j , "Total:",  j/total_accesos * 100 , "%, Tiempo transcurrido:", (time.time() - start_t) / 60 , "minutos")   
    
    # guardar calculo cada iteracion
    accesos.to_csv("Resultados/accesos_distancia_parcial.csv")
        
# guardar calculo completo
accesos.to_csv("Resultados/accesos_distancia_completo.csv")
