"""
Created By Emerson Aguilar Cruz
"""

import os
from exporte_sql._cls_exporte_sql import ExportarSql
import json

current_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

json_formulario = os.path.join(current_folder, 'config', 'config_formulario_soul.json')
with open(json_formulario, "r") as file_json_formulario:
    config_formulario = json.load(file_json_formulario)

class ExporteFormulario:

    @staticmethod
    def elegir_campana():

        print("Campañas disponibles:")
        for i, campana in enumerate(config_formulario.keys(), 1):
            print(f"{i}. {campana}")

        seleccion = input("Seleccione el número de la campaña a ejecutar: ")
        try:
            seleccion = int(seleccion)
            campana = list(config_formulario.keys())[seleccion - 1]
            print(f"Ejecutando exporte para campaña: {campana}")
            return campana
        except (ValueError, IndexError):
            print("Selección inválida. Intente nuevamente.")
            return None

    @staticmethod
    def exportar_csv_formulario(campana):
        try:
            schema = 'bbdd_cos_bog_allianz'
            folder_salida = os.path.join(current_folder, 'data', 'upload_soul', campana)
            os.makedirs(folder_salida, exist_ok=True)

            nombre_archivo = campana
            sql_path = os.path.join(current_folder, 'sql', f"_sql_formulario_soul_{campana}.sql")

            processor = ExportarSql(
                schema=schema,
                sql_path=sql_path,
                folder_salida=folder_salida,
                nombre_archivo=nombre_archivo
            )
            processor.exportar_excel()

        except Exception as e:
            print(f"Error: Error al exportar csv debido a {e}")


if __name__ == '__main__':
    campana = ExporteFormulario.elegir_campana()
    if campana:
        ExporteFormulario.exportar_csv_formulario(campana)
