# Evaluación de Estrategias de Autoadaptación en Microservicios Orquestados por Kubernetes

[![Kubernetes](https://img.shields.io/badge/Kubernetes-v1.34-blue.svg)](https://kubernetes.io/)
[![Grafana k6](https://img.shields.io/badge/Grafana_k6-v1.5-purple.svg)](https://k6.io/)
[![Python](https://img.shields.io/badge/Python-3.13-yellow.svg)](https://www.python.org/)

Este repositorio contiene el código fuente, los archivos de configuración de infraestructura y los conjuntos de datos derivados del **Trabajo de Integración Curricular** desarrollado para la carrera de Computación de la **Universidad Nacional de Loja (UNL)**.

La investigación utiliza la arquitectura de referencia **Google Online Boutique** como caso de estudio empírico para analizar el comportamiento de sistemas distribuidos bajo escenarios de estrés volumétrico estocástico.

## 🎯 Objetivo del Repositorio

El propósito central de este espacio es garantizar la **reproducibilidad abierta** de la investigación. Aquí se proporcionan todos los recursos técnicos y manifiestos declarativos para que investigadores externos puedan instanciar el entorno experimental, inyectar las simulaciones de carga y validar el análisis cuantitativo del Tiempo Medio de Recuperación (MTTR) y la degradación de la latencia (p95).

## 🛠️ Stack Tecnológico y Entorno

El entorno de experimentación se fundamenta en las siguientes herramientas:

* **Orquestación y Contenedores:** Kubernetes (K8s) ejecutado localmente sobre Docker Desktop (con soporte WSL2).
* **Aplicación de Referencia:** Google Online Boutique (Microservices Demo).
* **Mecanismos de Autoadaptación:** 
  * *Metrics Server* y *Horizontal Pod Autoscaler (HPA)* para el escalamiento reactivo.
  * *NGINX Ingress Controller* para la limitación de carga preventiva (*Rate Limiting*).
* **Ingeniería del Caos (Inyección de Estrés):** Grafana K6.
* **Procesamiento de Datos:** Python (Pandas, NumPy y Matplotlib).

## 📂 Estructura del Proyecto

El repositorio se organiza siguiendo las fases del diseño metodológico del experimento:

* 📁 `k8s-manifests/`: Manifiestos YAML para el despliegue de los once microservicios, configuración del Metrics Server y definición de las estrategias de mitigación (HPA y Throttling).
* 📁 `k6-scripts/`: Scripts en JavaScript para K6, que incluyen la prueba de línea base y los escenarios de estrés con picos de 300 usuarios virtuales concurrentes.
* 📁 `data-analysis/`: Scripts de Python orientados a la limpieza de datos JSON/CSV exportados por K6 y la renderización de los gráficos presentados en el documento final.
* 📁 `docs/`: Documentación técnica complementaria, manuales de configuración del entorno y notas de ejecución.

## ⚙️ Prerrequisitos

Antes de ejecutar las pruebas, asegúrese de tener instalado:
* Docker Desktop con integración WSL2 habilitada.
* `kubectl` configurado para apuntar a su clúster local.
* [Grafana K6](https://k6.io/docs/get-started/installation/) instalado en su máquina anfitriona.
* NGINX Ingress Controller habilitado en su clúster.

## 🚀 Guía de Reproducción

Para replicar el entorno experimental y ejecutar los escenarios de prueba, siga este procedimiento paso a paso:

**1. Clonación del repositorio:**
```bash
git clone [https://github.com/tesaut11/tesaut1.1.git](https://github.com/tesaut11/tesaut1.1.git)
cd tesaut1.1