"""
Servicio de Recolección de Datos Energéticos UPB
Realiza GET requests al servidor y aplica PATCH en archivos JSON locales cada 30 segundos,
además de almacenar históricos en JSON.
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path

# ===== CONFIGURACIÓN =====
# URL base de tu servidor local para las solicitudes GET
BASE_URL = "http://10.38.32.137:5555/data"

# Lista de IDs de sensores a monitorear
SENSORES = [
    'SM_B3_RECT',
    'SM_B4_PRIM',
    'SM_B10_ARQ',
    'SM_B12_DERE',
    'SM_B15_BIBL',
    'SM_B17_POLI',
    'SM_B18_PARQ',
    'SM_B5_BACH',
    'SM_B7_CTIC',
    'SM_B7_TAC',
    'SM_B8_AA',
    'SM_B8_CPA',
    'SM_B8_LABS',
    'SM_B9_SFA1',
    'SM_B9_SFA2',
    'SM_ECOVILLA'
]

# Intervalo de actualización en segundos
INTERVALO_ACTUALIZACION = 30

# Carpetas de almacenamiento
CARPETA_DATOS_ACTUALES = './datos'
CARPETA_HISTORICO = './historico'

# Cantidad máxima de registros históricos por sensor
MAX_REGISTROS_HISTORICOS = 2880  # 24 horas a 30 segundos = 2880 registros

# ===== CREAR CARPETAS SI NO EXISTEN =====
Path(CARPETA_DATOS_ACTUALES).mkdir(parents=True, exist_ok=True)
Path(CARPETA_HISTORICO).mkdir(parents=True, exist_ok=True)

# ===== ESTADÍSTICAS =====
estadisticas = {
    'total_get_requests': 0,
    'total_local_patches': 0,
    'get_exitosos': 0,
    'get_fallidos': 0,
    'patch_exitosos': 0,
    'patch_fallidos': 0,
    'ultima_actualizacion': None
}

# ===== FUNCIONES PRINCIPALES =====

def obtener_datos_sensor(sensor_id):
    """
    Realiza GET request a un sensor específico en el servidor.
    """
    try:
        # Construir URL completa dinámicamente
        url = f"{BASE_URL}/{sensor_id}.json"
        
        headers = {
            'Accept': 'application/json',
            'fiware-service': 'openiot',
            'fiware-servicepath': '/'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            datos = response.json()
            print(f"✅ GET {sensor_id}: Datos obtenidos correctamente del servidor")
            estadisticas['get_exitosos'] += 1
            return datos
        else:
            print(f"❌ GET {sensor_id}: Error {response.status_code} al obtener datos del servidor")
            estadisticas['get_fallidos'] += 1
            return None
            
    except requests.exceptions.Timeout:
        print(f"⏱️ GET {sensor_id}: Timeout al conectar con el servidor")
        estadisticas['get_fallidos'] += 1
        return None
    except requests.exceptions.ConnectionError:
        print(f"🔌 GET {sensor_id}: Error de conexión con el servidor")
        estadisticas['get_fallidos'] += 1
        return None
    except Exception as e:
        print(f"💥 GET {sensor_id}: Error inesperado - {e}")
        estadisticas['get_fallidos'] += 1
        return None

def patch_archivo_local(sensor_id, nuevos_datos):
    """
    Simula la acción de PATCH modificando un archivo JSON local.
    Lee el archivo, actualiza los datos y lo vuelve a escribir.
    """
    id_corto = sensor_id.replace('SmartMeter_', '')
    ruta_archivo = os.path.join(CARPETA_DATOS_ACTUALES, f"{id_corto}.json")

    try:
        # Leer el archivo actual si existe, si no, inicializar un diccionario vacío
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                datos_existentes = json.load(f)
        else:
            datos_existentes = {}

        # Aplicar el "patch" actualizando los datos existentes con los nuevos
        datos_existentes.update(nuevos_datos)

        # Escribir los datos actualizados de vuelta al archivo
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos_existentes, f, indent=2, ensure_ascii=False)
        
        print(f"✅ PATCH Local {id_corto}: Archivo actualizado correctamente")
        estadisticas['patch_exitosos'] += 1
        return True
    
    except Exception as e:
        print(f"❌ PATCH Local {id_corto}: Error al modificar el archivo local - {e}")
        estadisticas['patch_fallidos'] += 1
        return False

def actualizar_historico(sensor_id, datos):
    """
    Actualiza el histórico del sensor agregando el nuevo registro.
    """
    try:
        id_corto = sensor_id.replace('SmartMeter_', '')
        ruta_historico = os.path.join(CARPETA_HISTORICO, f"{id_corto}_historico.json")
        
        if os.path.exists(ruta_historico):
            with open(ruta_historico, 'r', encoding='utf-8') as f:
                historico = json.load(f)
        else:
            historico = {
                'sensor_id': sensor_id,
                'registros': []
            }
        
        nuevo_registro = {
            'timestamp': datetime.now().isoformat(),
            'ActivePower': datos.get('ActivePower', {}).get('value', 0),
            'TotalPowerFactor': datos.get('TotalPowerFactor', {}).get('value', 0),
            'RelativeTHDVoltage': datos.get('RelativeTHDVoltage', {}).get('value', 0),
            'Frequency': datos.get('Frequency', {}).get('value', 60),
            'V1': datos.get('V1', {}).get('value', 0),
            'V2': datos.get('V2', {}).get('value', 0),
            'V3': datos.get('V3', {}).get('value', 0),
            'I1': datos.get('I1', {}).get('value', 0),
            'I2': datos.get('I2', {}).get('value', 0),
            'I3': datos.get('I3', {}).get('value', 0)
        }
        
        historico['registros'].append(nuevo_registro)
        
        if len(historico['registros']) > MAX_REGISTROS_HISTORICOS:
            historico['registros'] = historico['registros'][-MAX_REGISTROS_HISTORICOS:]
        
        with open(ruta_historico, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=2, ensure_ascii=False)
        
        print(f"📈 {id_corto}: Histórico actualizado ({len(historico['registros'])} registros)")
        
    except Exception as e:
        print(f"❌ Error actualizando histórico de {sensor_id}: {e}")

def procesar_todos_sensores():
    """
    Procesa todos los sensores: obtiene datos del servidor, aplica el "patch" en archivos locales y actualiza históricos.
    """
    print("\n" + "="*70)
    print(f"🔄 Iniciando ciclo de actualización - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    for sensor_id in SENSORES:
        estadisticas['total_get_requests'] += 1
        
        # 1. Realizar GET para obtener los datos más recientes del servidor
        datos = obtener_datos_sensor(sensor_id)
        
        if datos:
            # 2. Aplicar el "patch" a los archivos JSON locales con los datos obtenidos
            patch_archivo_local(sensor_id, datos)

            # 3. Actualizar el histórico con los nuevos datos
            actualizar_historico(sensor_id, datos)
        
        time.sleep(0.5)
    
    estadisticas['total_local_patches'] += len([s for s in SENSORES if s in SENSORES]) # Contar patches exitosos
    estadisticas['ultima_actualizacion'] = datetime.now().isoformat()
    
    print("\n" + "-"*70)
    print(f"📊 ESTADÍSTICAS:")
    print(f"   Total GET requests: {estadisticas['total_get_requests']}")
    print(f"   Total PATCH locales: {estadisticas['total_local_patches']}")
    print(f"   GET Exitosos: {estadisticas['get_exitosos']}")
    print(f"   GET Fallidos: {estadisticas['get_fallidos']}")
    print(f"   PATCH Exitosos: {estadisticas['patch_exitosos']}")
    print(f"   PATCH Fallidos: {estadisticas['patch_fallidos']}")
    print(f"   Próxima actualización: {INTERVALO_ACTUALIZACION} segundos")
    print("-"*70 + "\n")

def ejecutar_servicio():
    """
    Ejecuta el servicio de recolección de datos en loop infinito.
    """
    print("🚀 Servicio de Recolección de Datos UPB")
    print(f"📡 URL Base (GET): {BASE_URL}")
    print(f"⏱️  Intervalo: {INTERVALO_ACTUALIZACION} segundos")
    print(f"📂 Directorio de datos: {CARPETA_DATOS_ACTUALES}")
    print(f"📚 Directorio de históricos: {CARPETA_HISTORICO}")
    print(f"🔢 Sensores monitoreados: {len(SENSORES)}")
    print("\n⚠️  Presiona Ctrl+C para detener el servicio\n")
    
    try:
        while True:
            procesar_todos_sensores()
            time.sleep(INTERVALO_ACTUALIZACION)
    except KeyboardInterrupt:
        print("\n\n🛑 Servicio detenido por el usuario")
        print(f"📊 Resumen final:")
        print(f"   Total de GET requests realizados: {estadisticas['total_get_requests']}")
        print(f"   Total de PATCH locales realizados: {estadisticas['total_local_patches']}")
        print(f"   GET requests exitosos: {estadisticas['get_exitosos']}")
        print(f"   GET requests fallidos: {estadisticas['get_fallidos']}")
        print(f"   PATCH locales exitosos: {estadisticas['patch_exitosos']}")
        print(f"   PATCH locales fallidos: {estadisticas['patch_fallidos']}")
        print("\n✅ Servicio finalizado correctamente\n")

def obtener_historico_sensor(sensor_id, ultimas_horas=24):
    """
    Lee el histórico de un sensor para usar en el dashboard.
    """
    try:
        ruta_historico = os.path.join(CARPETA_HISTORICO, f"{sensor_id.replace('SmartMeter_', '')}_historico.json")
        
        if not os.path.exists(ruta_historico):
            print(f"⚠️ No existe histórico para {sensor_id}")
            return []
        
        with open(ruta_historico, 'r', encoding='utf-8') as f:
            historico = json.load(f)
        
        registros = historico.get('registros', [])
        registros_por_hora = int((ultimas_horas * 3600) / INTERVALO_ACTUALIZACION)
        
        # Retorna solo los últimos N registros, si hay suficientes
        return registros[-registros_por_hora:]
        
    except Exception as e:
        print(f"❌ Error leyendo histórico de {sensor_id}: {e}")
        return []

if __name__ == '__main__':
    ejecutar_servicio()
