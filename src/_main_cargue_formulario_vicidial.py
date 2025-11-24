"""""
Created By Emerson Aguilar Cruz
"""""

import os
import sys

current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)

from vicidial._cls_load_vcdl import LoadListVcdl
    
def main():
    
    # -- Config Vcdl --
    user_vcdl = '1001185516'
    activo = 'Y'
    opcion_copiado = 'APPEND'
    indicativo_pais = '57 - COL'
    
    # -- Inicializador de clases -- 
    processor_load_vcdl = LoadListVcdl(

        user_vcdl=user_vcdl,
        activo=activo,
        opcion_copiado=opcion_copiado,
        indicativo_pais=indicativo_pais

    )

    try:
        processor_load_vcdl.cargar_vicidial()
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")

if __name__ == '__main__':

    main()