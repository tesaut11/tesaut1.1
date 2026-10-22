# Evaluación de Estrategias de Autoadaptación en Microservicios Orquestados por Kubernetes

Este repositorio contiene el código fuente, la configuración de la infraestructura y los datos obtenidos del Trabajo de Integración Curricular para la carrera de Computación de la Universidad Nacional de Loja (UNL).

En este proyecto se utiliza la arquitectura de Google Online Boutique como caso de estudio para analizar cómo se comportan los sistemas distribuidos ante escenarios de estrés y picos de tráfico.

## Propósito del repositorio

El objetivo principal de este repositorio es permitir que cualquier persona pueda reproducir los experimentos de la investigación. Aquí encontrarás los recursos técnicos y los manifiestos de Kubernetes necesarios para levantar el entorno, lanzar las pruebas de carga y validar los resultados (como el tiempo de recuperación y la latencia).

## Herramientas y tecnologías

El entorno de pruebas está construido con:
- **Orquestación:** Kubernetes (K8s) corriendo en local con Docker Desktop y WSL2.
- **Aplicación base:** Google Online Boutique.
- **Estrategias de autoadaptación:**
  - Metrics Server y Horizontal Pod Autoscaler (HPA) para el escalamiento.
  - NGINX Ingress Controller para limitar el tráfico (Rate Limiting / Throttling).
- **Pruebas de carga:** Grafana k6.
- **Procesamiento de datos:** Python (Pandas, NumPy y Matplotlib).

## Organización de los archivos

Las carpetas del proyecto están organizadas según las fases del experimento:
- `kubernetes-manifests/`: Archivos YAML para desplegar los microservicios originales.
- `pruebas/01_escenarios_yaml/`: Configuraciones de los escenarios evaluados (HPA, throttling) y el parche del Metrics Server.
- `pruebas/02_k6_scripts/`: Scripts de JavaScript para ejecutar las pruebas con k6.
- `pruebas/03_resultados/`: Archivos JSON y CSV con los datos en bruto generados por las pruebas.
- `pruebas/04_analisis_datos/`: Scripts de Python para limpiar los datos y generar las gráficas del documento final.

## Requisitos previos

Antes de empezar, necesitas tener instalado:
- Docker Desktop con la opción de WSL2 y Kubernetes local activada.
- `kubectl` configurado para conectarse al clúster de docker-desktop.
- Grafana k6 instalado en tu computadora.
- NGINX Ingress Controller habilitado en el clúster.

---

## Pasos para ejecutar las pruebas

Sigue estos pasos para replicar el entorno y ejecutar los escenarios de autoadaptación:

### 1. Preparar el entorno base

Primero, clona el repositorio y entra a la carpeta del proyecto:
```bash
git clone https://github.com/tesaut11/tesaut1.1.git
cd tesaut1.1
```

Despliega los microservicios de la aplicación utilizando los manifiestos de release (para descargar las imágenes precompiladas oficiales y evitar errores locales):
```bash
kubectl apply -f ./release/kubernetes-manifests.yaml
```

Elimina el generador de carga por defecto (para que k6 sea nuestra única fuente de tráfico) y asigna los límites de recursos obligatorios al frontend:
```bash
kubectl delete deployment loadgenerator --ignore-not-found
kubectl set resources deployment frontend -c server --requests=cpu=100m,memory=64Mi --limits=cpu=200m,memory=128Mi
```

Para que el HPA pueda medir el consumo de CPU, aplica este parche al Metrics Server:
```bash
kubectl patch deployment metrics-server -n kube-system --type 'json' -p '[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```
> **Nota:** Espera alrededor de un minuto y verifica que todos los pods estén en estado `Running 1/1` ejecutando `kubectl get pods`, y que el monitor funcione con `kubectl top pods`.

### 2. Configurar el acceso (Port-forward)

Como k6 corre fuera del clúster, necesitamos crear un puente de red. Abre una **terminal secundaria** y déjala corriendo con uno de estos dos comandos, dependiendo del escenario:

Para probar el **Escenario HPA** (conexión directa):
```bash
kubectl port-forward deployment/frontend 8080:8080
```

Para probar el **Escenario Throttling** (conexión a través del Ingress):
```bash
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80
```

---

### Prueba del Escenario 1: Escalamiento (HPA)

Asegúrate de usar el port-forward directo al `frontend`.

1. En tu terminal principal, aplica la regla del HPA:
```bash
kubectl apply -f ./pruebas/01_escenarios_yaml/s1_hpa.yaml
```

2. Ejecuta la prueba de carga con k6 y exporta los resultados (cópialo todo en una sola línea):
```bash
k6 run --out json=./pruebas/03_resultados/s1_it1.json --summary-export=./pruebas/03_resultados/s1_it1_summary.json ./pruebas/02_k6_scripts/stress-scaling.js
```
> **Nota:** Durante la prueba, la latencia subirá temporalmente debido al tiempo de "cold start", pero el HPA creará réplicas nuevas para estabilizar el sistema y no perder transacciones.

3. Al terminar, limpia la configuración y **restaura la réplica a 1** para no afectar futuras pruebas:
```bash
kubectl delete -f ./pruebas/01_escenarios_yaml/s1_hpa.yaml
kubectl scale deployment/frontend --replicas=1
```

---

### Prueba del Escenario 2: Throttling

Asegúrate de **cancelar el port-forward anterior** y levantar el port-forward del **Ingress Controller** para que las reglas de NGINX surtan efecto.

1. Aplica la política de limitación:
```bash
kubectl apply -f ./pruebas/01_escenarios_yaml/s2_throttling.yaml
```

2. Ejecuta la prueba de carga exportando los resultados:
```bash
k6 run --out json=./pruebas/03_resultados/s2_it1.json --summary-export=./pruebas/03_resultados/s2_it1_summary.json ./pruebas/02_k6_scripts/stress-scaling.js
```
> **Nota:** En este escenario, k6 registrará una alta tasa de rechazos intencionales (alrededor del 90% de fallos con código HTTP 503 o 429). Esto es el comportamiento esperado: el Ingress protege al clúster, manteniendo una latencia p95 muy baja y un Tiempo Medio de Recuperación (MTTR) de 0s.

3. Limpia la configuración final:
```bash
kubectl delete -f ./pruebas/01_escenarios_yaml/s2_throttling.yaml
```