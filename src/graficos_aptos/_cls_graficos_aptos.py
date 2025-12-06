"""
Generador de gráficos de Aptos/No Aptos para ETB
Lee queries SQL, ejecuta contra la base de datos y genera gráficos con colores ETB
Autor: Juan David Ramirez
"""
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

current_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)

from conexiones_db._cls_sqlalchemy import MySQLConnector


class GraficosAptos:
    
    # Colores oficiales de ETB
    COLORES_ETB = {
        'azul_principal': '#0033A0',      # Azul ETB principal
        'azul_oscuro': '#001F5F',         # Azul oscuro
        'azul_claro': '#4A90E2',          # Azul claro
        'gris': '#6C757D',                # Gris
        'verde': '#28A745',               # Verde (aptos)
        'rojo': '#DC3545',                # Rojo (no aptos)
        'naranja': '#FD7E14',             # Naranja (advertencia)
        'amarillo': '#FFC107'             # Amarillo
    }
    
    def __init__(self, campana='APP'):
        """
        Inicializa el generador de gráficos
        
        Args:
            campana (str): Nombre de la campaña ('APP', 'REDES', etc.)
        """
        self.campana = campana.upper()
        
        # Rutas del proyecto
        self.project_root = Path(project_root)
        self.sql_folder = self.project_root / 'sql'
        self.output_folder = self.project_root / 'data' / 'img' / 'aptos' / campana.lower()
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Conexión a BD usando el .env existente
        self.schema = 'bbdd_cos_bog_etb_auditorias_encuestas'
        
        print("="*45)
        print(f"GENERADOR DE GRÁFICOS DE APTOS - {self.campana}")
        print("="*45)
        print(f"📁 Carpeta SQL: {self.sql_folder}")
        print(f"📁 Carpeta de salida: {self.output_folder}")
        print("="*45)
    
    def conectar_db(self):
        """
        Conecta a la base de datos MySQL usando MySQLConnector con .env
        
        Returns:
            engine: Motor SQLAlchemy
        """
        try:
            engine = MySQLConnector().get_connection(database=self.schema)
            print("✅ Conexión a base de datos exitosa")
            return engine
        except Exception as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            raise
    
    def leer_query_sql(self):
        """
        Lee el archivo SQL correspondiente a la campaña
        
        Returns:
            str: Contenido de la query SQL
        """
        # Buscar archivo SQL de aptos
        sql_file = self.sql_folder / f'_sql_aptos_etb_{self.campana.lower()}.sql'
        
        if not sql_file.exists():
            raise FileNotFoundError(f"No se encontró el archivo SQL: {sql_file}")
        
        print(f"📖 Leyendo query: {sql_file.name}")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            query = f.read()
        
        return query
    
    def ejecutar_query(self, query):
        """
        Ejecuta la query y retorna un DataFrame
        
        Args:
            query (str): Query SQL a ejecutar
        
        Returns:
            DataFrame: Resultados de la query
        """
        print("🔄 Ejecutando query...")
        
        engine = self.conectar_db()
        
        try:
            df = pd.read_sql(query, engine)
            print(f"✅ Query ejecutada. Filas obtenidas: {len(df)}")
            return df
        except Exception as e:
            print(f"❌ Error ejecutando query: {e}")
            raise
    
    def generar_grafico_barras(self, df):
        """
        Genera un gráfico de barras con estilo empresarial ETB
        
        Args:
            df (DataFrame): Datos a graficar
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'aptos_{self.campana.lower()}_{timestamp}.png'
        filepath = self.output_folder / filename
        
        print(f"\n📊 Generando gráfico de barras...")
        
        # Configurar figura con más espacio
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('#F5F5F5')  # Fondo gris muy claro
        
        # Crear degradado de azules ETB para las barras
        num_categorias = len(df)
        colores_azules = [
            '#0033A0',  # Azul oscuro ETB
            '#1a4db8',
            '#3366cc',
            '#4d80e0',
            '#6699ff',
            '#80b3ff',
            '#99ccff',
            '#b3d9ff'
        ]
        
        # Si hay más categorías que colores, repetir los colores
        colores = colores_azules[:num_categorias] if num_categorias <= len(colores_azules) else colores_azules * (num_categorias // len(colores_azules) + 1)
        colores = colores[:num_categorias]
        
        # Crear barras horizontales
        bars = ax.barh(df['categoria'], df['total'], color=colores, edgecolor='#0033A0', linewidth=1.5, alpha=0.9)
        
        # Agregar valores en las barras con estilo empresarial
        for i, (bar, valor) in enumerate(zip(bars, df['total'])):
            width = bar.get_width()
            ax.text(width + max(df['total']) * 0.02, bar.get_y() + bar.get_height()/2,
                   f'{int(valor):,}', 
                   ha='left', va='center', fontweight='bold', fontsize=11, color='#0033A0')
        
        # Títulos y etiquetas con estilo empresarial
        ax.set_xlabel('Cantidad de Registros', fontsize=13, fontweight='bold', 
                     color='#0033A0', labelpad=10)
        ax.set_ylabel('Categoría', fontsize=13, fontweight='bold', 
                     color='#0033A0', labelpad=10)
        ax.set_title(f'Análisis de Aptos - ETB {self.campana}\n{datetime.now().strftime("%d/%m/%Y %H:%M")}',
                    fontsize=16, fontweight='bold', color='#0033A0', pad=25)
        
        # Grid empresarial
        ax.grid(axis='x', alpha=0.2, linestyle='-', linewidth=0.5, color='#0033A0')
        ax.set_axisbelow(True)
        
        # Fondo del área de ploteo
        ax.set_facecolor('white')
        
        # Spines (bordes) con estilo ETB
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#0033A0')
        ax.spines['left'].set_linewidth(2)
        ax.spines['bottom'].set_color('#0033A0')
        ax.spines['bottom'].set_linewidth(2)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#F5F5F5')
        print(f"✅ Gráfico de barras guardado: {filepath}")
        
        plt.close()
        
        return filepath
    
    def generar_tabla(self, df):
        """
        Genera una tabla estilo empresarial con los resultados
        
        Args:
            df (DataFrame): Datos a graficar
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'aptos_tabla_{self.campana.lower()}_{timestamp}.png'
        filepath = self.output_folder / filename
        
        print(f"📋 Generando tabla...")
        
        # Configurar figura
        fig, ax = plt.subplots(figsize=(10, len(df) * 0.6 + 2))
        fig.patch.set_facecolor('#F5F5F5')
        ax.axis('off')
        
        # Preparar datos para la tabla
        datos_tabla = []
        for _, row in df.iterrows():
            datos_tabla.append([row['categoria'], f"{int(row['total']):,}"])
        
        # Crear tabla
        tabla = ax.table(
            cellText=datos_tabla,
            colLabels=['Categoría', 'Total'],
            cellLoc='left',
            loc='center',
            colWidths=[0.7, 0.3]
        )
        
        # Estilo empresarial ETB
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(11)
        tabla.scale(1, 2.5)
        
        # Estilo del header
        for i in range(2):
            cell = tabla[(0, i)]
            cell.set_facecolor('#0033A0')
            cell.set_text_props(weight='bold', color='white', fontsize=12)
            cell.set_edgecolor('white')
            cell.set_linewidth(2)
        
        # Estilo de las filas (alternar colores)
        for i in range(1, len(datos_tabla) + 1):
            for j in range(2):
                cell = tabla[(i, j)]
                if i % 2 == 0:
                    cell.set_facecolor('#E6F2FF')  # Azul muy claro
                else:
                    cell.set_facecolor('white')
                cell.set_edgecolor('#0033A0')
                cell.set_linewidth(0.5)
                cell.set_text_props(color='#0033A0', fontsize=11)
                
                # Negrita en la columna de totales
                if j == 1:
                    cell.set_text_props(weight='bold', color='#0033A0')
        
        # Título
        plt.title(f'Detalle de Registros - ETB {self.campana}\n{datetime.now().strftime("%d/%m/%Y %H:%M")}',
                 fontsize=14, fontweight='bold', color='#0033A0', pad=20)
        
        # Guardar
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#F5F5F5')
        print(f"✅ Tabla guardada: {filepath}")
        
        plt.close()
        
        return filepath
    
    def ejecutar(self):
        """
        Ejecuta el proceso completo: lee query, ejecuta y genera gráficos
        """
        try:
            # Leer query
            query = self.leer_query_sql()
            
            # Ejecutar query
            df = self.ejecutar_query(query)
            
            if df.empty:
                print("⚠️  La query no retornó resultados")
                return
            
            print("\n📋 Resultados:")
            print(df.to_string(index=False))
            print()
            
            # Generar gráfico de barras y tabla
            grafico_barras = self.generar_grafico_barras(df)
            tabla = self.generar_tabla(df)
            
            print("\n" + "="*45)
            print("✅ PROCESO COMPLETADO EXITOSAMENTE")
            print("="*45)
            print(f"📊 Gráfico de barras: {grafico_barras}")
            print(f"📋 Tabla: {tabla}")
            print("="*45)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            raise
