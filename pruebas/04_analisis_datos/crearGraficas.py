import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# ---------------------------------------------------------
# CONFIGURACIÓN ACADÉMICA DE GRÁFICAS (Estilo Tesis/Paper)
# ---------------------------------------------------------
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'sans-serif',
    'pdf.fonttype': 42,  # Fuentes vectoriales reales para LaTeX
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'legend.fontsize': 10,
    'figure.autolayout': True
})
sns.set_style("whitegrid")

# Rutas de archivos (ajustadas para ejecutarse desde 04_analisis_datos)
ruta_raw = '../03_resultados/raw/'
ruta_salida = '../03_resultados/'

# Asegurar que existe el directorio de salida
os.makedirs(ruta_salida, exist_ok=True)

print("Iniciando procesamiento de datos para gráficas SRE...")

# =========================================================
# FIGURA 5.6: THROUGHPUT EFECTIVO Y TASA DE FALLOS (BARRAS)
# =========================================================
# Usamos los valores empíricos exactos de tu Tabla 5.9 para alinear 
# perfectamente la gráfica con el texto de la memoria TIC.
escenarios = ['S0: Baseline', 'S1: HPA', 'S2: Throttling']
throughput = [17.20, 11.80, 15.00]
errores = [6.22, 0.90, 91.91]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Gráfico 1: Throughput
sns.barplot(x=escenarios, y=throughput, ax=ax1, palette=['#D9534F', '#5BC0DE', '#5CB85C'], hue=escenarios, legend=False)
ax1.set_ylabel('Throughput Efectivo (req/s)', fontweight='bold')
ax1.set_title('Rendimiento Operativo (Pico 300 VUs)')
for i, v in enumerate(throughput):
    ax1.text(i, v + 0.5, f"{v:.2f}", ha='center', fontweight='bold')

# Gráfico 2: Errores
sns.barplot(x=escenarios, y=errores, ax=ax2, palette=['#D9534F', '#5BC0DE', '#5CB85C'], hue=escenarios, legend=False)
ax2.set_ylabel('Tasa de Fallos / Rechazos (%)', fontweight='bold')
ax2.set_title('Disponibilidad y Degradación Intencional')
for i, v in enumerate(errores):
    ax2.text(i, v + 2, f"{v:.2f}%", ha='center', fontweight='bold')

plt.savefig(f"{ruta_salida}figura_5_6_throughput.pdf", format='pdf', bbox_inches='tight')
plt.close()
print("-> Figura 5.6 generada con éxito.")

# =========================================================
# FIGURA 5.7: SERIE TEMPORAL DE LATENCIA P95 VS VUs
# =========================================================
def procesar_csv(archivo):
    """Lee el CSV, extrae latencia p95 por segundo y VUs"""
    if not os.path.exists(archivo):
        return None, None
        
    df = pd.read_csv(archivo, usecols=['metric_name', 'timestamp', 'metric_value'], low_memory=False)
    
    # Normalizar el tiempo (t=0)
    tiempo_inicial = df['timestamp'].min()
    df['time_sec'] = df['timestamp'] - tiempo_inicial
    
    # Extraer latencia y agrupar por segundo para sacar el percentil 95
    df_lat = df[df['metric_name'] == 'http_req_duration']
    lat_p95 = df_lat.groupby('time_sec')['metric_value'].quantile(0.95)
    
    # Suavizado (Rolling Mean) para darle aspecto profesional y absorber micro-varianzas
    lat_p95_smooth = lat_p95.rolling(window=5, min_periods=1).mean()
    
    # Extraer VUs
    df_vus = df[df['metric_name'] == 'vus']
    vus = df_vus.groupby('time_sec')['metric_value'].max()
    
    return lat_p95_smooth, vus

# Procesar los 3 escenarios
lat_s0, vus_s0 = procesar_csv(f"{ruta_raw}resultados_S0_baseline.csv")
lat_s1, _ = procesar_csv(f"{ruta_raw}resultados_S1_hpa.csv")
lat_s2, _ = procesar_csv(f"{ruta_raw}resultados_S2_throttling.csv")

if lat_s0 is not None and lat_s1 is not None and lat_s2 is not None:
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Eje secundario para VUs
    ax2 = ax1.twinx()
    
    # Rellenos (Shading) para las fases de la prueba de k6
    ax1.axvspan(0, 60, color='gray', alpha=0.05, label='Rampa Inicial')
    ax1.axvspan(60, 120, color='gray', alpha=0.15, label='Carga Nominal')
    ax1.axvspan(120, 240, color='red', alpha=0.05, label='Pico de Estrés (300 VUs)')
    ax1.axvspan(240, 360, color='gray', alpha=0.1, label='Recuperación')

    # Línea de SLA (170 ms)
    ax1.axhline(y=170, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='SLA / Límite Estable (170 ms)')

    # Graficar latencias (Escala Logarítmica para absorber los 60,000ms del S0)
    ax1.plot(lat_s0.index, lat_s0.values, color='#D9534F', linewidth=2, label='S0: Baseline (Sin Autoadaptación)')
    ax1.plot(lat_s1.index, lat_s1.values, color='#5BC0DE', linewidth=2, label='S1: HPA (Escalamiento)')
    ax1.plot(lat_s2.index, lat_s2.values, color='#5CB85C', linewidth=2, label='S2: Throttling (Limitación)')

    # Graficar VUs en el eje secundario
    ax2.fill_between(vus_s0.index, 0, vus_s0.values, color='gray', alpha=0.2, label='Usuarios Virtuales (VUs)')
    ax2.plot(vus_s0.index, vus_s0.values, color='gray', linestyle=':', alpha=0.5)

    # Configuraciones de ejes
    ax1.set_yscale('log')
    ax1.set_xlim(0, 360)
    ax1.set_ylim(10, 100000)
    ax2.set_ylim(0, 350)

    ax1.set_xlabel('Tiempo de la Prueba (segundos)', fontweight='bold')
    ax1.set_ylabel('Latencia p95 (ms) - Escala Logarítmica', fontweight='bold')
    ax2.set_ylabel('Usuarios Virtuales Concurrentes (VUs)', fontweight='bold', color='gray')

    # Unificar leyendas
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + [lines_2[0]], labels_1 + [labels_2[0]], loc='upper left', frameon=True, shadow=True)

    plt.savefig(f"{ruta_salida}figura_5_7_serie_temporal.pdf", format='pdf', bbox_inches='tight')
    plt.close()
    print("-> Figura 5.7 (Serie Temporal de Latencia) generada con éxito.")
else:
    print("-> ADVERTENCIA: No se encontraron los archivos CSV para generar la Figura 5.7.")

# =========================================================
# FIGURA 5.8: DESCOMPOSICIÓN DEL MTTR (BARRAS APILADAS)
# =========================================================
fig, ax = plt.subplots(figsize=(10, 4))

# Datos empíricos extraídos del documento (n=3)
categorias = ['S1: HPA (Reactivo)', 'S0: Baseline (Sin Mitigación)', 'S2: Throttling (Preventivo)']
inercia_mapek = [62, 120, 0] # 120s es solo para pintar la barra infinita de S0
cold_start = [23, 0, 0]

# Pintar barras
barras_inercia = ax.barh(categorias, inercia_mapek, color=['#F0AD4E', '#D9534F', '#5CB85C'], edgecolor='black')
barras_cold = ax.barh(categorias, cold_start, left=inercia_mapek, color='#D9534F', edgecolor='black', hatch='//')

# Etiquetas personalizadas para representar los hallazgos reales
ax.text(62/2, 0, '62s\n(Inercia MAPE-K)', ha='center', va='center', color='black', fontweight='bold', fontsize=9)
ax.text(62 + 23/2, 0, '23s\n(Cold Start)', ha='center', va='center', color='white', fontweight='bold', fontsize=9)
ax.text(120/2, 1, '∞ (Colapso por agotamiento de red y recursos)', ha='center', va='center', color='white', fontweight='bold')
ax.text(2, 2, '0s (Inmunidad / Rechazo preventivo HTTP 503)', ha='left', va='center', color='black', fontweight='bold')

ax.set_xlabel('Tiempo Medio de Recuperación - MTTR (segundos)', fontweight='bold')
ax.set_title('Descomposición Estructural del MTTR por Estrategia')
ax.set_xlim(0, 120)

# Leyenda manual
from matplotlib.patches import Patch
elementos_leyenda = [
    Patch(facecolor='#F0AD4E', edgecolor='black', label='Bucle MAPE-K (Recolección de Métricas)'),
    Patch(facecolor='#D9534F', edgecolor='black', hatch='//', label='Cold Start (Descarga de imagen y Probes)')
]
ax.legend(handles=elementos_leyenda, loc='lower right', shadow=True)

plt.savefig(f"{ruta_salida}figura_5_8_mttr.pdf", format='pdf', bbox_inches='tight')
plt.close()
print("-> Figura 5.8 (Descomposición de MTTR) generada con éxito.")
print("\n¡Proceso Finalizado! Los tres archivos PDF están listos en 'pruebas/03_resultados/'.")