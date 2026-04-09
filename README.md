# Evaluación de Estrategias de Autoadaptación en Microservicios Orquestados por Kubernetes

Este repositorio contiene el código fuente, los archivos de configuración de infraestructura y los conjuntos de datos derivados del Proyecto de Integración Curricular desarrollado por **Angel Jhonel Pesantes Romero**, estudiante de la carrera de Computación (Itinerario: Ingeniería de Software) en la Universidad Nacional de Loja (UNL).

La investigación utiliza la arquitectura de referencia **Google Online Boutique** como caso de estudio para analizar el comportamiento de sistemas distribuidos bajo escenarios de estrés.

## Objetivo del Repositorio

El propósito central de este espacio es garantizar la reproducibilidad de la investigación. Se proporcionan todos los recursos técnicos para que investigadores externos puedan instanciar el entorno experimental, ejecutar las simulaciones de carga y validar el análisis cuantitativo del Tiempo Medio de Recuperación (MTTR) y la variación de la latencia p95.

## Stack Tecnológico

El entorno de experimentación se fundamenta en las siguientes herramientas:

* **Orquestación y Gestión de Contenedores:** Kubernetes (K8s) sobre Docker Desktop.
* **Aplicación bajo estudio:** Google Online Boutique (Microservices Demo).
* **Generación de Carga e Inyección de Estrés:** K6.
* **Análisis de Datos:** Python (Pandas, NumPy y Matplotlib).

## Estructura del Proyecto

El repositorio se organiza siguiendo las fases del diseño metodológico:

* `k8s-manifests/`: Manifiestos YAML para el despliegue de los microservicios, habilitación del Metrics Server y definición de las estrategias de autoadaptación (Horizontal Pod Autoscaler y Limitación de Carga).
* `k6-scripts/`: Scripts en JavaScript para la ejecución de pruebas de rendimiento, incluyendo escenarios de validación funcional y pruebas de estrés escalables.
* `data-analysis/`: Scripts de Python orientados al procesamiento de trazas de datos en formato CSV y la generación de indicadores estadísticos.
* `docs/`: Documentación técnica complementaria, manuales de configuración y notas de campo.

## Guía de Reproducción

Para replicar el entorno experimental y ejecutar los escenarios de prueba, siga este procedimiento:

1. **Clonación del repositorio:**
   ```bash
   git clone [https://github.com/tesaut11/tesaut1.1.git](https://github.com/tesaut11/tesaut1.1.git)
   cd tesaut1.1
2. **Despliegue de infraestructura y servicios de métricas:**

   ```Bash
   kubectl apply -f k8s-manifests/metrics-fix.yaml
   kubectl apply -f k8s-manifests/k8s-tesis.yaml
   
3. **Configuración de la estrategia de autoadaptación (Ejemplo: Escalamiento Horizontal):**

   ```Bash
   kubectl apply -f k8s-manifests/hpa-frontend.yaml
   
4. **Ejecución de inyección de carga y captura de datos:**

   ```Bash
   k6 run --out csv=resultados_scaling.csv k6-scripts/stress-scaling.js
   
Autor
Angel Jhonel Pesantes Romero Carrera de Computación - Itinerario de Ingeniería de Software

Universidad Nacional de Loja (UNL)
