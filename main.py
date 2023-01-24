# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
import pyodbc
import requests
import xml.etree.ElementTree as et
from datetime import date, datetime, timedelta

import modules.requests_content
import modules.requests_content_zubex
import modules.requests_content_Fandeli_QRO
import modules.requests_content_Fandeli_VDM
import modules.requests_content_Artigraf
import modules.requests_content_Karisma


def create_SQL_connection(server='tcp:beetmann-energy.database.windows.net', bd='mercados', user='adm', password='MercadosBD20'):
    """Establish connection to the SQL database."""
    
    try:
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+bd+';UID='+user+';PWD='+password)
        return cnxn
    except:
        print('Error en la conexión con la base de datos. Contacte al equipo de soporte técnico.')
        exit(1)


def main():

    initial_date = date.fromisoformat(input('\nIngrese fecha inicial (aaaa/mm/dd): '))
    final_date = date.fromisoformat(input('Ingrese fecha final (aaaa/mm/dd): '))
    print()
    current_date = initial_date
    data = []
    cnxn = create_SQL_connection()

    with cnxn:

        while current_date <= final_date:
            query = """
                    SELECT * 
                    FROM [dbo].[ODC Beetmann] 
                    WHERE [Fecha de la oferta de compra] = '{date}' and Cliente = 'Urrea'
                    """.format(date=current_date)
            existing_ODC = pd.read_sql(query, cnxn)
            
            if not existing_ODC.empty:
                print("Información existente")

            else:
                date_1, date_2 = current_date - timedelta(days=7), current_date - timedelta(days=14)
                date_3, date_4 = current_date - timedelta(days=21), current_date - timedelta(days=28)

                consulta_sql = """
                                SELECT table_1.Hora, AVG(table_1.Valor) AS Valor FROM 
                                    (SELECT 
                                        Convert(DATE, (([Fecha]+[Hora])-(.003472222))) AS 'Fecha', 
                                        ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1) AS 'Hora', 
                                        ROUND(((sum([Kwhe]))/1000),4)* 1.124859392575928 AS 'Valor' 
                                    FROM [dbo].[Cincominutal URREA] 
                                    WHERE Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_1}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_2}'
                                        OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_3}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_4}'
                                    GROUP BY  Convert(DATE, (([Fecha]+[Hora])-(.003472222))), ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1)
                                    ) 
                                    AS table_1 
                                    GROUP BY table_1.Hora
                                """.format(d_1=date_1, d_2=date_2, d_3=date_3, d_4=date_4)
                df = pd.DataFrame(pd.read_sql(consulta_sql, cnxn))
                
                if df.empty:
                    print("No se encontró información para esta fecha")

                else:
                    print("Se encontró información para esta fecha")
                    values_sum = sum(df['Valor'])

                    url = 'https://ws01.cenace.gob.mx:8082/mxswmem/EnviarOfertaCompraEnergiaService.asmx?wsdl'
                    headers = {'content-type': 'text/xml'}
                    body = modules.requests_content.body

                    ODC_date = datetime.strftime(current_date, '%d/%m/%Y')
                    hours = {
                            '1': df['Valor'][0], '2': df['Valor'][1], '3': df['Valor'][2], '4': df['Valor'][3], 
                            '5': df['Valor'][4], '6': df['Valor'][5], '7': df['Valor'][6], '8': df['Valor'][7], 
                            '9': df['Valor'][8], '10': df['Valor'][9], '11': df['Valor'][10], '12': df['Valor'][11], 
                            '13': df['Valor'][12], '14': df['Valor'][13], '15': df['Valor'][14], '16': df['Valor'][15], 
                            '17': df['Valor'][16], '18': df['Valor'][17], '19': df['Valor'][18], '20': df['Valor'][19], 
                            '21': df['Valor'][20], '22': df['Valor'][21], '23': df['Valor'][22], '24': df['Valor'][23]
                            }
                    
                    body = body %(ODC_date, ODC_date, hours['1'], hours['2'], hours['3'], 
                                  hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], 
                                  hours['9'], hours['10'], hours['11'], hours['12'], hours['13'], 
                                  hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], 
                                  hours['19'], hours['20'], hours['21'], hours['22'], hours['23'], 
                                  hours['24'])
                    
                    response = requests.post(url, data=body, headers=headers)
                    info = et.fromstring(response.content)[0][0][0]
                    jdata = json.loads(info.text)
                    resultados = jdata['resultado'][0]
                    code = resultados['codigo']
                    
                    if code != '2000':
                        print('No se pudo enviar la oferta de compra para la fecha', current_date, ':(')
                        exit()

                    else:
                        
                        now = datetime.now() - timedelta(.208333)
                        urrea = "Urrea"
                        Metodos = 'Promedio'
                        TOTAL = values_sum
                        fechas = date_1.strftime('%Y-%m-%d') + ',' + date_2.strftime('%Y-%m-%d') + ',' + date_3.strftime('%Y-%m-%d') + ',' + date_4.strftime('%Y-%m-%d')
                        dias = '0'

                        cursor = cnxn.cursor()

                        cursor.execute("""
                                        INSERT INTO [dbo].[ODC Beetmann]  
                                            ([Fecha de envio], [Fecha de la oferta de compra], [Cliente], [Metodo ], [Parametros usados (dias utlizados , dia mas parecido buscado)], 
                                            [Dias antes / despues al dia mas parecido], [Hora 1], [Hora 2], [Hora 3], [Hora 4], [Hora 5], [Hora 6], 
                                            [Hora 7], [Hora 8], [Hora 9], [Hora 10], [Hora 11], [Hora 12], [Hora 13], [Hora 14], [Hora 15], [Hora 16], 
                                            [Hora 17], [Hora 18], [Hora 19], [Hora 20], [Hora 21], [Hora 22], [Hora 23], [Hora 24], [TOTAL]) 
                                        values(?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        """, 
                                        now , datetime.strptime(ODC_date, '%d/%m/%Y'), urrea, Metodos, fechas, dias, hours['1'], hours['2'], 
                                        hours['3'], hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], hours['9'], hours['10'], hours['11'], 
                                        hours['12'], hours['13'], hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], hours['19'], 
                                        hours['20'], hours['21'], hours['22'], hours['23'], hours['24'], TOTAL)
                        
                        cnxn.commit()
                        print('Oferta de compra enviada y base de datos actualizada')

            current_date += timedelta(days=1)

def main_zubex():

    initial_date = date.fromisoformat(input('\nIngrese fecha inicial (aaaa/mm/dd): '))
    final_date = date.fromisoformat(input('Ingrese fecha final (aaaa/mm/dd): '))
    print()
    current_date = initial_date
    data = []
    cnxn = create_SQL_connection()

    with cnxn:

        while current_date <= final_date:
            query = """
                    SELECT * 
                    FROM [dbo].[ODC Beetmann] 
                    WHERE [Fecha de la oferta de compra] = '{date}' and Cliente = 'Zubex'
                    """.format(date=current_date)
            existing_ODC = pd.read_sql(query, cnxn)
            
            if not existing_ODC.empty:
                print("Información existente")

            else:
        

                date_1, date_2 = current_date - timedelta(days=7), current_date - timedelta(days=14)
                date_3, date_4 = current_date - timedelta(days=21), current_date - timedelta(days=28)

                consulta_sql = """
                                SELECT table_1.Hora, AVG(table_1.Valor) AS Valor FROM 
                                    (SELECT 
                                        Convert(DATE, (([Fecha]+[Hora])-(.003472222))) AS 'Fecha', 
                                        ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1) AS 'Hora', 
                                        (ROUND(((sum([Kwhe]))/1000),4)*1.0989010989010989)  AS 'Valor' 
                                    FROM [dbo].[Cincominutal Zubex] 
                                    WHERE Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_1}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_2}'
                                        OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_3}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_4}'
                                    GROUP BY  Convert(DATE, (([Fecha]+[Hora])-(.003472222))), ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1)
                                    ) 
                                    AS table_1 
                                    GROUP BY table_1.Hora
                                """.format(d_1=date_1, d_2=date_2, d_3=date_3, d_4=date_4)
                df = pd.DataFrame(pd.read_sql(consulta_sql, cnxn))
                
                if df.empty:
                    print("No se encontró información para esta fecha")

                else:
                    print("Se encontró información para esta fecha")
                    values_sum = sum(df['Valor'])

                    url = 'https://ws01.cenace.gob.mx:8082/mxswmem/EnviarOfertaCompraEnergiaService.asmx?wsdl'
                    headers = {'content-type': 'text/xml'}
                    body = modules.requests_content_zubex.body

                    ODC_date = datetime.strftime(current_date, '%d/%m/%Y')
                    hours = {
                            '1': df['Valor'][0], '2': df['Valor'][1], '3': df['Valor'][2], '4': df['Valor'][3], 
                            '5': df['Valor'][4], '6': df['Valor'][5], '7': df['Valor'][6], '8': df['Valor'][7], 
                            '9': df['Valor'][8], '10': df['Valor'][9], '11': df['Valor'][10], '12': df['Valor'][11], 
                            '13': df['Valor'][12], '14': df['Valor'][13], '15': df['Valor'][14], '16': df['Valor'][15], 
                            '17': df['Valor'][16], '18': df['Valor'][17], '19': df['Valor'][18], '20': df['Valor'][19], 
                            '21': df['Valor'][20], '22': df['Valor'][21], '23': df['Valor'][22], '24': df['Valor'][23]
                            }
                    
                    body = body %(ODC_date, ODC_date, hours['1'], hours['2'], hours['3'], 
                                  hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], 
                                  hours['9'], hours['10'], hours['11'], hours['12'], hours['13'], 
                                  hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], 
                                  hours['19'], hours['20'], hours['21'], hours['22'], hours['23'], 
                                  hours['24'])
                    
                    response = requests.post(url, data=body, headers=headers)
                    info = et.fromstring(response.content)[0][0][0]
                    jdata = json.loads(info.text)
                    resultados = jdata['resultado'][0]
                    code = resultados['codigo']
                    
                    if code != '2000':
                        print('No se pudo enviar la oferta de compra para la fecha', current_date, ':(')
                        exit()

                    else:
                        
                        now = datetime.now() - timedelta(.208333)
                        cliente = "Zubex"
                        Metodos = 'Promedio'
                        TOTAL = values_sum
                        fechas = date_1.strftime('%Y-%m-%d') + ',' + date_2.strftime('%Y-%m-%d') + ',' + date_3.strftime('%Y-%m-%d') + ',' + date_4.strftime('%Y-%m-%d')
                        dias = '0'

                        cursor = cnxn.cursor()

                        cursor.execute("""
                                        INSERT INTO [dbo].[ODC Beetmann]  
                                            ([Fecha de envio], [Fecha de la oferta de compra], [Cliente], [Metodo ], [Parametros usados (dias utlizados , dia mas parecido buscado)], 
                                            [Dias antes / despues al dia mas parecido], [Hora 1], [Hora 2], [Hora 3], [Hora 4], [Hora 5], [Hora 6], 
                                            [Hora 7], [Hora 8], [Hora 9], [Hora 10], [Hora 11], [Hora 12], [Hora 13], [Hora 14], [Hora 15], [Hora 16], 
                                            [Hora 17], [Hora 18], [Hora 19], [Hora 20], [Hora 21], [Hora 22], [Hora 23], [Hora 24], [TOTAL]) 
                                        values(?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        """, 
                                        now , datetime.strptime(ODC_date, '%d/%m/%Y'), cliente, Metodos, fechas, dias, hours['1'], hours['2'], 
                                        hours['3'], hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], hours['9'], hours['10'], hours['11'], 
                                        hours['12'], hours['13'], hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], hours['19'], 
                                        hours['20'], hours['21'], hours['22'], hours['23'], hours['24'], TOTAL)
                        
                        cnxn.commit()
                        print('Oferta de compra enviada y base de datos actualizada')

            current_date += timedelta(days=1)

def main_Fandeli_QRO():

    initial_date = date.fromisoformat(input('\nIngrese fecha inicial (aaaa/mm/dd): '))
    final_date = date.fromisoformat(input('Ingrese fecha final (aaaa/mm/dd): '))
    print()
    current_date = initial_date
    data = []
    cnxn = create_SQL_connection()

    with cnxn:

        while current_date <= final_date:
            query = """
                    SELECT * 
                    FROM [dbo].[ODC Beetmann] 
                    WHERE [Fecha de la oferta de compra] = '{date}' and Cliente = 'Fandeli QRO'
                    """.format(date=current_date)
            existing_ODC = pd.read_sql(query, cnxn)
            
            if not existing_ODC.empty:
                print("Información existente")

            else:
                date_1, date_2 = current_date - timedelta(days=7), current_date - timedelta(days=14)
                date_3, date_4 = current_date - timedelta(days=21), current_date - timedelta(days=28)

                consulta_sql = """
SELECT table_1.Hora, AVG(table_1.Valor) AS Valor FROM 
(SELECT 
Convert(DATE, (([Fecha]+[Hora])-(.003472222))) AS 'Fecha', 
((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1) AS 'Hora', 
(ROUND(((sum([Kwhe]))/1000),4)*1.131221719457014 )  AS 'Valor' 
FROM [dbo].[Cincominutal Fandeli] 
WHERE (Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_1}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_2}'
OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_3}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_4}') and
(equipo = 'FAB_NACIONAL_DE_LIJA_QRO_812_P')
GROUP BY  Convert(DATE, (([Fecha]+[Hora])-(.003472222))), ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1)
) 
AS table_1 
GROUP BY table_1.Hora
                                """.format(d_1=date_1, d_2=date_2, d_3=date_3, d_4=date_4)
                df = pd.DataFrame(pd.read_sql(consulta_sql, cnxn))
                
                if df.empty:
                    print("No se encontró información para esta fecha")

                else:
                    print("Se encontró información para esta fecha")
                    values_sum = sum(df['Valor'])

                    url = 'https://ws01.cenace.gob.mx:8082/mxswmem/EnviarOfertaCompraEnergiaService.asmx?wsdl'
                    headers = {'content-type': 'text/xml'}
                    body = modules.requests_content_Fandeli_QRO.body

                    ODC_date = datetime.strftime(current_date, '%d/%m/%Y')
                    hours = {
                            '1': df['Valor'][0], '2': df['Valor'][1], '3': df['Valor'][2], '4': df['Valor'][3], 
                            '5': df['Valor'][4], '6': df['Valor'][5], '7': df['Valor'][6], '8': df['Valor'][7], 
                            '9': df['Valor'][8], '10': df['Valor'][9], '11': df['Valor'][10], '12': df['Valor'][11], 
                            '13': df['Valor'][12], '14': df['Valor'][13], '15': df['Valor'][14], '16': df['Valor'][15], 
                            '17': df['Valor'][16], '18': df['Valor'][17], '19': df['Valor'][18], '20': df['Valor'][19], 
                            '21': df['Valor'][20], '22': df['Valor'][21], '23': df['Valor'][22], '24': df['Valor'][23]
                            }
                    
                    body = body %(ODC_date, ODC_date, hours['1'], hours['2'], hours['3'], 
                                  hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], 
                                  hours['9'], hours['10'], hours['11'], hours['12'], hours['13'], 
                                  hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], 
                                  hours['19'], hours['20'], hours['21'], hours['22'], hours['23'], 
                                  hours['24'])
                    
                    response = requests.post(url, data=body, headers=headers)
                    info = et.fromstring(response.content)[0][0][0]
                    jdata = json.loads(info.text)
                    resultados = jdata['resultado'][0]
                    code = resultados['codigo']
                    
                    if code != '2000':
                        print('No se pudo enviar la oferta de compra para la fecha', current_date, ':(')
                        exit()

                    else:
                        
                        now = datetime.now() - timedelta(.208333)
                        cliente = "Fandeli QRO"
                        Metodos = 'Promedio'
                        TOTAL = values_sum
                        fechas = date_1.strftime('%Y-%m-%d') + ',' + date_2.strftime('%Y-%m-%d') + ',' + date_3.strftime('%Y-%m-%d') + ',' + date_4.strftime('%Y-%m-%d')
                        dias = '0'

                        cursor = cnxn.cursor()

                        cursor.execute("""
                                        INSERT INTO [dbo].[ODC Beetmann]  
                                            ([Fecha de envio], [Fecha de la oferta de compra], [Cliente], [Metodo ], [Parametros usados (dias utlizados , dia mas parecido buscado)], 
                                            [Dias antes / despues al dia mas parecido], [Hora 1], [Hora 2], [Hora 3], [Hora 4], [Hora 5], [Hora 6], 
                                            [Hora 7], [Hora 8], [Hora 9], [Hora 10], [Hora 11], [Hora 12], [Hora 13], [Hora 14], [Hora 15], [Hora 16], 
                                            [Hora 17], [Hora 18], [Hora 19], [Hora 20], [Hora 21], [Hora 22], [Hora 23], [Hora 24], [TOTAL]) 
                                        values(?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        """, 
                                        now , datetime.strptime(ODC_date, '%d/%m/%Y'), cliente, Metodos, fechas, dias, hours['1'], hours['2'], 
                                        hours['3'], hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], hours['9'], hours['10'], hours['11'], 
                                        hours['12'], hours['13'], hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], hours['19'], 
                                        hours['20'], hours['21'], hours['22'], hours['23'], hours['24'], TOTAL)
                        
                        cnxn.commit()
                        print('Oferta de compra enviada y base de datos actualizada')

            current_date += timedelta(days=1)

def main_Fandeli_VDM():

    initial_date = date.fromisoformat(input('\nIngrese fecha inicial (aaaa/mm/dd): '))
    final_date = date.fromisoformat(input('Ingrese fecha final (aaaa/mm/dd): '))
    print()
    current_date = initial_date
    data = []
    cnxn = create_SQL_connection()

    with cnxn:

        while current_date <= final_date:
            query = """
                    SELECT * 
                    FROM [dbo].[ODC Beetmann] 
                    WHERE [Fecha de la oferta de compra] = '{date}' and Cliente = 'Fandeli VDM'
                    """.format(date=current_date)
            existing_ODC = pd.read_sql(query, cnxn)
            
            if not existing_ODC.empty:
                print("Información existente")

            else:

                date_1, date_2 = current_date - timedelta(days=7), current_date - timedelta(days=14)
                date_3, date_4 = current_date - timedelta(days=21), current_date - timedelta(days=28)

                consulta_sql = """
SELECT table_1.Hora, AVG(table_1.Valor) AS Valor FROM 
(SELECT 
Convert(DATE, (([Fecha]+[Hora])-(.003472222))) AS 'Fecha', 
((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1) AS 'Hora', 
(ROUND(((sum([Kwhe]))/1000),4)*1.222493887530562)  AS 'Valor' 
FROM [dbo].[Cincominutal Fandeli] 
WHERE (Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_1}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_2}'
OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_3}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_4}') and
(equipo = '569931001461' or equipo = '569931201291')
GROUP BY  Convert(DATE, (([Fecha]+[Hora])-(.003472222))), ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1)
) 
AS table_1 
GROUP BY table_1.Hora
                                """.format(d_1=date_1, d_2=date_2, d_3=date_3, d_4=date_4)
                df = pd.DataFrame(pd.read_sql(consulta_sql, cnxn))
                
                if df.empty:
                    print("No se encontró información para esta fecha")

                else:
                    print("Se encontró información para esta fecha")
                    values_sum = sum(df['Valor'])

                    url = 'https://ws01.cenace.gob.mx:8082/mxswmem/EnviarOfertaCompraEnergiaService.asmx?wsdl'
                    headers = {'content-type': 'text/xml'}
                    body = modules.requests_content_Fandeli_VDM.body

                    ODC_date = datetime.strftime(current_date, '%d/%m/%Y')
                    hours = {
                            '1': df['Valor'][0], '2': df['Valor'][1], '3': df['Valor'][2], '4': df['Valor'][3], 
                            '5': df['Valor'][4], '6': df['Valor'][5], '7': df['Valor'][6], '8': df['Valor'][7], 
                            '9': df['Valor'][8], '10': df['Valor'][9], '11': df['Valor'][10], '12': df['Valor'][11], 
                            '13': df['Valor'][12], '14': df['Valor'][13], '15': df['Valor'][14], '16': df['Valor'][15], 
                            '17': df['Valor'][16], '18': df['Valor'][17], '19': df['Valor'][18], '20': df['Valor'][19], 
                            '21': df['Valor'][20], '22': df['Valor'][21], '23': df['Valor'][22], '24': df['Valor'][23]
                            }
                    
                    body = body %(ODC_date, ODC_date, hours['1'], hours['2'], hours['3'], 
                                  hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], 
                                  hours['9'], hours['10'], hours['11'], hours['12'], hours['13'], 
                                  hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], 
                                  hours['19'], hours['20'], hours['21'], hours['22'], hours['23'], 
                                  hours['24'])
                    
                    response = requests.post(url, data=body, headers=headers)
                    info = et.fromstring(response.content)[0][0][0]
                    jdata = json.loads(info.text)
                    resultados = jdata['resultado'][0]
                    code = resultados['codigo']
                    
                    if code != '2000':
                        print('No se pudo enviar la oferta de compra para la fecha', current_date, ':(')
                        exit()

                    else:
                        
                        now = datetime.now() - timedelta(.208333)
                        cliente = "Fandeli VDM"
                        Metodos = 'Promedio'
                        TOTAL = values_sum
                        fechas = date_1.strftime('%Y-%m-%d') + ',' + date_2.strftime('%Y-%m-%d') + ',' + date_3.strftime('%Y-%m-%d') + ',' + date_4.strftime('%Y-%m-%d')
                        dias = '0'

                        cursor = cnxn.cursor()

                        cursor.execute("""
                                        INSERT INTO [dbo].[ODC Beetmann]  
                                            ([Fecha de envio], [Fecha de la oferta de compra], [Cliente], [Metodo ], [Parametros usados (dias utlizados , dia mas parecido buscado)], 
                                            [Dias antes / despues al dia mas parecido], [Hora 1], [Hora 2], [Hora 3], [Hora 4], [Hora 5], [Hora 6], 
                                            [Hora 7], [Hora 8], [Hora 9], [Hora 10], [Hora 11], [Hora 12], [Hora 13], [Hora 14], [Hora 15], [Hora 16], 
                                            [Hora 17], [Hora 18], [Hora 19], [Hora 20], [Hora 21], [Hora 22], [Hora 23], [Hora 24], [TOTAL]) 
                                        values(?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        """, 
                                        now , datetime.strptime(ODC_date, '%d/%m/%Y'), cliente, Metodos, fechas, dias, hours['1'], hours['2'], 
                                        hours['3'], hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], hours['9'], hours['10'], hours['11'], 
                                        hours['12'], hours['13'], hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], hours['19'], 
                                        hours['20'], hours['21'], hours['22'], hours['23'], hours['24'], TOTAL)
                        
                        cnxn.commit()
                        print('Oferta de compra enviada y base de datos actualizada')

            current_date += timedelta(days=1)


def main_Artigraf():


    initial_date = date.fromisoformat(input('\nIngrese fecha inicial (aaaa/mm/dd): '))
    final_date = date.fromisoformat(input('Ingrese fecha final (aaaa/mm/dd): '))
    print()
    current_date = initial_date
    data = []
    cnxn = create_SQL_connection()

    with cnxn:

        while current_date <= final_date:
            query = """
                    SELECT * 
                    FROM [dbo].[ODC Beetmann] 
                    WHERE [Fecha de la oferta de compra] = '{date}' and Cliente = 'Artigraf San Juan del Rio'
                    """.format(date=current_date)
            existing_ODC = pd.read_sql(query, cnxn)
            
            if not existing_ODC.empty:
                print("Información existente")

            else:

                date_1, date_2 = current_date - timedelta(days=7), current_date - timedelta(days=14)
                date_3, date_4 = current_date - timedelta(days=21), current_date - timedelta(days=28)

                consulta_sql = """
SELECT table_1.Hora, AVG(table_1.Valor) AS Valor FROM 
(SELECT 
Convert(DATE, (([Fecha]+[Hora])-(.003472222))) AS 'Fecha', 
((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1) AS 'Hora', 
(ROUND(((sum([Kwhe]))/1000),4)*1.131221719457014000)  AS 'Valor' 
FROM [dbo].[Cincominutal Artigraf] 
WHERE (Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_1}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_2}'
OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_3}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_4}')
GROUP BY  Convert(DATE, (([Fecha]+[Hora])-(.003472222))), ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1)
) 
AS table_1 
GROUP BY table_1.Hora
                                """.format(d_1=date_1, d_2=date_2, d_3=date_3, d_4=date_4)
                df = pd.DataFrame(pd.read_sql(consulta_sql, cnxn))
                
                if df.empty:
                    print("No se encontró información para esta fecha")

                else:
                    print("Se encontró información para esta fecha")
                    values_sum = sum(df['Valor'])

                    url = 'https://ws01.cenace.gob.mx:8082/mxswmem/EnviarOfertaCompraEnergiaService.asmx?wsdl'
                    headers = {'content-type': 'text/xml'}
                    body = modules.requests_content_Artigraf.body

                    ODC_date = datetime.strftime(current_date, '%d/%m/%Y')
                    hours = {
                            '1': df['Valor'][0], '2': df['Valor'][1], '3': df['Valor'][2], '4': df['Valor'][3], 
                            '5': df['Valor'][4], '6': df['Valor'][5], '7': df['Valor'][6], '8': df['Valor'][7], 
                            '9': df['Valor'][8], '10': df['Valor'][9], '11': df['Valor'][10], '12': df['Valor'][11], 
                            '13': df['Valor'][12], '14': df['Valor'][13], '15': df['Valor'][14], '16': df['Valor'][15], 
                            '17': df['Valor'][16], '18': df['Valor'][17], '19': df['Valor'][18], '20': df['Valor'][19], 
                            '21': df['Valor'][20], '22': df['Valor'][21], '23': df['Valor'][22], '24': df['Valor'][23]
                            }
                    
                    body = body %(ODC_date, ODC_date, hours['1'], hours['2'], hours['3'], 
                                  hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], 
                                  hours['9'], hours['10'], hours['11'], hours['12'], hours['13'], 
                                  hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], 
                                  hours['19'], hours['20'], hours['21'], hours['22'], hours['23'], 
                                  hours['24'])
                    
                    response = requests.post(url, data=body, headers=headers)
                    info = et.fromstring(response.content)[0][0][0]
                    jdata = json.loads(info.text)
                    resultados = jdata['resultado'][0]
                    code = resultados['codigo']
                    
                    if code != '2000':
                        print('No se pudo enviar la oferta de compra para la fecha', current_date, ':(')
                        exit()

                    else:
                        
                        now = datetime.now() - timedelta(.208333)
                        cliente = "Artigraf"
                        Metodos = 'Promedio'
                        TOTAL = values_sum
                        fechas = date_1.strftime('%Y-%m-%d') + ',' + date_2.strftime('%Y-%m-%d') + ',' + date_3.strftime('%Y-%m-%d') + ',' + date_4.strftime('%Y-%m-%d')
                        dias = '0'

                        cursor = cnxn.cursor()

                        cursor.execute("""
                                        INSERT INTO [dbo].[ODC Beetmann]  
                                            ([Fecha de envio], [Fecha de la oferta de compra], [Cliente], [Metodo ], [Parametros usados (dias utlizados , dia mas parecido buscado)], 
                                            [Dias antes / despues al dia mas parecido], [Hora 1], [Hora 2], [Hora 3], [Hora 4], [Hora 5], [Hora 6], 
                                            [Hora 7], [Hora 8], [Hora 9], [Hora 10], [Hora 11], [Hora 12], [Hora 13], [Hora 14], [Hora 15], [Hora 16], 
                                            [Hora 17], [Hora 18], [Hora 19], [Hora 20], [Hora 21], [Hora 22], [Hora 23], [Hora 24], [TOTAL]) 
                                        values(?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        """, 
                                        now , datetime.strptime(ODC_date, '%d/%m/%Y'), cliente, Metodos, fechas, dias, hours['1'], hours['2'], 
                                        hours['3'], hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], hours['9'], hours['10'], hours['11'], 
                                        hours['12'], hours['13'], hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], hours['19'], 
                                        hours['20'], hours['21'], hours['22'], hours['23'], hours['24'], TOTAL)
                        
                        cnxn.commit()
                        print('Oferta de compra enviada y base de datos actualizada')

            current_date += timedelta(days=1)


def main_Karisma():

    initial_date = date.fromisoformat(input('\nIngrese fecha inicial (aaaa/mm/dd): '))
    final_date = date.fromisoformat(input('Ingrese fecha final (aaaa/mm/dd): '))
    print()
    current_date = initial_date
    data = []
    cnxn = create_SQL_connection()

    with cnxn:

        while current_date <= final_date:
            query = """
                    SELECT * 
                    FROM [dbo].[ODC Beetmann] 
                    WHERE [Fecha de la oferta de compra] = '{date}' and Cliente = 'Karisma'
                    """.format(date=current_date)
            existing_ODC = pd.read_sql(query, cnxn)
            
            if not existing_ODC.empty:
                print("Información existente")

            else:

                date_1, date_2 = current_date - timedelta(days=7), current_date - timedelta(days=14)
                date_3, date_4 = current_date - timedelta(days=21), current_date - timedelta(days=28)

                consulta_sql = """
SELECT table_1.Hora, AVG(table_1.Valor) AS Valor FROM 
(SELECT 
Convert(DATE, (([Fecha]+[Hora])-(.003472222))) AS 'Fecha', 
((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1) AS 'Hora', 
(ROUND(((sum([Kwhe]))/1000),4)*1.108647450110865000)  AS 'Valor' 
FROM [dbo].[Cincominutal Karisma] 
WHERE (Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_1}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_2}'
OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_3}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{d_4}') 
GROUP BY  Convert(DATE, (([Fecha]+[Hora])-(.003472222))), ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1)
) 
AS table_1 
GROUP BY table_1.Hora
                                """.format(d_1=date_1, d_2=date_2, d_3=date_3, d_4=date_4)
                df = pd.DataFrame(pd.read_sql(consulta_sql, cnxn))
                
                if df.empty:
                    print("No se encontró información para esta fecha")

                else:
                    print("Se encontró información para esta fecha")
                    values_sum = sum(df['Valor'])

                    url = 'https://ws01.cenace.gob.mx:8082/mxswmem/EnviarOfertaCompraEnergiaService.asmx?wsdl'
                    headers = {'content-type': 'text/xml'}
                    body = modules.requests_content_Karisma.body

                    ODC_date = datetime.strftime(current_date, '%d/%m/%Y')
                    hours = {
                            '1': df['Valor'][0], '2': df['Valor'][1], '3': df['Valor'][2], '4': df['Valor'][3], 
                            '5': df['Valor'][4], '6': df['Valor'][5], '7': df['Valor'][6], '8': df['Valor'][7], 
                            '9': df['Valor'][8], '10': df['Valor'][9], '11': df['Valor'][10], '12': df['Valor'][11], 
                            '13': df['Valor'][12], '14': df['Valor'][13], '15': df['Valor'][14], '16': df['Valor'][15], 
                            '17': df['Valor'][16], '18': df['Valor'][17], '19': df['Valor'][18], '20': df['Valor'][19], 
                            '21': df['Valor'][20], '22': df['Valor'][21], '23': df['Valor'][22], '24': df['Valor'][23]
                            }
                    
                    body = body %(ODC_date, ODC_date, hours['1'], hours['2'], hours['3'], 
                                  hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], 
                                  hours['9'], hours['10'], hours['11'], hours['12'], hours['13'], 
                                  hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], 
                                  hours['19'], hours['20'], hours['21'], hours['22'], hours['23'], 
                                  hours['24'])
                    
                    response = requests.post(url, data=body, headers=headers)
                    info = et.fromstring(response.content)[0][0][0]
                    jdata = json.loads(info.text)
                    resultados = jdata['resultado'][0]
                    code = resultados['codigo']
                    
                    if code != '2000':
                        print('No se pudo enviar la oferta de compra para la fecha', current_date, ':(')
                        exit()

                    else:
                        
                        now = datetime.now() - timedelta(.208333)
                        cliente = "Karisma"
                        Metodos = 'Promedio'
                        TOTAL = values_sum
                        fechas = date_1.strftime('%Y-%m-%d') + ',' + date_2.strftime('%Y-%m-%d') + ',' + date_3.strftime('%Y-%m-%d') + ',' + date_4.strftime('%Y-%m-%d')
                        dias = '0'

                        cursor = cnxn.cursor()

                        cursor.execute("""
                                        INSERT INTO [dbo].[ODC Beetmann]  
                                            ([Fecha de envio], [Fecha de la oferta de compra], [Cliente], [Metodo ], [Parametros usados (dias utlizados , dia mas parecido buscado)], 
                                            [Dias antes / despues al dia mas parecido], [Hora 1], [Hora 2], [Hora 3], [Hora 4], [Hora 5], [Hora 6], 
                                            [Hora 7], [Hora 8], [Hora 9], [Hora 10], [Hora 11], [Hora 12], [Hora 13], [Hora 14], [Hora 15], [Hora 16], 
                                            [Hora 17], [Hora 18], [Hora 19], [Hora 20], [Hora 21], [Hora 22], [Hora 23], [Hora 24], [TOTAL]) 
                                        values(?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        """, 
                                        now , datetime.strptime(ODC_date, '%d/%m/%Y'), cliente, Metodos, fechas, dias, hours['1'], hours['2'], 
                                        hours['3'], hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], hours['9'], hours['10'], hours['11'], 
                                        hours['12'], hours['13'], hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], hours['19'], 
                                        hours['20'], hours['21'], hours['22'], hours['23'], hours['24'], TOTAL)
                        
                        cnxn.commit()
                        print('Oferta de compra enviada y base de datos actualizada')

            current_date += timedelta(days=1)






if __name__ == '__main__':
    print("iniciando envio de ODC para URREA")
    main()
    print("iniciando envio de ODC para Zubex")
    main_zubex()
    print("iniciando envio de ODC para Fandeli QRO")
    main_Fandeli_QRO()
    print("iniciando envio de ODC para Fandeli VDM")
    main_Fandeli_VDM()  
    print("iniciando envio de ODC para Artigraf")
    main_Artigraf()  
    print("iniciando envio de ODC para Karisma")
    main_Karisma()  