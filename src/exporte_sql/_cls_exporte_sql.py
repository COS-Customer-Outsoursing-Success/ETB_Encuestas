"""
Created By Emerson Aguilar Cruz
Modificado por Juan David Ramirez - Segmentación automática Soul
"""

import sys
import os
import pandas as pd
from datetime import datetime

current_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)

from conexiones_db._cls_sqlalchemy import MySQLConnector


class ExportarSql:

    def __init__(self, schema=None, folder_salida=None, sql_path=None, nombre_archivo=None, segmentar_soul=False, campana=None):
        """
        Clase para exportar datos SQL a diferentes formatos
        
        Args:
            schema (str): Nombre del esquema de la base de datos
            folder_salida (str): Carpeta donde se guardarán los archivos
            sql_path (str): Ruta al archivo SQL
            nombre_archivo (str): Nombre base del archivo de salida
            segmentar_soul (bool): Si True, segmenta automáticamente en chunks de 1800
            campana (str): Nombre de la campaña (para segmentación Soul)
        """
        self.schema = schema
        self.engine = MySQLConnector().get_connection(database=self.schema)

        self.folder_salida = folder_salida or os.path.join(project_root, "data", "exportaciones")
        os.makedirs(self.folder_salida, exist_ok=True)
        
        self.nombre_archivo = nombre_archivo or "resultado"
        self.sql_path = sql_path
        self.df = None
        
        # Configuración de segmentación Soul
        self.segmentar_soul = segmentar_soul
        self.campana = campana
        self.chunk_size = 1800

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
            print(f"Consulta ejecutada correctamente. Filas obtenidas: {len(self.df):,}")
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
        """
        Exporta a Excel y segmenta automáticamente si está habilitado
        """
        if self.df is None:
            self.leer_sql()
        
        # Generar timestamp
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # Si la segmentación Soul está habilitada
        if self.segmentar_soul and self.campana:
            self._exportar_con_segmentacion(timestamp)
        else:
            # Exportación normal sin segmentación
            nombre_archivo = nombre_archivo or f"{self.nombre_archivo}.xlsx"
            ruta = os.path.join(self.folder_salida, nombre_archivo)
            self.df.to_excel(ruta, index=False, engine="openpyxl")
            print(f"Exportado a Excel en: {ruta}")

    def _exportar_con_segmentacion(self, timestamp):
        """
        Exporta el archivo completo en original_soul y segmenta en upload_soul
        
        Args:
            timestamp (str): Fecha en formato YYYYMMDD
        """
        total_filas = len(self.df)
        
        print("="*60)
        print(f"🔄 SEGMENTACIÓN AUTOMÁTICA SOUL - {self.campana}")
        print("="*60)
        print(f"📊 Total de filas: {total_filas:,}")
        
        # Normalizar nombre de campaña para archivos
        campana_archivo = self.campana.replace(' ', '_').upper()
        nombre_base = f"{campana_archivo}_{timestamp}"
        
        # 1. GUARDAR ORIGINAL COMPLETO en data/original_soul/[CAMPAÑA]/
        folder_original = os.path.join(project_root, "data", "original_soul", self.campana)
        os.makedirs(folder_original, exist_ok=True)
        
        ruta_original = os.path.join(folder_original, f"{nombre_base}.xlsx")
        self.df.to_excel(ruta_original, index=False, engine="openpyxl")
        print(f"✅ Original guardado: {ruta_original}")
        
        # 2. SEGMENTAR si tiene más de 1800 filas
        if total_filas > self.chunk_size:
            self._segmentar_chunks(nombre_base, total_filas)
        else:
            # Si tiene menos de 1800, copiar el archivo completo a upload_soul
            ruta_upload = os.path.join(self.folder_salida, f"{nombre_base}.xlsx")
            self.df.to_excel(ruta_upload, index=False, engine="openpyxl")
            print(f"✅ Archivo completo (sin segmentar): {ruta_upload}")
            print(f"ℹ️  El archivo tiene menos de {self.chunk_size} filas, no se segmentó")
        
        print("="*60)
        print("✅ EXPORTACIÓN Y SEGMENTACIÓN COMPLETADA")
        print("="*60)
    
    def _segmentar_chunks(self, nombre_base, total_filas):
        """
        Segmenta el DataFrame en chunks de 1800 filas
        
        Args:
            nombre_base (str): Nombre base del archivo (ej: ETB_REDES_20251206)
            total_filas (int): Total de filas del DataFrame
        """
        # Calcular número de chunks
        num_chunks = (total_filas + self.chunk_size - 1) // self.chunk_size
        print(f"📦 Se crearán {num_chunks} chunk(s) de {self.chunk_size} filas")
        print("-"*60)
        
        for i in range(num_chunks):
            inicio = i * self.chunk_size
            fin = min((i + 1) * self.chunk_size, total_filas)
            
            # Extraer chunk
            chunk_df = self.df.iloc[inicio:fin].copy()
            
            # Nombre del chunk
            nombre_chunk = f"{nombre_base}_chunk_{i+1}_de_{num_chunks}.xlsx"
            ruta_chunk = os.path.join(self.folder_salida, nombre_chunk)
            
            # Guardar chunk
            chunk_df.to_excel(ruta_chunk, index=False, engine="openpyxl")
            
            filas_en_chunk = len(chunk_df)
            print(f"✅ Chunk {i+1}/{num_chunks}: {nombre_chunk}")
            print(f"   📊 Filas: {inicio+1} a {fin} ({filas_en_chunk:,} filas)")

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
