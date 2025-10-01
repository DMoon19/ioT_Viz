import dash
from dash import html, dcc, Output, Input, callback
import plotly.graph_objects as go
import json
import numpy as np
import os
import glob
from datetime import datetime

# ===== CONFIGURACIÓN DE UBICACIONES =====
ubicaciones_bloques = {
    'SM_B3_RECT': {'lat': 6.243467736814663, 'lon': -75.58954632082104, 'nombre': 'Bloque 03 - Rectoria'},
    'SM_B4_PRIM': {'lat': 6.243449072723936, 'lon': -75.58845868506315, 'nombre': 'Bloque 04 - Primaria'},
    'SM_B10_ARQ': {'lat': 6.240100188926724, 'lon': -75.5897769907676, 'nombre': 'Bloque 10 - Arquidiseño'},
    'SM_B12_DERE': {'lat': 6.243161112214128, 'lon': -75.59074392708648, 'nombre': 'Bloque 12 - Derecho'},
    'SM_B15_BIBL': {'lat': 6.242413214051972, 'lon': -75.59040596877229, 'nombre': 'Bloque 15 - Biblioteca'},
    'SM_B17_POLI': {'lat': 6.24181192187392, 'lon': -75.59048647758016, 'nombre': 'Bloque 17 - Polideportivo'},
    'SM_B18_PARQ': {'lat': 6.242081617459467, 'lon': -75.59131711957072, 'nombre': 'Bloque 18 - Parqueadero'},
    'SM_B5_BACH': {'lat': 6.2422549273955745, 'lon': -75.58828085911723, 'nombre': 'Bloque 05 - Bachillerato'},
    'SM_B7_CTIC': {'lat': 6.241906666238077, 'lon': -75.58933076643933, 'nombre': 'Bloque 07 - CTIC'},
    'SM_B7_TAC': {'lat': 6.241953236208937, 'lon': -75.58939213634756, 'nombre': 'Bloque 07 - TAC'},
    'SM_B8_AA': {'lat': 6.240980072888442, 'lon': -75.58884425260584, 'nombre': 'Bloque 08 - AA'},
    'SM_B8_CPA': {'lat': 6.2409894049830035, 'lon': -75.58940885757534, 'nombre': 'Bloque 08 - Comunicaciones'},
    'SM_B8_LABS': {'lat': 6.2412053762679, 'lon': -75.58934448456219, 'nombre': 'Bloque 08 - Labs'},
    'SM_B9_SFA1': {'lat': 6.240625503626784, 'lon': -75.58945280690212, 'nombre': 'Bloque 09 - SFA1'},
    'SM_B9_SFA2': {'lat': 6.240612838632484, 'lon': -75.58923621853498, 'nombre': 'Bloque 09 - SFA2'},
    'SM_ECOVILLA': {'lat': 6.241485389390946, 'lon': -75.58882785221495, 'nombre': 'Ecovilla'}
}


# ===== FUNCIÓN PARA CARGAR DATOS JSON =====
def cargar_datos_json():
    datos_energia = {}
    archivos_json = glob.glob("./historico/SM_*.json")

    if not archivos_json:
        print("⚠️ No se encontraron archivos en ./historico/.")
        return {}

    print(f"📂 Encontrados {len(archivos_json)} archivos JSON en ./historico/")

    for archivo in archivos_json:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)

            sensor_id = data.get("sensor_id")
            if not sensor_id or sensor_id not in ubicaciones_bloques:
                continue

            registros = data.get("registros", [])
            if not registros:
                continue

            ultimo = registros[-1]

            datos_energia[sensor_id] = {
                'ActivePower': ultimo.get('ActivePower', 0),
                'TotalPowerFactor': ultimo.get('TotalPowerFactor', 0.9),
                'RelativeTHDVoltage': ultimo.get('RelativeTHDVoltage', 2.0),
                'nombre': ubicaciones_bloques[sensor_id]['nombre'],
                'lat': ubicaciones_bloques[sensor_id]['lat'],
                'lon': ubicaciones_bloques[sensor_id]['lon'],
                'serie': registros
            }

            print(f"✅ {sensor_id}: {datos_energia[sensor_id]['ActivePower']:.1f} kW")

        except Exception as e:
            print(f"❌ Error leyendo {archivo}: {e}")

    return datos_energia


# ===== GENERAR SERIES TEMPORALES =====
def generar_datos_temporales():
    datos_temporales = {}
    for sensor_id, datos in datos_bloques.items():
        serie = datos.get('serie', [])
        if not serie:
            continue
        datos_temporales[sensor_id] = [
            {
                'timestamp': datetime.fromisoformat(p['timestamp']),
                'ActivePower': p['ActivePower'],
                'TotalPowerFactor': p['TotalPowerFactor'],
                'RelativeTHDVoltage': p['RelativeTHDVoltage']
            }
            for p in serie
        ]
    return datos_temporales


# ===== KPIS CONFIG =====
kpis_config = {
    'ActivePower': {
    'titulo': '💡 Consumo Energético',
    'colorscale': [
        [0.0, "#ffffb2"],   # Amarillo claro para valores bajos
        [0.3, "#fecc5c"],   # Amarillo oscuro
        [0.6, "#fd8d3c"],   # Naranja
        [1.0, "#e31a1c"]    # Rojo fuerte
    ],
    'unidad': 'kW'
},
    'TotalPowerFactor': {'titulo': '⚡ Eficiencia Energética', 'colorscale': 'RdYlGn', 'unidad': '%'},
    'RelativeTHDVoltage': {'titulo': '⚙️ Calidad Energética', 'colorscale': 'RdYlGn_r', 'unidad': '%'}
}

# ===== CARGA DE DATOS =====
print("🚀 Iniciando carga de datos...")
datos_bloques = cargar_datos_json()
datos_temporales = generar_datos_temporales()
print(f"✅ {len(datos_bloques)} sensores cargados con datos históricos")

# ===== DASH APP =====
app = dash.Dash(__name__)
app.layout = html.Div([
    # ===== ENCABEZADO =====
    html.Div([
        html.H1("🏫 Monitor Energético UPB",
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '5px'}),
        html.P("Sistema de monitoreo energético en tiempo real",
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '18px'})
    ], style={'marginBottom': '30px'}),

    # ===== DESCRIPCIÓN DE KPIS =====
    html.Div([
        html.H2("📖 Indicadores clave (KPI)", style={'color': '#34495e'}),
        html.P("Estos son los indicadores que puedes monitorear en tiempo real para cada edificio del campus:",
               style={'color': '#7f8c8d'}),

        html.Div([
            html.Div([
                html.H3("💡 Consumo Energético"),
                html.P("Mide la potencia activa consumida en cada edificio. "
                       "Representa el gasto de energía en kilovatios (kW).")
            ], style={'width': '30%', 'display': 'inline-block',
                      'backgroundColor': '#ecf0f1', 'padding': '15px',
                      'borderRadius': '10px', 'marginRight': '2%'}),

            html.Div([
                html.H3("⚡ Eficiencia Energética"),
                html.P("Indica el factor de potencia (%). Un valor cercano al 100% significa "
                       "que la energía se está utilizando de manera eficiente, "
                       "reduciendo pérdidas.")
            ], style={'width': '30%', 'display': 'inline-block',
                      'backgroundColor': '#ecf0f1', 'padding': '15px',
                      'borderRadius': '10px', 'marginRight': '2%'}),

            html.Div([
                html.H3("⚙️ Calidad Energética"),
                html.P("Se mide a través de la distorsión armónica total (THD). "
                       "Un menor porcentaje implica una mejor estabilidad y "
                       "menores interferencias en la red eléctrica.")
            ], style={'width': '30%', 'display': 'inline-block',
                      'backgroundColor': '#ecf0f1', 'padding': '15px',
                      'borderRadius': '10px'})
        ])
    ], style={'margin': '20px'}),

    # ===== CONTROLES =====
    html.Div([
        html.H2("🎛️ Controles de visualización", style={'color': '#34495e'}),
        html.Div([
            html.Div([
                html.Label("¿Qué quieres monitorear?", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='kpi-selector',
                    options=[
                        {'label': '💡 Consumo Energético', 'value': 'ActivePower'},
                        {'label': '⚡ Eficiencia Energética', 'value': 'TotalPowerFactor'},
                        {'label': '⚙️ Calidad Energética', 'value': 'RelativeTHDVoltage'}
                    ],
                    value='ActivePower'
                )
            ], style={'width': '55%', 'display': 'inline-block', 'paddingRight': '20px'}),

            html.Div([
                html.Label("Opciones de mapa:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                dcc.Checklist(
                    id="map-options",
                    options=[
                        {"label": " 🏢 Landmarks edificios", "value": "landmarks"},
                    ],
                    value=["heatmap"],
                    style={'fontSize': '14px'}
                )
            ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ], style={'margin': '20px', 'backgroundColor': '#f8f9fa',
                  'padding': '20px', 'borderRadius': '10px'})
    ]),

    # ===== RESULTADOS =====
    html.Div(id='resultados-simples',
             style={'margin': '20px', 'fontSize': '18px', 'fontWeight': 'bold'}),

    # ===== VISUALIZACIONES =====
    html.Div([
        html.Div([dcc.Graph(id="mapa-energia", style={'height': '650px'})],
                 style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            html.Div([
                html.H3("📈 Tendencia histórica", style={'textAlign': 'center'}),
                dcc.Graph(id="grafica-lineas", style={'height': '280px'})
            ], style={'marginBottom': '20px'}),

            html.Div([
                html.H3("📊 Promedio por intervalos", style={'textAlign': 'center'}),
                dcc.Graph(id="grafica-barras", style={'height': '300px'})
            ])
        ], style={'width': '38%', 'display': 'inline-block', 'paddingLeft': '2%', 'verticalAlign': 'top'})
    ]),

    # ===== TABLA TÉCNICA =====
    html.Details([
        html.Summary("🔧 Análisis Técnico Detallado (Para personal técnico)",
                     style={'fontSize': '18px', 'fontWeight': 'bold', 'color': '#34495e',
                            'cursor': 'pointer', 'padding': '15px', 'backgroundColor': '#ecf0f1',
                            'borderRadius': '8px', 'marginTop': '20px'}),
        html.Div(id='tabla-tecnica', style={'margin': '20px'})
    ], style={'margin': '20px'})
])


# ===== CALLBACK PRINCIPAL =====
@callback(
    [Output('mapa-energia', 'figure'),
     Output('resultados-simples', 'children'),
     Output('grafica-lineas', 'figure'),
     Output('grafica-barras', 'figure'),
     Output('tabla-tecnica', 'children')],
    [Input('kpi-selector', 'value'),
     Input('map-options', 'value')]
)
def actualizar_dashboard(kpi_seleccionado, map_options):
    config = kpis_config[kpi_seleccionado]
    sensores = list(datos_bloques.keys())

    if not sensores:
        empty_fig = go.Figure()
        return empty_fig, "⚠️ Sin datos", empty_fig, empty_fig, html.Div("Sin datos")

    lats = [datos_bloques[b]['lat'] for b in sensores]
    lons = [datos_bloques[b]['lon'] for b in sensores]
    nombres = [datos_bloques[b]['nombre'] for b in sensores]
    valores_raw = [datos_bloques[b].get(kpi_seleccionado, 0) for b in sensores]
    valores = [v * 100 if kpi_seleccionado == 'TotalPowerFactor' else v for v in valores_raw]

    min_v, max_v = min(valores), max(valores)
    span = max_v - min_v if max_v != min_v else 1.0
    sizes = [15 + 25 * ((v - min_v) / span) for v in valores]

    # ===== MAPA =====
    fig_mapa = go.Figure()
    mostrar_heatmap = 'heatmap' in map_options
    mostrar_landmarks = 'landmarks' in map_options
    mostrar_labels = 'labels' in map_options

    # Capa 1: Puntos de calor
    if mostrar_heatmap:
        fig_mapa.add_trace(go.Scattermapbox(
            lat=lats, lon=lons, mode='markers',
            marker=dict(size=sizes, color=valores, colorscale=config['colorscale'],
                        cmin=min_v, cmax=max_v, opacity=0.7, showscale=True,
                        colorbar=dict(title=f"{config['titulo']}<br>({config['unidad']})", x=1.02)),
            customdata=list(zip(nombres, valores)),
            hovertemplate="<b>%{customdata[0]}</b><br>" +
                          f"{config['titulo']}: %{{customdata[1]:.2f}} {config['unidad']}<br><extra></extra>",
            name="Calor", showlegend=False
        ))

        # Capa 2: Landmarks (marcadores de sensores fijos)
        if mostrar_landmarks:
            # Capa del borde blanco
            fig_mapa.add_trace(go.Scattermapbox(
                lat=lats, lon=lons, mode='markers',
                marker=dict(
                    size=32,  # borde más grande
                    color='white',
                    symbol='circle'
                ),
                hoverinfo='skip',  # no mostrar tooltip en el borde
                showlegend=False
            ))

            # Capa del centro rojo (pin)
            fig_mapa.add_trace(go.Scattermapbox(
                lat=lats, lon=lons, mode='markers',
                marker=dict(
                    size=22,  # más pequeño para quedar centrado
                    color='red',
                    symbol='circle'
                ),
                text=nombres,
                customdata=list(zip(nombres, valores)),
                hovertemplate="<b>%{text}</b><br>" +
                              f"{config['titulo']}: %{{customdata[1]:.2f}} {config['unidad']}<br><extra></extra>",
                name="Sensores",
                showlegend=False
            ))
    # Capa 3: Etiquetas con fondo de contraste
    if mostrar_labels:
        nombres_cortos = [n.split(' - ')[0] if ' - ' in n else n[:12] for n in nombres]
        # Sombra para contraste
        fig_mapa.add_trace(go.Scattermapbox(
            lat=[lat + 0.00002 for lat in lats],
            lon=[lon + 0.00002 for lon in lons],
            mode='text', text=nombres_cortos, textposition='top center',
            textfont=dict(size=11, color='rgba(0,0,0,0.9)', family='Arial Black'),
            hoverinfo='skip', showlegend=False
        ))
        # Texto principal blanco
        fig_mapa.add_trace(go.Scattermapbox(
            lat=lats, lon=lons, mode='text', text=nombres_cortos,
            textposition='top center',
            textfont=dict(size=11, color='white', family='Arial Black'),
            hoverinfo='skip', showlegend=False
        ))

    fig_mapa.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(zoom=16.8, center=dict(lat=float(np.mean(lats)), lon=float(np.mean(lons)))),
        margin={"r": 100, "t": 10, "l": 10, "b": 10}, height=650
    )

    # ===== GRÁFICA LÍNEAS =====
    fig_lineas = go.Figure()
    colores = ['#e74c3c', '#3498db', '#27ae60', '#f39c12', '#9b59b6']

    for idx, (sensor_id, serie) in enumerate(list(datos_temporales.items())[:5]):
        if not serie:
            continue
        timestamps = [p['timestamp'] for p in serie]
        valores_t = [p[kpi_seleccionado] * (100 if kpi_seleccionado == 'TotalPowerFactor' else 1) for p in serie]

        fig_lineas.add_trace(go.Scatter(
            x=timestamps, y=valores_t, mode='lines+markers',
            name=datos_bloques[sensor_id]['nombre'].split(' - ')[0],
            line=dict(color=colores[idx], width=2),
            marker=dict(size=4)
        ))

    fig_lineas.update_layout(
        xaxis_title="Tiempo", yaxis_title=config['unidad'],
        margin=dict(t=20, l=50, r=20, b=40),
        legend=dict(orientation="h", y=1.1, x=0),
        hovermode='x unified'
    )

    # ===== GRÁFICA BARRAS =====
    horas = {}
    for sensor_id, serie in datos_temporales.items():
        for p in serie:
            ts = p['timestamp'].replace(
                second=0 if p['timestamp'].second < 30 else 30,
                microsecond=0
            )
            valor = p[kpi_seleccionado] * (100 if kpi_seleccionado == 'TotalPowerFactor' else 1)
            horas.setdefault(ts, []).append(valor)

    horas_prom = {ts: np.mean(v) for ts, v in horas.items()}
    horas_ord = sorted(horas_prom.keys())
    valores_ord = [horas_prom[ts] for ts in horas_ord]
    x_labels = [ts.strftime("%H:%M:%S") for ts in horas_ord]

    # Colores según nivel
    colores_barras = []
    for v in valores_ord:
        if v < np.percentile(valores_ord, 33):
            colores_barras.append('#27ae60')  # Verde
        elif v < np.percentile(valores_ord, 66):
            colores_barras.append('#f39c12')  # Amarillo
        else:
            colores_barras.append('#e74c3c')  # Rojo

    fig_barras = go.Figure(go.Bar(
        x=x_labels, y=valores_ord, marker_color=colores_barras,
        hovertemplate="<b>%{x}</b><br>Promedio: %{y:.2f}<extra></extra>"
    ))
    fig_barras.update_layout(
        xaxis=dict(title="Tiempo (cada 30s)", tickangle=45),
        yaxis=dict(title=config['unidad']),
        margin=dict(t=20, l=50, r=20, b=80)
    )

    # ===== TABLA TÉCNICA =====
    datos_ord = sorted(
        [(sid, datos_bloques[sid]) for sid in sensores],
        key=lambda x: x[1].get(kpi_seleccionado, 0),
        reverse=True
    )

    tabla_rows = []
    for idx, (sensor_id, datos) in enumerate(datos_ord):
        # Color según posición
        if idx < 3:
            bg = '#d5f4e6'  # Verde para top 3
        elif idx >= len(datos_ord) - 3:
            bg = '#fdeaea'  # Rojo para bottom 3
        else:
            bg = 'white'

        tabla_rows.append(html.Tr([
            html.Td(f"#{idx + 1}", style={'padding': '10px', 'fontWeight': 'bold', 'textAlign': 'center'}),
            html.Td(datos['nombre'], style={'padding': '10px'}),
            html.Td(f"{datos.get('ActivePower', 0):.1f} kW", style={'padding': '10px', 'textAlign': 'right'}),
            html.Td(f"{datos.get('TotalPowerFactor', 0) * 100:.2f}%", style={'padding': '10px', 'textAlign': 'right'}),
            html.Td(f"{datos.get('RelativeTHDVoltage', 0):.2f}%", style={'padding': '10px', 'textAlign': 'right'})
        ], style={'backgroundColor': bg, 'borderBottom': '1px solid #ddd'}))

    tabla_tecnica = html.Div([
        html.H3("📋 Ranking de Sensores", style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.P(f"Ordenados por {config['titulo']}",
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '20px'}),
        html.Table([
            html.Thead([html.Tr([
                html.Th("Ranking", style={'padding': '15px', 'backgroundColor': '#34495e', 'color': 'white'}),
                html.Th("Sensor", style={'padding': '15px', 'backgroundColor': '#34495e', 'color': 'white'}),
                html.Th("Potencia Activa", style={'padding': '15px', 'backgroundColor': '#34495e', 'color': 'white'}),
                html.Th("Factor Potencia", style={'padding': '15px', 'backgroundColor': '#34495e', 'color': 'white'}),
                html.Th("THD Voltaje", style={'padding': '15px', 'backgroundColor': '#34495e', 'color': 'white'})
            ])]),
            html.Tbody(tabla_rows)
        ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': 'white',
                  'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'borderRadius': '8px'})
    ])

    # Mensaje de estado
    opciones_activas = []
    if mostrar_heatmap:
        opciones_activas.append("Puntos de calor")
    if mostrar_landmarks:
        opciones_activas.append("Landmarks")
    if mostrar_labels:
        opciones_activas.append("Etiquetas")

    mensaje = f"📊 Mostrando {config['titulo']} | Opciones: {', '.join(opciones_activas) if opciones_activas else 'Ninguna'}"

    return fig_mapa, mensaje, fig_lineas, fig_barras, tabla_tecnica


if __name__ == '__main__':
    print("🚀 Dashboard UPB iniciado en http://127.0.0.1:8050")
    app.run(debug=True, host='127.0.0.1', port=8050)