# Evaluación de Estrategias de Autoadaptación en Microservicios Orquestados por Kubernetes

Este repositorio contiene el código fuente, los archivos de configuración de infraestructura y los conjuntos de datos derivados del Trabajo de Integración Curricular desarrollado para la carrera de Computación de la Universidad Nacional de Loja (UNL).

La investigación utiliza la arquitectura de referencia Google Online Boutique como caso de estudio empírico para analizar el comportamiento de sistemas distribuidos bajo escenarios de estrés volumétrico estocástico.

## 🎯 Objetivo del Repositorio

El propósito central de este espacio es garantizar la reproducibilidad abierta de la investigación. Aquí se proporcionan todos los recursos técnicos y manifiestos declarativos para que investigadores externos puedan instanciar el entorno experimental, inyectar las simulaciones de carga y validar el análisis cuantitativo del Tiempo Medio de Recuperación (MTTR) y la degradación de la latencia (p95).

## 🛠️ Stack Tecnológico y Entorno

El entorno de experimentación se fundamenta en las siguientes herramientas:

* **Orquestación y Contenedores:** Kubernetes (K8s) ejecutado localmente sobre Docker Desktop (con soporte WSL2).
* **Aplicación de Referencia:** Google Online Boutique (Microservices Demo).
* **Mecanismos de Autoadaptación:**
  * Metrics Server y Horizontal Pod Autoscaler (HPA) para el escalamiento reactivo.
* **Procesamiento de Datos:** Python (Pandas, NumPy y Matplotlib).

## 📂 Estructura del Proyecto

El repositorio se organiza siguiendo las fases del diseño metodológico del experimento, reflejando la estructura real del entorno de desarrollo:

* `📁 kubernetes-manifests/`: Manifiestos YAML originales para el despliegue de los once microservicios de la aplicación base.
* `📁 pruebas/01_escenarios_yaml/`: Definición de las estrategias de mitigación evaluadas (`s0_baseline.yaml`, `s1_hpa.yaml`, `s2_throttling.yaml`) y parches de infraestructura (`metrics-fix.yaml`).
* `📁 pruebas/02_k6_scripts/`: Scripts desarrollados en JavaScript para Grafana k6, que definen las rampas de calentamiento, carga nominal y los picos caóticos de estrés (ej. `stress-scaling.js`).
* `📁 pruebas/03_resultados/`: Conjuntos de datos empíricos en bruto (archivos JSON/CSV) exportados tras las iteraciones de prueba.
* `📁 pruebas/04_analisis_datos/`: Algoritmos en Python desarrollados para la limpieza de datos y la renderización de las gráficas vectoriales del documento final.

## ⚙️ Prerrequisitos

Antes de ejecutar las pruebas, asegúrese de tener instalado:

* Docker Desktop con integración WSL2 y el clúster de Kubernetes local habilitado.
* `kubectl` configurado para apuntar a su clúster local (docker-desktop).
* Grafana K6 instalado en su máquina anfitriona.
* NGINX Ingress Controller habilitado en su clúster.

## 🚀 Guía de Reproducción

Para replicar el entorno experimental y ejecutar los escenarios de prueba (ideal para demostraciones o validación), siga este procedimiento paso a paso:

### Paso 1: Clonación del repositorio

```bash
git clone https://github.com/tesaut11/tesaut1.1.git
cd tesaut1.1
```

### Paso 2: Despliegue de la Aplicación Base (Línea Base)

Instancie la arquitectura de microservicios de Google Online Boutique:

```bash
kubectl apply -f ./kubernetes-manifests
```

### Paso 3: Habilitación de la Telemetría (Metrics Server)

Para que el Escalamiento Horizontal (HPA) funcione, el clúster debe poder medir el consumo de CPU. Aplique el manifiesto de parche local:

```bash
kubectl patch deployment metrics-server -n kube-system --type 'json' -p '[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

*Nota: Espere unos 60 segundos y verifique que las métricas están siendo recolectadas ejecutando `kubectl top pods`.*

### Paso 4: Exposición del Servicio y Puerta de Red (Gateway/Ingress)

Dado que K6 se ejecuta en la máquina anfitriona, es necesario exponer el punto de entrada de la aplicación. Dependiendo del escenario, abra una **Terminal 1** y mantenga en ejecución uno de los siguientes comandos durante las pruebas:

**Opción A: Puente de red directo al frontend (Para Línea Base y Escenario HPA):**
```bash
kubectl port-forward deployment/frontend 8080:8080
```

**Opción B: Puerta de Red a través del Ingress Controller (Para Escenario Throttling):**
Para que las políticas de Rate Limiting surtan efecto, el tráfico debe ingresar por el NGINX Ingress Controller:
```bash
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80
```

## 🧪 Ejecución del Escenario 1: Escalamiento Horizontal (HPA)

1. Aplicar la política de autoadaptación (**Terminal 2**):

```bash
kubectl apply -f ./pruebas/01_escenarios_yaml/s1_hpa.yaml
```

Verifique la correcta asignación del umbral (Target 50% CPU):

```bash
kubectl get hpa
```

2. Monitorear el clúster en tiempo real (**Terminal 2**):
   Ejecute el siguiente comando filtrado para observar la creación dinámica de réplicas (Cold Start) del frontend ante la saturación:

```bash
kubectl get pods -l app=frontend -w
```

3. Inyectar carga sintética con Grafana k6 (**Terminal 3**):
   En una tercera terminal, dispare el ataque volumétrico (pico de 300 VUs) a través del puerto expuesto:

```bash
k6 run ./pruebas/02_k6_scripts/stress-scaling.js
```

4. Limpieza post-prueba:

```bash
kubectl delete -f ./pruebas/01_escenarios_yaml/s1_hpa.yaml
```

## 🛡️ Ejecución del Escenario 2: Limitación de Carga (Throttling)

*(Asegúrese de estar utilizando la **Opción B** en el Paso 4 para que el tráfico pase por la Puerta de Red del Ingress).*

1. Aplicar la política de protección perimetral (**Terminal 2**):

```bash
kubectl apply -f ./pruebas/01_escenarios_yaml/s2_throttling.yaml
```

2. Monitorear el clúster (**Terminal 2**):

```bash
kubectl get pods -l app=frontend -w
```

3. Inyectar carga sintética (**Terminal 3**):
   Ejecute nuevamente el script. En este escenario, Kubernetes no creará nuevos pods de frontend, pero K6 registrará el rechazo intencional del tráfico excedente (Errores HTTP 503 o 429 dependiendo de la configuración del Ingress):

```bash
  k6 run ./pruebas/02_k6_scripts/stress-scaling.js
```

4. Limpieza final:

```bash
kubectl delete -f ./pruebas/01_escenarios_yaml/s2_throttling.yaml
```