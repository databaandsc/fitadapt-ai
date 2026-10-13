# FitAdapt AI · Explotación y Despliegue

Aplicación web de pantalla única (SPA) enfocada en el acondicionamiento físico personalizado mediante Inteligencia Artificial. Este repositorio contiene el código y la documentación operativa para su despliegue en arquitectura *full-stack serverless* (Vercel) y mediante contenedores (AWS EC2).

## 1. Identificación

* **Práctica:** UD1 · Explotación y despliegue de una aplicación con IA
* **Módulo:** Explotación de Servicios de Procesamiento y Analítica de Datos (ESPAD)
* **Aplicación:** FitAdapt AI (Generador de rutinas mediante LLM)
* **Integrantes del Grupo: Ricardo Fernández Chamorro | Carlos Madrid**

## 2. Plan de Documentación

Este documento está dirigido a ingenieros de sistemas, desarrolladores y evaluadores que necesiten reproducir, desplegar o diagnosticar la aplicación. Sigue un enfoque incremental (Diátaxis): la documentación técnica se actualizará a medida que se completen los hitos de infraestructura (Vercel, Clerk, Docker, AWS). Se priorizan instrucciones reproducibles, comandos exactos y tablas de configuración.

## 3. Arquitectura del Sistema

La aplicación sigue un modelo de desacoplamiento entre cliente y servidor, unificados bajo un mismo origen en producción para evitar problemas de CORS:

* **Frontend (Cliente):** SPA construida con Vue 3, TypeScript y Tailwind CSS. Compilada a estáticos mediante Vite.
* **Backend (API):** Servicio desarrollado en Python con FastAPI. Expone endpoints REST y valida los contratos de datos (entradas y salidas) de forma estricta utilizando Pydantic v2.
* **Proveedor de IA:** El backend actúa como intermediario seguro, inyectando un *System Prompt* defensivo y comunicándose con la API de Groq/OpenAI. Las claves privadas nunca viajan al navegador del cliente.

## 4. Requisitos e Instalación Local

Para levantar el entorno de desarrollo y pruebas en local, se requiere **Node.js (18.x o superior)** y **Python (3.10 o superior)**.

### 4.1. Configuración del Backend (FastAPI)

Ejecutar desde la raíz del proyecto en una terminal:

```bash
# 1. Crear y activar el entorno virtual (macOS/Linux)
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias exactas
pip install -r requirements.txt

# 3. Arrancar el servidor de desarrollo
python -m uvicorn api.index:app --reload --port 8000
```

*El servicio de salud (*health check*) responderá en `http://127.0.0.1:8000/api/health`.*

### 4.2. Configuración del Frontend (Vue 3)

*(Pendiente de inicializar en las siguientes fases)*. Los comandos base serán:

**Bash**

```
npm install
npm run dev
```

## 5. Variables de Entorno

La configuración inyectada mediante variables de entorno garantiza el confinamiento de secretos. En desarrollo local, se utiliza un archivo `.env` (excluido en `.gitignore`). La plantilla de referencia es `.env.example`.


| **Variable**      | **Finalidad**                                                           | **Tipo**    | **Ubicación / Entorno** |
| ----------------- | ----------------------------------------------------------------------- | ----------- | ------------------------ |
| `OPENAI_API_KEY`  | Credencial de acceso a la API del LLM (Groq/OpenAI).                    | **Secreto** | `.env`/ Runtime Backend  |
| `OPENAI_BASE_URL` | URL base para derivar el tráfico a proveedores compatibles (ej. Groq). | Pública    | `.env`/ Runtime Backend  |
| `AI_MODEL`        | Nombre del modelo a instanciar (ej.`llama-3.3-70b-versatile`).          | Pública    | `.env`/ Runtime Backend  |

*(Las siguientes secciones se irán completando a medida que se superen las fases de despliegue y configuración exigidas en la práctica).*

## 6. Despliegue en Vercel

*(Documentación pendiente)*

## 7. Autenticación (Clerk)

*(Documentación pendiente )*

## 8. Contenerización (Docker)

*(Documentación pendiente)*

## 9. Despliegue en AWS EC2

*(Documentación pendiente)*

## 10. Operación, Verificación y Tests

*(Documentación pendiente - Detalle de pruebas Pytest/Vitest y comprobaciones manuales)*

## 11. Registro de Problemas y Soluciones

* **Incidencia 1:** Conflicto de entornos virtuales locales (Conda vs Venv) al ejecutar `uvicorn`.

  * **Síntoma:** Error `ModuleNotFoundError: No module named 'fastapi'`.
  * **Solución:** Forzar la ejecución de Uvicorn a través del binario de Python del entorno virtual activo mediante el comando `python -m uvicorn api.index:app --reload --port 8000`.
* **Incidencia 2:** Fallo en la generación de rutinas por retirada de modelos en el proveedor Groq.

  * **Síntoma:** El servidor devuelve `HTTP 500 Internal Server Error` y el log de FastAPI muestra `Error code: 400 - The model has been decommissioned`.
  * **Solución:** El backend manejó la excepción correctamente evitando el bloqueo. Se acudió a la consola de Groq para consultar los *Model IDs* vigentes y se actualizó la variable `AI_MODEL` en el archivo `.env` por una versión operativa (ej. `mixtral-8x7b-32768`), resolviendo la petición con éxito.

## 12. Historial de Versiones (Git y Evidencias)

* `v0.1-backend`*(En curso)*: Estructura base de FastAPI, modelos Pydantic y lógica de IA completada y probada.
