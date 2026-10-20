# Evaluación de Estrategias de Autoadaptación en Microservicios Orquestados por Kubernetes

Este repositorio contiene el código fuente, la configuración de la infraestructura y los datos obtenidos del Trabajo de Integración Curricular para la carrera de Computación de la Universidad Nacional de Loja (UNL).

En este proyecto se utiliza la arquitectura de Google Online Boutique como caso de estudio para analizar cómo se comportan los sistemas distribuidos ante escenarios de estrés y picos de tráfico.

## Propósito del repositorio

El objetivo principal de este repositorio es permitir que cualquier persona pueda reproducir los experimentos de la investigación. Aquí encontrarás los recursos técnicos y los manifiestos de Kubernetes necesarios para levantar el entorno, lanzar las pruebas de carga y validar los resultados (como el tiempo de recuperación y la latencia).

## Herramientas y tecnologías

El entorno de pruebas está construido con:

- Orquestación: Kubernetes (K8s) corriendo en local con Docker Desktop y WSL2.
- Aplicación base: Google Online Boutique.
- Estrategias de autoadaptación: 
  * Metrics Server y Horizontal Pod Autoscaler (HPA) para el escalamiento.
  * NGINX Ingress Controller para limitar el tráfico (Rate Limiting / Throttling).
- Pruebas de carga: Grafana k6.
- Procesamiento de datos: Python (Pandas, NumPy y Matplotlib).

## Organización de los archivos

Las carpetas del proyecto están organizadas según las fases del experimento:

- `kubernetes-manifests/`: Archivos YAML para desplegar los microservicios originales.
- `pruebas/01_escenarios_yaml/`: Configuraciones de los escenarios evaluados (baseline, HPA, throttling) y el parche del Metrics Server.
- `pruebas/02_k6_scripts/`: Scripts de JavaScript para ejecutar las pruebas con k6.
- `pruebas/03_resultados/`: Archivos JSON y CSV con los datos en bruto generados por las pruebas.
- `pruebas/04_analisis_datos/`: Scripts de Python para limpiar los datos y generar las gráficas del documento final.

## Requisitos previos

Antes de empezar, necesitas tener instalado:

- Docker Desktop con la opción de WSL2 y Kubernetes local activada.
- `kubectl` configurado para conectarse al clúster de docker-desktop.
- Grafana k6 instalado en tu computadora.
- NGINX Ingress Controller habilitado en el clúster.

## Pasos para ejecutar las pruebas

Sigue estos pasos para replicar el entorno y ejecutar los escenarios:

### 1. Preparar el entorno base

Primero, clona el repositorio y entra a la carpeta del proyecto:

```bash
git clone https://github.com/tesaut11/tesaut1.1.git
cd tesaut1.1
```

Despliega todos los microservicios de la aplicación:

```bash
kubectl apply -f ./kubernetes-manifests
```

Para que el HPA pueda medir el consumo de CPU, aplica este parche al Metrics Server:

```bash
kubectl patch deployment metrics-server -n kube-system --type 'json' -p '[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```
*Nota: Espera alrededor de un minuto y verifica que está funcionando ejecutando `kubectl top pods`.*

### 2. Configurar el acceso (Port-forward)

Como k6 corre fuera del clúster, necesitamos crear un puente de red para poder enviarle tráfico a la aplicación. Abre una primera terminal y déjala corriendo con uno de estos dos comandos, dependiendo de lo que vayas a probar:

Para probar el Baseline o el Escenario HPA (conexión directa):
```bash
kubectl port-forward deployment/frontend 8080:8080
```

Para probar el Escenario Throttling (conexión a través del Ingress):
```bash
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80
```

---

### Prueba del Escenario 1: Escalamiento (HPA)

Asegúrate de estar usando el port-forward directo al frontend.

1. En una segunda terminal, aplica la regla del HPA:
```bash
kubectl apply -f ./pruebas/01_escenarios_yaml/s1_hpa.yaml
```

2. Pon a vigilar los pods del frontend para ver cómo se crean nuevas réplicas:
```bash
kubectl get pods -l app=frontend -w
```

3. Abre una tercera terminal y ejecuta la prueba de carga con k6:
```bash
k6 run ./pruebas/02_k6_scripts/stress-scaling.js
```

4. Al terminar, limpia la configuración:
```bash
kubectl delete -f ./pruebas/01_escenarios_yaml/s1_hpa.yaml
```

---

### Prueba del Escenario 2: Throttling

Asegúrate de estar usando el port-forward del Ingress Controller para que las reglas de NGINX surtan efecto.

1. En la segunda terminal, aplica la política de limitación:
```bash
kubectl apply -f ./pruebas/01_escenarios_yaml/s2_throttling.yaml
```

2. Pon a vigilar los pods nuevamente:
```bash
kubectl get pods -l app=frontend -w
```

3. En la tercera terminal, vuelve a lanzar el ataque. Esta vez verás que no se crean nuevos pods, pero k6 empezará a registrar errores HTTP 503 o 429:
```bash
k6 run ./pruebas/02_k6_scripts/stress-scaling.js
```

4. Limpia la configuración final:
```bash
kubectl delete -f ./pruebas/01_escenarios_yaml/s2_throttling.yaml
```