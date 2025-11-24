"""""
Created By Emerson Aguilar Cruz
"""""

from conexiones_db._cls_sqlalchemy import MySQLConnector
from load_data._cls_load_data import *
from read_data._cls_read_data import FileReader
import os
import json


class LoadArbolTipificacion:

    def __init__(self, config_path=None, schema=None, table=None, archivo_excel=None):

        self.current_folder = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.current_folder)
        self.project_home = os.path.dirname(self.project_root)

        self.config_path = config_path 
        with open (self.config_path, 'r', encoding='utf-8') as f:
            self.config_arbol_tipificacion = json.load(f) 

        self.arboles_disponibles = [key for key in self.config_arbol_tipificacion.keys() if key not in ['schema', 'table']]
        print("Arboles disponibles:")
        for i, campaña in enumerate(self.arboles_disponibles, start=1):
            print(f"{i}. {campaña}")

        while True:
            try:
                seleccion = int(input("Ingrese el número del arbol que desea ejecutar: "))
                if 1 <= seleccion <= len(self.arboles_disponibles):
                    self.campana_seleccionada = self.arboles_disponibles[seleccion - 1]
                    break
                else:
                    print("Número inválido. Intente nuevamente.")
            except ValueError:
                print("Entrada no válida. Ingrese un número.")

        self.arbol_config = self.config_arbol_tipificacion[self.campana_seleccionada]

        self.schema = self.arbol_config['schema']
        self.table = self.arbol_config['table']

        self.archivo_excel = os.path.join(self.project_home, 'data', 'arbol_tipificacion', self.arbol_config['nombre_arbol'])
        os.makedirs(self.archivo_excel, exist_ok=True)

        self.engine = MySQLConnector().get_connection(database=self.schema)
        self.df = None
        self.loader = MySQLLoader(self.engine, self.schema, self.table)

    def read_arbol(self):
        if not hasattr(self, 'archivo_excel') or not os.path.exists(self.archivo_excel):
            raise ValueError(f"Error ruta no valida: {getattr(self.archivo_excel, 'No definida')}")

        archivos = [f for f in os.listdir(self.archivo_excel) if os.path.isfile(os.path.join(self.archivo_excel, f))]
        if not archivos:
            print(f"Error: No se encuentran archivos en la ruta: {self.archivo_excel}")
            return None

        try:
            reader = FileReader(start_path=self.archivo_excel, end_path=self.archivo_excel)

            hojas_disponibles, hoja_seleccionada = reader.sheet_names(reader.get_latest_file())
            print("Hojas encontradas:", hojas_disponibles)
            print("Hoja seleccionada:", hoja_seleccionada)

            if hoja_seleccionada:
                self.df = reader.read_directory_simple(sheet_name=hoja_seleccionada)
            else:
                print("No se seleccionó una hoja válida. No se cargaron datos.")
                return None

            if self.df is None or self.df.empty:
                print("Error: El archivo no se pudo leer o está vacío")
                return None

            self.df = self.df.replace("NA", "NA")
            self.df = self.df.where(pd.notnull(self.df), None)
            self.df['tipificacion_n3'] = self.df['tipificacion_n3'].fillna("NA")

            print("Registros con tipificacion_n3 'NA':", (self.df['tipificacion_n3'] == "NA").sum())
            print("Archivo leído y limpiado exitosamente")

        except Exception as e:
            print(f"Error: Error al leer el archivo por {e}")

    def ejecutar_query(self, query):
        try:
            with self.engine.connect() as conn:
                conn.execute(text(query))
                conn.commit()
                print("Consulta ejecutada exitosamente")
        except SQLAlchemyError as e:
            print(f"Error al ejecutar la consulta: {e}")

    def  load_data(self):
        self.loader.delete_all_and_insert(self.df)
        return print("Lectura Completada")
    
    def main(self):
        self.read_arbol()
        self.load_data()

        query_actualizacion = f"""
        UPDATE {self.table}
        SET tipificacion_n3 = "NA"
        WHERE tipificacion_n3 = "";
        """
        self.ejecutar_query(query_actualizacion)