import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings

# Ignorar warnings visuales en consola
warnings.filterwarnings('ignore')

# ==========================================
# CONFIGURACIÓN INICIAL Y ESTILO
# ==========================================
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
plt.rcParams['font.family'] = 'serif'

file_s0 = 'resultados_S0_baseline.csv'
file_s1 = 'resultados_S1_hpa.csv'
file_s2 = 'resultados_S2_throttling.csv'

# ==========================================
# FUNCIÓN DE PREPROCESAMIENTO K6
# ==========================================
def procesar_csv_k6(filepath):
    # low_memory=False soluciona el DtypeWarning
    df = pd.read_csv(filepath, low_memory=False)
    
    # 1. Convertir el timestamp a segundos relativos (empezando desde 0)
    df['timestamp'] = pd.to_numeric(df['timestamp'])
    tiempo_minimo = df['timestamp'].min()
    df['tiempo_s'] = (df['timestamp'] - tiempo_minimo).astype(int)
    
    # 2. Extraer Usuarios Virtuales (VUs)
    df_vus = df[df['metric_name'] == 'vus'].groupby('tiempo_s')['metric_value'].max().reset_index()
    df_vus.rename(columns={'metric_value': 'vus'}, inplace=True)
    
    # 3. Extraer Latencia p95 (http_req_duration)
    df_lat = df[df['metric_name'] == 'http_req_duration'].groupby('tiempo_s')['metric_value'].quantile(0.95).reset_index()
    df_lat.rename(columns={'metric_value': 'latencia_p95_ms'}, inplace=True)
    
    # Unir ambas métricas en un solo DataFrame ordenado por tiempo
    df_final = pd.merge(df_lat, df_vus, on='tiempo_s', how='outer').sort_values('tiempo_s')
    df_final['vus'] = df_final['vus'].ffill().fillna(0)
    df_final['latencia_p95_ms'] = df_final['latencia_p95_ms'].fillna(0)
    
    return df_final

# ==========================================
# CARGA DE DATOS REALES
# ==========================================
print("Procesando archivos CSV de K6...")
try:
    df_s0 = procesar_csv_k6(file_s0)
    df_s1 = procesar_csv_k6(file_s1)
    df_s2 = procesar_csv_k6(file_s2)
    print("¡Datos procesados correctamente!")
except Exception as e:
    print(f"Error al leer los archivos: {e}")
    print("Asegúrate de que los archivos existan en el directorio.")
    exit()

# ==========================================
# GRÁFICA 1: Dinámica de Latencia vs. Carga
# ==========================================
fig1, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()

# Graficar latencias
ax1.plot(df_s0['tiempo_s'], df_s0['latencia_p95_ms'], label='S0: Baseline', color='#d62728', linewidth=2, alpha=0.9)
ax1.plot(df_s1['tiempo_s'], df_s1['latencia_p95_ms'], label='S1: HPA', color='#1f77b4', linewidth=2, alpha=0.9)
ax1.plot(df_s2['tiempo_s'], df_s2['latencia_p95_ms'], label='S2: Limitación (Throttling)', color='#2ca02c', linewidth=2, alpha=0.9)

# Graficar VUs (Usamos S0 como referencia para el perfil de carga)
ax2.fill_between(df_s0['tiempo_s'], 0, df_s0['vus'], color='gray', alpha=0.15, label='Usuarios Virtuales (VUs)')
ax2.plot(df_s0['tiempo_s'], df_s0['vus'], color='gray', linestyle='--', alpha=0.5)

# Formateo Ejes
ax1.set_yscale('log')
ax1.set_xlabel('Tiempo de la Prueba (s)')
ax1.set_ylabel('Latencia p95 (ms) - Escala Logarítmica')
ax2.set_ylabel('Usuarios Virtuales (VUs)')

ax1.set_xlim(0, 360)
ax1.set_ylim(50, 100000)
ax2.set_ylim(0, 350)

# Líneas de fases
for fase in [60, 120, 240]:
    ax1.axvline(x=fase, color='black', linestyle=':', alpha=0.5)

# Leyendas unificadas
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

plt.title('Dinámica de Recuperación: Latencia p95 frente a Picos de Tráfico Estocástico')
fig1.tight_layout()
fig1.savefig('grafica_1_serie_temporal.pdf', format='pdf', bbox_inches='tight')

# ==========================================
# GRÁFICA 2: Throughput vs Tasa de Fallos
# ==========================================
escenarios = ['S0: Baseline', 'S1: HPA', 'S2: Throttling']
throughput = [17.20, 11.80, 15.00]
fallos = [6.22, 0.90, 91.91]

fig2, ax3 = plt.subplots(figsize=(8, 5))
ax4 = ax3.twinx()
x = np.arange(len(escenarios))
width = 0.4

barras = ax3.bar(x, throughput, width, label='Throughput (req/s)', color='#4c72b0')
puntos = ax4.plot(x, fallos, color='#c44e52', marker='o', markersize=10, linewidth=2, label='Tasa de Fallos (%)')

ax3.set_ylabel('Throughput Efectivo (req/s)')
ax4.set_ylabel('Tasa de Fallos (%)')
ax3.set_xticks(x)
ax3.set_xticklabels(escenarios)
ax3.set_ylim(0, 20)
ax4.set_ylim(0, 100)

lines_3, labels_3 = ax3.get_legend_handles_labels()
lines_4, labels_4 = ax4.get_legend_handles_labels()
ax3.legend(lines_3 + lines_4, labels_3 + labels_4, loc='center right')

plt.title('Rendimiento y Disponibilidad Operativa bajo Carga Máxima (300 VUs)')
fig2.tight_layout()
fig2.savefig('grafica_2_rendimiento_fallos.pdf', format='pdf', bbox_inches='tight')

# ==========================================
# GRÁFICA 3: Descomposición del MTTR (Diagrama de Gantt)
# ==========================================
fig3, ax5 = plt.subplots(figsize=(9, 4))
categorias = ['S2: Throttling\n(Preventivo)', 'S1: HPA\n(Reactivo)', 'S0: Baseline\n(Sin Autoadaptación)']

ax5.barh('S1: HPA\n(Reactivo)', 15, color='#f28e2b', label='Bucle MAPE-K (Sincronización HPA)')
ax5.barh('S1: HPA\n(Reactivo)', 70, left=15, color='#e15759', label='Cold Start (Inicialización de Réplicas)')

ax5.barh('S0: Baseline\n(Sin Autoadaptación)', 120, color='#76b7b2', alpha=0.5)
ax5.text(60, 'S0: Baseline\n(Sin Autoadaptación)', '∞ (Agotamiento de Recursos)', ha='center', va='center', fontweight='bold')

ax5.barh('S2: Throttling\n(Preventivo)', 0.5, color='#59a14f')
ax5.text(2, 'S2: Throttling\n(Preventivo)', '0 s (Rechazo Temprano)', va='center', fontweight='bold')

ax5.set_xlabel('Tiempo Medio de Recuperación - MTTR (segundos)')
ax5.set_xlim(0, 130)
ax5.legend(loc='lower right')

plt.title('Descomposición Temporal del Costo de Recuperación (MTTR)')
fig3.tight_layout()
fig3.savefig('grafica_3_mttr_gantt.pdf', format='pdf', bbox_inches='tight')

print("Generación finalizada. Revisa los archivos PDF en tu carpeta.")