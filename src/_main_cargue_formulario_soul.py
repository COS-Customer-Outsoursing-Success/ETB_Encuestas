"""""
Created By Emerson Aguilar Cruz
"""""

import os
import sys

current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)

from soul_formulario._cls_cargue_formularios import FormulariosSoul
    
def main():
    
    # -- Config Credenciales --
    usuario = 'juan.ramirezl'
    contrasena = 'Ju@ncho.5517'

    
    # -- Inicializador de clases -- 
    processor_soul = FormulariosSoul(

        usuario=usuario,
        contrasena=contrasena
    )

    try:
        processor_soul.buscar_formulario()
        processor_soul.cargar_formulario()
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")

if __name__ == '__main__':

    main()