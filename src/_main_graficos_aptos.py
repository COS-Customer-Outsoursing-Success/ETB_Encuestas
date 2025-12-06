"""
Generar gráficos de Aptos/No Aptos
"""
import sys
import os

# Agregar el directorio src al path
current_folder = os.path.dirname(os.path.abspath(__file__))
src_folder = os.path.dirname(current_folder)
sys.path.insert(0, src_folder)

from graficos_aptos._cls_graficos_aptos import GraficosAptos


def main():
    """
    Función principal
    """
    # Configuración de campañas (manual)
    campanas = [
        {'numero': 1, 'emoji': '📌', 'nombre': 'Aptos APP', 'archivo': 'app'}
    ]
    print("="*45)
    print()
    print("Seleccione la campaña a analizar:")
    print()
    
    # Mostrar opciones
    for campana in campanas:
        print(f"  {campana['emoji']}  {campana['numero']}. {campana['nombre']}")
    
    print()
    print("="*45)
    
    # Seleccionar campaña
    while True:
        try:
            seleccion = int(input("\nIngrese el número: "))
            
            # Buscar campaña seleccionada
            campana_seleccionada = None
            for campana in campanas:
                if campana['numero'] == seleccion:
                    campana_seleccionada = campana
                    break
            
            if campana_seleccionada:
                break
            else:
                print("❌ Número no válido, intente nuevamente")
        except ValueError:
            print("❌ Entrada no válida. Ingrese un número")
    
    print()
    
    # Crear generador y ejecutar
    generador = GraficosAptos(campana_seleccionada['archivo'])
    generador.ejecutar()
    
    print("\n✅ Proceso finalizado, Revisa data/img/aptos... ")


if __name__ == '__main__':
    main()
