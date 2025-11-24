"""""
Created By Emerson Aguilar Cruz
"""""

import os
import sys

current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)

from arbol_tipificacion._cls_load_arbol_tipificacion import LoadArbolTipificacion
    
def main():
           
    config_path = os.path.join(project_root, 'config', 'config_arbol_tipificacion.json')
    
    # -- Inicializador de clases -- 
    processor_arbol = LoadArbolTipificacion(
        config_path = config_path, 

    )

    try:
        processor_arbol.main()
    except Exception as e:
        print(f"Error en el proceso principal: {str(e)}")

if __name__ == '__main__':

    main()