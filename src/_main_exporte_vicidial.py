"""
Created By Emerson Aguilar Cruz
"""

import os
import json
from datetime import datetime
from exporte_sql._cls_exporte_sql import ExportarSql

current_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

json_formulario = os.path.join(current_folder, 'config', 'config_load_vicidial.json')
with open(json_formulario, "r") as file_json_formulario:
    config_formulario = json.load(file_json_formulario)


class ExporteFormulario:

    @staticmethod
    def elegir_campana():
        """
        Muestra un menú interactivo para seleccionar la campaña a exportar
        """
        print("\n" + "="*40)
        print("📋 CAMPAÑAS DISPONIBLES PARA EXPORTAR")
        print("="*40)
        
        for i, campana in enumerate(config_formulario.keys(), 1):
            print(f"  {i}. 📌 {campana}")
        
        print("="*40)

        seleccion = input("\n👉 Seleccione el número de la campaña a ejecutar: ")
        adicional = input("📝 Información adicional sobre lista (opcional): ")
        
        try:
            seleccion = int(seleccion)
            campana = list(config_formulario.keys())[seleccion - 1]
            
            print("\n" + "="*40)
            print("✅ CAMPAÑA SELECCIONADA")
            print("="*40)
            print(f"🎯 Campaña: {campana}")
            if adicional:
                print(f"📝 Info adicional: {adicional}")
            print("="*40 + "\n")
            
            return campana, adicional
        except (ValueError, IndexError):
            print("\n❌ Selección inválida. Intente nuevamente.\n")
            return None, None

    @staticmethod
    def exportar_xlsx_vicidial(campana_key, adicional):
        """
        Exporta la data de la campaña seleccionada en formato CSV para Vicidial
        """
        try:
            schema = 'bbdd_cos_bog_allianz'  # TODO: Esto debería venir del config
            folder_salida = os.path.join(current_folder, 'data', 'upload_vcdl', 'nuevo')
            os.makedirs(folder_salida, exist_ok=True)

            campana_sql = config_formulario[campana_key]["campana"]
            hoy_formateado = datetime.now().strftime('%d%m')
            nombre_archivo = f"{campana_key} - {hoy_formateado}_{adicional}" if adicional else f"{campana_key} - {hoy_formateado}"
            sql_path = os.path.join(current_folder, 'sql', f"_sql_depurador_predictivo_{campana_sql}.sql")

            print("\n" + "-"*40)
            print("🔄 CONFIGURACIÓN DE EXPORTACIÓN")
            print("-"*40)
            print(f"🗄️  Base de datos: {schema}")
            print(f"📁 Carpeta salida: {folder_salida}")
            print(f"📄 Archivo: {nombre_archivo}.csv")
            print(f"📜 Script SQL: _sql_depurador_predictivo_{campana_sql}.sql")
            print("-"*40 + "\n")

            print("🔄 Ejecutando exportación...\n")

            processor = ExportarSql(
                schema=schema,
                sql_path=sql_path,
                folder_salida=folder_salida,
                nombre_archivo=nombre_archivo
            )
            processor.exportar_csv()

            print("\n" + "="*40)
            print("✅ EXPORTACIÓN COMPLETADA")
            print("="*40)
            print(f"📁 Archivo guardado en: {folder_salida}")
            print(f"📄 Nombre: {nombre_archivo}.csv")
            print("="*40 + "\n")

        except FileNotFoundError as e:
            print(f"\n❌ Error: No se encontró el archivo SQL")
            print(f"   Ruta buscada: {sql_path}")
            print(f"   Detalle: {e}\n")
        except Exception as e:
            print(f"\n❌ Error al exportar: {e}")
            import traceback
            traceback.print_exc()
            print()


if __name__ == '__main__':
    
    campana, adicional = ExporteFormulario.elegir_campana()
    
    if campana:
        ExporteFormulario.exportar_xlsx_vicidial(campana, adicional)

    else:
        print("\n❌ No se pudo ejecutar la exportación\n")
