# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import pandas as pd
import pyodbc
import requests
import xml.etree.ElementTree as et
from datetime import date, datetime, timedelta

import requests_content

def crear_conexion_SQL(method='sqlalchemy'):
    import pyodbc
    import sqlalchemy as sa

    driver_pyodbc = '{SQL Server}'
    driver_sqlalchemy = '{ODBC Driver 17 for SQL Server}' # DRIVER MAC OS M2
    server = 'tcp:beetmann-energy.database.windows.net'
    database = 'mercados'
    username = 'adm'
    password = 'MercadosBD20'
    try:
        if method == 'pyodbc':
            cnxn_data = 'DRIVER='+driver_pyodbc+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
            cnxn = pyodbc.connect(cnxn_data)

        elif method == 'sqlalchemy':
            cnxn_data = 'Driver='+driver_sqlalchemy+';+SERVER='+server+';+Database='+database+';+UID='+username+';+PWD='+password+';+Trusted_Connection=no;'
            cnxn = sa.create_engine('mssql+pyodbc:///?odbc_connect=Driver%3D%7BODBC+Driver+17+for+SQL+Server%7D%3B+SERVER%3Dtcp%3Abeetmann-energy.database.windows.net%3B+Database%3Dmercados%3B+UID%3Dadm%3B+PWD%3DMercadosBD20%3B+Trusted_Connection%3Dno%3B')
        
        return cnxn

    except:
        resp = "Error al crear una conexion con la base de datos"
        return resp

def odc(carga, multi, fecha_inicio, fecha_fin):
    current_date = datetime.strptime(str(fecha_inicio), '%Y-%m-%d %H:%M:%S').date()
    final_date = datetime.strptime(str(fecha_fin), '%Y-%m-%d %H:%M:%S').date()
    cnxn = crear_conexion_SQL(method='sqlalchemy')

    consulta_XML_sql = cnxn.execute(f"SELECT ieo.equipo_medimem FROM  Clave_de_carga_registro AS c INNER JOIN informacion_entrada_operacion AS ieo on c.clave = ieo.clave_de_carga WHERE c.clave = '{carga}'")
    equipo = consulta_XML_sql.fetchone()

    consulta_cliente = cnxn.execute(f"SELECT distinct icc.cliente AS CLIENTE FROM informacion_entrada_operacion as iep INNER JOIN informacion_contratos_clientes as icc ON iep.rpu = icc.rpu LEFT JOIN Clave_de_carga_registro AS c ON iep.clave_de_carga = c.clave WHERE iep.clave_de_carga = '{carga}' ")
    cliente_sql = consulta_cliente.fetchone()

    consulta_fp = cnxn.execute(f"SELECT c.division_tarifaria FROM Clave_de_carga_registro AS c INNER JOIN informacion_entrada_operacion AS ieo on c.clave = ieo.clave_de_carga WHERE iep.clave_de_carga = '{carga}' ")
    cliente_fp = consulta_fp.fetchone()

    while current_date <= final_date:
        query = f"SELECT *  FROM [dbo].[ODC Beetmann]  WHERE [Fecha de la oferta de compra] = '{current_date}' and Cliente = '{cliente_sql[0]}'"
        existing_ODC = pd.read_sql(query, cnxn)
        
        if not existing_ODC.empty:
            print("Información existente")

        else:
            date_1, date_2 = current_date - timedelta(days = 7), current_date - timedelta(days = 14)
            date_3, date_4 = current_date - timedelta(days = 21), current_date - timedelta(days = 28)

            consulta_fp = cnxn.execute(f"SELECT FDP FROM factor_de_perdidas WHERE Region LIKE '%{cliente_fp[0]}%'")
            fp_client = consulta_fp.fetchone()

            consulta_sql = f"SELECT table_1.Hora, AVG(table_1.Valor) AS Valor FROM  (SELECT Convert(DATE, (([Fecha]+[Hora])-(.003472222))) AS 'Fecha', \
            ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1) AS 'Hora', (ROUND(((sum([Kwhe]))/1000),4) * (1 + {fp_client[0]})) * {multi} AS 'Valor' \
            FROM [dbo].[Cincominutales_medimem] WHERE (Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{date_1}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{date_2}'\
            OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{date_3}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{date_4}') and (equipo = '{equipo[0]}' )\
            GROUP BY  Convert(DATE, (([Fecha]+[Hora])-(.003472222))), ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1) )  AS table_1  GROUP BY table_1.Hora"
            df = pd.DataFrame(pd.read_sql(consulta_sql, cnxn))
            
            if df.empty:
                print("No se encontró información para esta fecha")

            else:
                print("Se encontró información para esta fecha")
                values_sum = sum(df['Valor'])

                url = 'https://ws01.cenace.gob.mx:8082/mxswmem/EnviarOfertaCompraEnergiaService.asmx?wsdl'
                headers = {'content-type': 'text/xml'}
                body = requests_content.body

                ODC_date = datetime.strftime(current_date, '%d/%m/%Y')
                hours = {'1': df['Valor'][0], '2': df['Valor'][1], '3': df['Valor'][2], '4': df['Valor'][3], '5': df['Valor'][4], '6': df['Valor'][5], '7': df['Valor'][6], '8': df['Valor'][7], '9': df['Valor'][8], '10': df['Valor'][9], '11': df['Valor'][10], '12': df['Valor'][11], '13': df['Valor'][12], '14': df['Valor'][13], '15': df['Valor'][14], '16': df['Valor'][15], '17': df['Valor'][16], '18': df['Valor'][17], '19': df['Valor'][18], '20': df['Valor'][19], '21': df['Valor'][20], '22': df['Valor'][21], '23': df['Valor'][22], '24': df['Valor'][23] }
                body = body %(ODC_date, ODC_date, carga, hours['1'], hours['2'], hours['3'], hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], hours['9'], hours['10'], hours['11'], hours['12'], hours['13'], hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], hours['19'], hours['20'], hours['21'], hours['22'], hours['23'], hours['24'])
                
                response = requests.post(url, data = body, headers = headers)
                info = et.fromstring(response.content)[0][0][0]
                jdata = json.loads(info.text)
                resultados = jdata['resultado'][0]
                code = resultados['codigo']
                
                if code != '2000':
                    print('No se pudo enviar la oferta de compra para la fecha', current_date, ':(')
                    exit()

                else:
                    
                    now = datetime.now() - timedelta(.208333)
                    cliente = cliente_sql[0]
                    Metodos = 'Promedio'
                    TOTAL = values_sum
                    fechas = date_1.strftime('%Y-%m-%d') + ',' + date_2.strftime('%Y-%m-%d') + ',' + date_3.strftime('%Y-%m-%d') + ',' + date_4.strftime('%Y-%m-%d')
                    dias = '0'

                    cursor = cnxn.cursor()
                    query_almacenar = "INSERT INTO [dbo].[ODC Beetmann] ([Fecha de envio], [Fecha de la oferta de compra], [Cliente], [Metodo ], [Parametros usados (dias utlizados , dia mas parecido buscado)], [Dias antes / despues al dia mas parecido], [Hora 1], [Hora 2], [Hora 3], [Hora 4], [Hora 5], [Hora 6], [Hora 7], [Hora 8], [Hora 9], [Hora 10], [Hora 11], [Hora 12], [Hora 13], [Hora 14], [Hora 15], [Hora 16], [Hora 17], [Hora 18], [Hora 19], [Hora 20], [Hora 21], [Hora 22], [Hora 23], [Hora 24], [TOTAL]) values(?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
                    values = (now , datetime.strptime(ODC_date, '%d/%m/%Y'), cliente, Metodos, fechas, dias, hours['1'], hours['2'], hours['3'], hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], hours['9'], hours['10'], hours['11'], hours['12'], hours['13'], hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], hours['19'], hours['20'], hours['21'], hours['22'], hours['23'], hours['24'], TOTAL)
                    cursor.execute(query_almacenar, values)

                    print('Oferta de compra enviada y base de datos actualizada')

        current_date += timedelta(days=1)

def odc_all(carga_, multi, fecha_inicio, fecha_fin):
    current_date = datetime.strptime(str(fecha_inicio), '%Y-%m-%d %H:%M:%S').date()
    final_date = datetime.strptime(str(fecha_fin), '%Y-%m-%d %H:%M:%S').date()
    cnxn = crear_conexion_SQL(method='sqlalchemy')

    consulta_XML_sql = cnxn.execute(f"SELECT clave FROM  Clave_de_carga_registro")
    cargas_sql = consulta_XML_sql.fetchall()

    for x in cargas_sql:
        carga = x
        consulta_XML_sql = cnxn.execute(f"SELECT ieo.equipo_medimem FROM  Clave_de_carga_registro AS c INNER JOIN informacion_entrada_operacion AS ieo on c.clave = ieo.clave_de_carga WHERE c.clave = '{carga[0]}'")
        equipo = consulta_XML_sql.fetchone()

        consulta_cliente = cnxn.execute(f"SELECT distinct icc.cliente AS CLIENTE FROM informacion_entrada_operacion as iep INNER JOIN informacion_contratos_clientes as icc ON iep.rpu = icc.rpu LEFT JOIN Clave_de_carga_registro AS c ON iep.clave_de_carga = c.clave WHERE iep.clave_de_carga = '{carga[0]}' ")
        cliente_sql = consulta_cliente.fetchone()

        consulta_fp = cnxn.execute(f"SELECT c.division_tarifaria FROM Clave_de_carga_registro AS c INNER JOIN informacion_entrada_operacion AS ieo on c.clave = ieo.clave_de_carga WHERE iep.clave_de_carga = '{carga}' ")
        cliente_fp = consulta_fp.fetchone()

        while current_date <= final_date:
            query = f"SELECT *  FROM [dbo].[ODC Beetmann]  WHERE [Fecha de la oferta de compra] = '{current_date}' and Cliente = '{cliente_sql[0]}'"
            existing_ODC = pd.read_sql(query, cnxn)
            
            if not existing_ODC.empty:
                print("Información existente")

            else:
                date_1, date_2 = current_date - timedelta(days = 7), current_date - timedelta(days = 14)
                date_3, date_4 = current_date - timedelta(days = 21), current_date - timedelta(days = 28)

                consulta_fp = cnxn.execute(f"SELECT FDP FROM factor_de_perdidas WHERE Region LIKE '%{cliente_fp[0]}%'")
                fp_client = consulta_fp.fetchone()

                consulta_sql = f"SELECT table_1.Hora, AVG(table_1.Valor) AS Valor FROM  (SELECT Convert(DATE, (([Fecha]+[Hora])-(.003472222))) AS 'Fecha', \
                ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1) AS 'Hora', (ROUND(((sum([Kwhe]))/1000),4) * (1 + {fp_client[0]}) ) * {multi} AS 'Valor' \
                FROM [dbo].[Cincominutales_medimem] WHERE (Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{date_1}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{date_2}'\
                OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{date_3}' OR Convert(DATE, (([Fecha]+[Hora])-(.003472222))) = '{date_4}') and (equipo = '{equipo[0]}' )\
                GROUP BY  Convert(DATE, (([Fecha]+[Hora])-(.003472222))), ((DATEPART(hour,(([Fecha]+[Hora])-(.003472222))))+1) )  AS table_1  GROUP BY table_1.Hora"
                df = pd.DataFrame(pd.read_sql(consulta_sql, cnxn))
                
                if df.empty:
                    print("No se encontró información para esta fecha")

                else:
                    print("Se encontró información para esta fecha")
                    values_sum = sum(df['Valor'])

                    url = 'https://ws01.cenace.gob.mx:8082/mxswmem/EnviarOfertaCompraEnergiaService.asmx?wsdl'
                    headers = {'content-type': 'text/xml'}
                    body = requests_content.body

                    ODC_date = datetime.strftime(current_date, '%d/%m/%Y')
                    hours = {'1': df['Valor'][0], '2': df['Valor'][1], '3': df['Valor'][2], '4': df['Valor'][3], '5': df['Valor'][4], '6': df['Valor'][5], '7': df['Valor'][6], '8': df['Valor'][7], '9': df['Valor'][8], '10': df['Valor'][9], '11': df['Valor'][10], '12': df['Valor'][11], '13': df['Valor'][12], '14': df['Valor'][13], '15': df['Valor'][14], '16': df['Valor'][15], '17': df['Valor'][16], '18': df['Valor'][17], '19': df['Valor'][18], '20': df['Valor'][19], '21': df['Valor'][20], '22': df['Valor'][21], '23': df['Valor'][22], '24': df['Valor'][23] }
                    body = body %(ODC_date, ODC_date, carga[0], hours['1'], hours['2'], hours['3'], hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], hours['9'], hours['10'], hours['11'], hours['12'], hours['13'], hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], hours['19'], hours['20'], hours['21'], hours['22'], hours['23'], hours['24'])
                    
                    response = requests.post(url, data = body, headers = headers)
                    info = et.fromstring(response.content)[0][0][0]
                    jdata = json.loads(info.text)
                    resultados = jdata['resultado'][0]
                    code = resultados['codigo']
                    
                    if code != '2000':
                        print('No se pudo enviar la oferta de compra para la fecha', current_date, ':(')
                        exit()

                    else:
                        
                        now = datetime.now() - timedelta(.208333)
                        cliente = cliente_sql[0]
                        Metodos = 'Promedio'
                        TOTAL = values_sum
                        fechas = date_1.strftime('%Y-%m-%d') + ',' + date_2.strftime('%Y-%m-%d') + ',' + date_3.strftime('%Y-%m-%d') + ',' + date_4.strftime('%Y-%m-%d')
                        dias = '0'

                        cursor = cnxn.cursor()
                        query_almacenar = "INSERT INTO [dbo].[ODC Beetmann] ([Fecha de envio], [Fecha de la oferta de compra], [Cliente], [Metodo ], [Parametros usados (dias utlizados , dia mas parecido buscado)], [Dias antes / despues al dia mas parecido], [Hora 1], [Hora 2], [Hora 3], [Hora 4], [Hora 5], [Hora 6], [Hora 7], [Hora 8], [Hora 9], [Hora 10], [Hora 11], [Hora 12], [Hora 13], [Hora 14], [Hora 15], [Hora 16], [Hora 17], [Hora 18], [Hora 19], [Hora 20], [Hora 21], [Hora 22], [Hora 23], [Hora 24], [TOTAL]) values(?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
                        values = (now , datetime.strptime(ODC_date, '%d/%m/%Y'), cliente, Metodos, fechas, dias, hours['1'], hours['2'], hours['3'], hours['4'], hours['5'], hours['6'], hours['7'], hours['8'], hours['9'], hours['10'], hours['11'], hours['12'], hours['13'], hours['14'], hours['15'], hours['16'], hours['17'], hours['18'], hours['19'], hours['20'], hours['21'], hours['22'], hours['23'], hours['24'], TOTAL)
                        cursor.execute(query_almacenar, values)

                        print('Oferta de compra enviada y base de datos actualizada')

            current_date += timedelta(days=1)

def menu_consulta_dias_rango(carga, multi):
    input_inicio = ''
    input_fin = ''

    while True:
        input_inicio = input(f"Coloca el periodo de Inicio (YYYY-MM-DD): ") 
        input_fin = input(f"Coloca el periodo de Fin (YYYY-MM-DD): ") 

        try:
            fecha_inicio = datetime.strptime(input_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(input_fin, '%Y-%m-%d')

            if carga == 'todos':
                return odc_all(carga, multi, fecha_inicio, fecha_fin)

            if fecha_inicio > fecha_fin:
                print("La fecha de inicio debe ser menor que la fecha de fin. Inténtalo de nuevo.")
            else:
                return odc(carga, multi, fecha_inicio, fecha_fin)

        except ValueError:
            print("El formato de fecha no es válido. Inténtalo de nuevo.")

def menu_consulta_input(carga):
    if carga == 'todos':
        while True:
            multi = input(f"Coloca el multiplicador (Default 1): ") or '1'

            if multi.strip():
                return menu_consulta_dias_rango(carga, multi)
            else:
                print("Debe ingresar todos los valores.")
    
    else:
        while True:
            multi = input(f"Coloca el multiplicador (Default 1): ") or '1'

            if multi.strip():
                return menu_consulta_dias_rango(carga, multi)
            else:
                print("Debe ingresar todos los valores.")

def main():
    cnxn = crear_conexion_SQL(method='sqlalchemy')
    consulta_XML_sql = cnxn.execute('SELECT clave FROM  Clave_de_carga_registro')
    cargas = consulta_XML_sql.fetchall()
    opciones =  [tupla[0] for tupla in cargas]
    opciones.append("todos")
    
    print("\nSeleccione la carga a facturar:\n")
    for i, opcion in enumerate(opciones):
        print(f"\t{i + 1}. {opcion}")

    while True:
        try:
            opcion = int(input("> "))
            if str(opcion).lower() == "todos":
                odc_all()
            if opcion < 1 or opcion > len(opciones):
                raise ValueError()
            return menu_consulta_input(opciones[opcion-1])
        except ValueError:
            print("Ingrese una opción válida.")

if __name__ == '__main__':
    main()
