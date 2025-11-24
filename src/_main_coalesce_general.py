"""
Created By Emerson Aguilar Cruz
"""

import os
import sys
import json
from coalesce._cls_etl_coalesce_ import EtlCoalesceTel

current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_folder)

sys.path.append(project_root)

config_path = os.path.join(project_root, "config", "config_coalesce.json")

with open(config_path, "r", encoding="utf-8") as f:
    config_campanas = json.load(f)

def elegir_campania() -> str:
    """
    Muestra un menú interactivo para seleccionar la campaña a ejecutar
    """
    campaigns = list(config_campanas.keys())

    print("\n" + "="*70)
    print("📋 CAMPAÑAS DISPONIBLES PARA COALESCE")
    print("="*70)
    
    for idx, nombre in enumerate(campaigns, start=1):
        print(f"  {idx}. 📌 {nombre}")
    
    print("="*70)

    while True:
        try:
            choice = int(input("\n👉 Ingrese el número de la campaña a ejecutar: "))
            if 1 <= choice <= len(campaigns):
                return campaigns[choice - 1]
            print("⚠️  Selección fuera de rango. Intente de nuevo.")
        except ValueError:
            print("❌ Entrada no válida. Debe ser un número entero.")

def main():
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + " "*15 + "🚀 PROCESO DE COALESCE DE TELÉFONOS" + " "*19 + "#")
    print("#" + " "*68 + "#")
    print("#"*70 + "\n")
    
    try:
        campana = elegir_campania()
        config = config_campanas[campana]
        sql_file = os.path.join(project_root, "sql", config["sql_file_path"])
        
        print("\n" + "="*70)
        print("✅ CONFIGURACIÓN DE CAMPAÑA")
        print("="*70)
        print(f"🎯 Campaña seleccionada: {campana}")
        print(f"🗄️  Base de datos: {config['schema']}")
        print(f"📊 Tabla destino: {config['table']}")
        print(f"📱 Columnas telefónicas: {', '.join(config['phone_columns'])}")
        print(f"📄 Script SQL: {config['sql_file_path']}")
        print("="*70 + "\n")

        print("\n" + "-"*70)
        print("🔄 INICIANDO PROCESO DE ETL COALESCE")
        print("-"*70)

        procesador = EtlCoalesceTel(
            schema=config["schema"],
            table=config["table"],
            sql_file_path=sql_file,
            cuenta=config["cuenta"],
            phone_columns=config["phone_columns"],
        )

        procesador.coalesce_etl()
        procesador.load_data()

        print("\n" + "#"*70)
        print("#" + " "*68 + "#")
        print("#" + " "*15 + "✅ PROCESO COMPLETADO EXITOSAMENTE" + " "*18 + "#")
        print("#" + " "*68 + "#")
        print("#"*70 + "\n")

    except FileNotFoundError as e:
        print(f"\n❌ Error: No se encontró el archivo SQL especificado")
        print(f"   Ruta buscada: {sql_file}")
        print(f"   Detalle: {e}\n")
    except KeyError as e:
        print(f"\n❌ Error: Configuración incompleta en el JSON")
        print(f"   Clave faltante: {e}\n")
    except Exception as error:
        print(f"\n❌ Error en el proceso principal: {error}")
        import traceback
        traceback.print_exc()
        print()


if __name__ == "__main__":
    main()
