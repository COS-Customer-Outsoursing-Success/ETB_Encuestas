"""
Created By Emerson Aguilar Cruz
Mejorado: Mensajes cortos, sin duplicados de periodo, encoding UTF-8 corregido, archivo no bloqueado
"""
import os
from datetime import datetime
from conexiones_db._cls_sqlalchemy import MySQLConnector 
from read_data._cls_read_data import *
from load_data._cls_load_data import *
import json
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

class LoadAsignacion:

    def __init__(self, config_path=None):
        
        self.fecha = datetime.now().strftime("%Y-%m-%d")
        
        self.current_folder = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.current_folder)
        self.project_home = os.path.dirname(self.project_root)

        self.config_path = config_path
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config_asignacion = json.load(f)

        self.campanas_disponibles = [key for key in self.config_asignacion.keys() if key not in ['schema', 'table']]
        
        print("\n" + "="*50)
        print("📋 CAMPAÑAS DISPONIBLES")
        print("="*50)
        
        for i, campaña in enumerate(self.campanas_disponibles, start=1):
            print(f"  {i}. 📌 {campaña}")
        
        print("="*50)

        while True:
            try:
                seleccion = int(input("\n👉 Número de campaña: "))
                if 1 <= seleccion <= len(self.campanas_disponibles):
                    self.campana_seleccionada = self.campanas_disponibles[seleccion - 1]
                    break
                else:
                    print("⚠️  Inválido.")
            except ValueError:
                print("❌ Ingrese un número.")

        self.campana_config = self.config_asignacion[self.campana_seleccionada]

        self.start_path = os.path.join(self.project_home, 'data', 'asignacion', 'nueva', self.campana_config['nombre_asignacion'])
        self.end_path = os.path.join(self.project_home, 'data', 'asignacion', 'cargado', self.campana_config['nombre_asignacion'])
        os.makedirs(self.start_path, exist_ok=True)
        os.makedirs(self.end_path, exist_ok=True)
        
        self.schema = self.campana_config['schema']
        self.table = self.campana_config['table']

        self.engine = MySQLConnector().get_connection(database=self.schema)
        self.df = None
        self.loader = MySQLLoader(self.engine, self.schema, self.table)

        print("\n" + "="*50)
        print("✅ CONFIGURACIÓN")
        print("="*50)
        print(f"🎯 Campaña: {self.campana_seleccionada}")
        print(f"🗄️  BD: {self.schema}")
        print(f"📊 Tabla: {self.table}")
        print("="*50)

    def _seleccionar_hoja(self, hojas):
        print("\n" + "="*50)
        print("📋 SELECCIÓN DE HOJA")
        print("="*50)
        
        for i, hoja in enumerate(hojas, start=1):
            print(f"  {i}. 📄 {hoja}")
        
        print("="*50)
        
        while True:
            try:
                sel = int(input("\n👉 Número: "))
                if 1 <= sel <= len(hojas):
                    return hojas[sel - 1]
                else:
                    print(f"⚠️  Entre 1 y {len(hojas)}.")
            except ValueError:
                print("❌ Número.")

    def _solicitar_periodo(self):
        print("\n" + "="*50)
        print("📅 PERIODO")
        print("="*50)
        
        while True:
            periodo = input("👉 AAAAMM (ej:202511): ")
            if periodo.isdigit() and len(periodo) == 6:
                print(f"✅ {periodo}")
                print("="*50)
                return periodo
            else:
                print("❌ 6 dígitos.")

    def _corregir_encoding(self, df):
        """Corrige Ã±→ñ, Ã→í, etc"""
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(lambda x: 
                x.encode('latin1').decode('utf-8', errors='ignore') 
                if isinstance(x, str) and 'Ã' in x 
                else x
            )
        return df
        
    def read_data(self):

        telefonos = self.campana_config['telefonos']

        if not os.path.exists(self.start_path):
            raise ValueError(f"Ruta no válida")

        files = [f for f in os.listdir(self.start_path) if os.path.isfile(os.path.join(self.start_path, f))]
        if not files:
            print(f"❌ Sin archivos")
            return None

        try:
            reader = FileReader(start_path=self.start_path, end_path=self.end_path)
            latest_file_path = reader.get_latest_file()

            if not latest_file_path:
                print("❌ Sin archivo")
                return None

            nombre_archivo = os.path.basename(latest_file_path)
            nombre_base = os.path.splitext(nombre_archivo)[0]
            
            # Hojas - CERRAR AUTOMÁTICAMENTE
            try:
                with pd.ExcelFile(latest_file_path) as xls:
                    hojas = xls.sheet_names
            except Exception as e:
                print(f"❌ {e}")
                return None
            
            hoja_sel = self._seleccionar_hoja(hojas)
            
            print("\n" + "="*50)
            print("📄 LECTURA")
            print("="*50)
            print(f"📎 {nombre_archivo}")
            print(f"📋 {hoja_sel}")
            print("="*50)

            # Leer Y CERRAR automáticamente con with
            with pd.ExcelFile(latest_file_path) as xls:
                self.df = pd.read_excel(xls, sheet_name=hoja_sel)
            
            # Limpiar headers
            self.df.columns = reader._clean_headers(self.df).columns
            
            # CORREGIR ENCODING
            self.df = self._corregir_encoding(self.df)
            
            # Periodo
            periodo = self._solicitar_periodo()
            
            # Control
            creation_time = reader.get_creation_time(latest_file_path)
            creation_date = datetime.strptime(creation_time, '%Y-%m-%d %H:%M:%S')
            year = creation_date.strftime('%Y')
            
            self.df['fecha_asignacion'] = creation_time
            self.df['anio'] = year
            self.df['periodo'] = periodo
            self.df['fecha_cargue'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.df['nombre_base'] = nombre_base
            self.df['hoja'] = hoja_sel

            if self.df.empty:
                print("❌ Vacío")
                return None
            
            # Mover archivo (ahora sí debería funcionar)
            try:
                reader.move_file(nombre_archivo)
                print(f"✅ Archivo movido")
            except Exception as e:
                print(f"⚠️  No se movió: {str(e)[:50]}")
            
            print("\n" + "="*50)
            print("🔍 ANÁLISIS")
            print("="*50)
            print(f"📊 Registros: {len(self.df):,}")
            print(f"📑 Columnas: {len(self.df.columns)}")
            print("="*50)

            # Renombrar
            if self.campana_config['renombrar_columnas']:
                self.df = self.df.rename(columns=self.campana_config['renombrar_columnas'])

            print("\n" + "="*50)
            print("🔄 TRANSFORMACIÓN")
            print("="*50)

            # Columnas
            cols_nec = self.campana_config['columnas_necesarias']
            cols_ex = [c for c in cols_nec if c in self.df.columns]
            self.df = self.df[cols_ex]
            print(f"📋 Cols: {len(cols_ex)}")
            
            # Tipos
            for col in self.df.columns:
                if self.df[col].dtype in ['float64', 'int64']:
                    self.df[col] = self.df[col].astype(object)
                self.df[col] = self.df[col].where(pd.notnull(self.df[col]), None)

            for col in self.df.select_dtypes(include='object').columns:
                self.df[col] = self.df[col].fillna('-')

            self.df = self.df.where(pd.notnull(self.df), None)
            
            # Tels - LIMPIEZA MEJORADA
            def std_tel(x):
                if pd.isna(x) or x == '-' or x is None:
                    return '-'
                x = str(x).strip()
                # Limpiar caracteres raros como "?"
                x = x.replace('?', '').replace('¿', '').replace('�', '')
                # Eliminar espacios y caracteres no numéricos (excepto +)
                x = ''.join(c for c in x if c.isdigit() or c == '+')
                # Si quedó vacío, retornar -
                if not x or x == '':
                    return '-'
                # Agregar prefijo si es número de 7 dígitos
                x = '601' + x if len(x) == 7 and x.isdigit() else x
                return x

            for col in telefonos:
                if col in self.df.columns:
                    self.df[col] = self.df[col].apply(std_tel)
            
            print(f"📞 Tels: {len(telefonos)}")

            # Fechas
            cols_fecha = self.campana_config['columnas_fecha']
            for col in cols_fecha:
                if col in self.df.columns:
                    try:
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    except:
                        pass
            
            print(f"📅 Fechas: {len(cols_fecha)}")

            # Duplicados
            cols_dup = self.campana_config.get('cols_duplicados', [])
            
            if cols_dup and all(c in self.df.columns for c in cols_dup):
                try:
                    antes = len(self.df)
                    df_dup = self.df[self.df.duplicated(subset=cols_dup, keep=False)]

                    if not df_dup.empty:
                        try:
                            self.loader.table_name = self.campana_config['table_duplicados']
                            self.loader.schema = self.schema
                            self.loader.upsert_into_table(df_dup[cols_dup])
                            print(f"💾 Dups: {len(df_dup):,}")
                        except:
                            pass

                        self.df.drop_duplicates(subset=cols_dup, inplace=True)
                        print(f"🗑️  -{antes - len(self.df):,}")
                except:
                    pass
            
            print(f"✅ Final: {len(self.df):,}")
            print("="*50)

            # Val final
            for col in self.df.columns:
                if self.df[col].dtype in ['float64', 'int64']:
                    self.df[col] = self.df[col].astype(object)
                self.df[col] = self.df[col].where(pd.notnull(self.df[col]), None)

            return self.df

        except Exception as e:
            print("\n" + "="*50)
            print("❌ ERROR")
            print("="*50)
            print(f"{str(e)}")
            print("="*50)
            return None

    def load_data(self):
        print("\n" + "="*50)
        print("💾 CARGA BD")
        print("="*50)
        
        self.loader.table_name = self.campana_config['table']
        try:
            self.loader.upsert_into_table(self.df)
            print(f"✅ {len(self.df):,} registros")
            print("="*50)
        except Exception as e:
            print(f"❌ {str(e)[:40]}")
            print("="*50)

    def main(self):
        try:
            self.read_data()
            if self.df is not None and not self.df.empty:
                self.load_data()
                
                print("\n" + "="*50)
                print("✅ COMPLETADO")
                print("="*50)
                print(f"📊 {len(self.df):,} registros")
                print(f"📅 {datetime.now().strftime('%H:%M:%S')}")
                print("="*50 + "\n")
            else:
                print("\n" + "="*50)
                print("❌ CANCELADO")
                print("="*50 + "\n")
        except Exception as e:
            print("\n" + "="*50)
            print("❌ ERROR")
            print("="*50)
            print(f"{str(e)[:50]}")
            print("="*50 + "\n")
