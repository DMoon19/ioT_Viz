# ioT_Viz

Visualización sencilla de datos IoT en local. Este repositorio incluye un script para obtener datos de sensores o APIs y un visor para graficarlos en tiempo real o casi en tiempo real. 

Es una visualización entendible para cualquier persona, sea ajena o bien por el contrario, conocedora del comportamiento eléctrico y/o consumo de energía que puede llegar a tener en este caso, los bloques de una universidad que cuentan con un alto tráfico de estudiantes como docentes y sistemas en continuo funcionamiento haciendo uso de la energía eléctrica para cumplir con las funciones cotidianas de la universidad.

Con ayuda de este programa se pueden llegar a tomar decisiones pertinentes respecto al como se comporten los datos y la información que nos proporcionen, se puede llegar a saber que bloques están funcionando bien en cuanto a eficiencia y cuales no, se puede llegar a saber si uno de ellos está fallando y gracias a ello acudir al bloque para tomar acción y poder ver si algún componente no se comporta como debería o si se está haciendo uso indebido de los espacios que ofrece la universidad haciendo uso de dispositivos u otras maquinas que puedan poner en riesgo un sistema eléctrico no capacitado para ello.

## Características

- Recolector de datos programable con Python `getter.py`, que guarda archivos CSV u otro formato local.
- Visor web sencillo en `app.py` para explorar series temporales y estado actual.
- Carpeta `datos/` para datos activos y `historico/` para respaldos o acumulados.
- Diseño pensado para correr en una Raspberry Pi u otro host Linux o Windows.
- Código en Python puro, sin dependencias pesadas.

## Estructura del proyecto

```
ioT_Viz/
├─ app.py            # Servidor del dashboard o visor local
├─ getter.py         # Recolector: lee sensores o API y guarda en /datos
├─ datos/            # Archivos recientes generados por el recolector
└─ historico/        # Archivos antiguos o de respaldo
```

## Requisitos

- Python 3.11 o 3.12 recomendado. Estas versiones tienen mejoras de rendimiento y soporte amplio en librerías del ecosistema.
- Sistema operativo: Linux, macOS o Windows.
- Paquetes de Python típicos para este tipo de proyecto:
  - `flask` o `streamlit` o `dash` según el visor que prefieras
  - `pandas` para leer y manipular CSV
  - `matplotlib` o `plotly` para gráficos
  - `requests` o `paho-mqtt` si tu fuente es HTTP o MQTT

> Si ya tienes un archivo `requirements.txt`, úsalo en lugar de la lista anterior.

## Instalación

Clona el repositorio y crea un entorno virtual.

```bash
git clone https://github.com/DMoon19/ioT_Viz.git
cd ioT_Viz

# Entorno virtual
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Instala dependencias mínimas sugeridas
pip install --upgrade pip
pip install pandas matplotlib flask
# Alternativas de visor: elige una
# pip install streamlit
# pip install dash plotly
```

## Configuración

Crea un archivo `.env` opcional para variables de entorno típicas.

```env
# Ejemplos
DATA_DIR=datos
HIST_DIR=historico
PORT=8000
HOST=0.0.0.0
REFRESH_SECONDS=5
```

En `getter.py` define la fuente de datos. Ejemplos comunes:
- Lectura de un endpoint HTTP y guardado periódico en CSV.
- Suscripción a un tópico MQTT y volcado a archivo.
- Lectura de un puerto serial con un microcontrolador.

## Uso

1) Inicia el recolector de datos hasta tener una cantidad deseada (se recolectan cada 30 segundos).

```bash
python getter.py
```

2) Lanza el visor. Usa la variante que tengas implementada en `app.py`.

- Si es Flask:

```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=8000 
```
o
```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=8050 
```

- Si es Streamlit:

```bash
streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```

- Si es Dash:

```bash
python app.py
```

Abre el navegador en `http://localhost:8000` o el puerto que hayas definido.

## Desarrollo

Sugerencias:
- Usa `uv` o `pipx` para entornos reproducibles.
- Agrega un `requirements.txt` o `pyproject.toml`.
- Implementa validación básica de archivos antes de graficar.
- Añade tests con `pytest` si crearás lógica de parsing o limpieza.

### Estilo

- Black para formato
- Ruff para lint
- Pre-commit para ganchos locales

```bash
pip install black ruff pre-commit
pre-commit install
```

## Despliegue rápido con Docker (opcional)

Crea un `Dockerfile` simple.

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Cambia según tus dependencias reales
RUN pip install --no-cache-dir pandas matplotlib flask

ENV DATA_DIR=datos     HIST_DIR=historico     PORT=8000     HOST=0.0.0.0     REFRESH_SECONDS=5

EXPOSE 8000
CMD ["python", "app.py"]
```

Construye e inicia el contenedor.

```bash
docker build -t iot_viz .
docker run -it --rm -p 8000:8000 -v $(pwd)/datos:/app/datos -v $(pwd)/historico:/app/historico iot_viz
```

## Roadmap sugerido

- Endpoint de salud y métricas para el visor.
- Página con estadísticas por sensor y rango de fechas.
- Exportación a CSV y Parquet con compresión.
- Integración con MQTT y autenticación opcional.
- Alertas por email o Telegram cuando una métrica supere un umbral.

### Versiones recomendadas

- Python 3.11 o 3.12 para obtener mejor rendimiento y compatibilidad.
- Pip moderno 24.x o superior.
- Si usas Streamlit: 1.36 o superior.
- Si usas Flask: 3.0 o superior.
- Si usas Dash: 2.17 o superior y Plotly 5.24 o superior.

