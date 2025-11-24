"""
Created By Emerson Aguilar Cruz
"""

import sys
import os
import pandas as pd

current_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)

from conexiones_db._cls_sqlalchemy import MySQLConnector


class ExportarSql:

    def __init__(self, schema=None, folder_salida=None, sql_path=None, nombre_archivo=None):
        self.schema = schema
        self.engine = MySQLConnector().get_connection(database=self.schema)

        self.folder_salida = folder_salida or os.path.join(project_root, "data", "exportaciones")
        os.makedirs(self.folder_salida, exist_ok=True)
        
        self.nombre_archivo = nombre_archivo or "resultado"
        self.sql_path = sql_path
        self.df = None

    def leer_sql(self):
        """Ejecuta la consulta SQL y carga el DataFrame"""
        try:
            with open(self.sql_path, 'r', encoding='utf-8') as file:
                query_sql = file.read()
                print("Leyendo Archivo SQL...")
        except Exception as e:
            raise Exception(f"Error al leer archivo SQL: {e}")

        try:
            self.df = pd.read_sql(query_sql, self.engine)
            print(f"Consulta ejecutada correctamente. Filas obtenidas: {len(self.df)}")
        except Exception as e:
            raise Exception(f"Error al ejecutar SQL: {e}")

        return self.df

    def exportar_csv(self, nombre_archivo=None, sep=","):
        if self.df is None:
            self.leer_sql()
        nombre_archivo = nombre_archivo or f"{self.nombre_archivo}.csv"
        ruta = os.path.join(self.folder_salida, nombre_archivo)
        self.df.to_csv(ruta, index=False, sep=sep, encoding="utf-8-sig")
        print(f"Exportado a CSV en: {ruta}")

    def exportar_excel(self, nombre_archivo=None):
        if self.df is None:
            self.leer_sql()
        nombre_archivo = nombre_archivo or f"{self.nombre_archivo}.xlsx"
        ruta = os.path.join(self.folder_salida, nombre_archivo)
        self.df.to_excel(ruta, index=False, engine="openpyxl")
        print(f"Exportado a Excel en: {ruta}")

    def exportar_txt(self, nombre_archivo=None, sep="\t"):
        if self.df is None:
            self.leer_sql()
        nombre_archivo = nombre_archivo or f"{self.nombre_archivo}.txt"
        ruta = os.path.join(self.folder_salida, nombre_archivo)
        self.df.to_csv(ruta, index=False, sep=sep, encoding="utf-8")
        print(f"Exportado a TXT en: {ruta}")

    def exportar(self, formato="csv"):
        formato = formato.lower()
        if formato == "csv":
            self.exportar_csv()
        elif formato == "excel":
            self.exportar_excel()
        elif formato == "txt":
            self.exportar_txt()
        elif formato == "all":
            self.exportar_csv()
            self.exportar_excel()
            self.exportar_txt()
            print("Exportado en todos los formatos disponibles.")
        else:
            raise ValueError("Formato no soportado. Use: 'csv', 'excel', 'txt' o 'all'.")
