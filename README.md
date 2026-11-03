# FitAdapt AI · Explotación y Despliegue

Aplicación web de pantalla única (SPA) enfocada en el acondicionamiento físico personalizado mediante Inteligencia Artificial. Este repositorio contiene el código y la documentación operativa para su despliegue en arquitectura *full-stack serverless* (Vercel) y mediante contenedores (AWS EC2).

## 1. Identificación

* **Práctica:** UD1 · Explotación y despliegue de una aplicación con IA
* **Módulo:** Explotación de Servicios de Procesamiento y Analítica de Datos (ESPAD)
* **Aplicación:** FitAdapt AI (Generador de rutinas mediante LLM)
* **Integrantes del Grupo: Ricardo Fernández Chamorro | Carlos Madrid**

## 2. Plan de Documentación

Este documento está dirigido a ingenieros de sistemas, desarrolladores y evaluadores que necesiten reproducir, desplegar o diagnosticar la aplicación. Sigue un enfoque incremental ([Diátaxis](https://diataxis.fr/)): la documentación técnica se actualiza a medida que se completan los hitos de infraestructura (Vercel, Clerk, Docker, AWS). Se priorizan instrucciones reproducibles, comandos exactos y tablas de configuración.

## 3. Arquitectura del Sistema

La aplicación sigue un modelo de desacoplamiento entre cliente y servidor, unificados bajo un mismo origen en producción para evitar problemas de CORS:

* **Frontend (Cliente):** SPA construida con Vue 3, TypeScript y Tailwind CSS. Compilada a estáticos mediante Vite.
* **Backend (API):** Servicio desarrollado en Python con FastAPI. Expone endpoints REST y valida los contratos de datos (entradas y salidas) de forma estricta utilizando Pydantic v2.
* **Proveedor de IA:** El backend actúa como intermediario seguro, inyectando un *System Prompt* defensivo y comunicándose con la API de Groq/OpenAI. Las claves privadas nunca viajan al navegador del cliente.
* **Diferencia entre entornos de despliegue:**
  * **Vercel (Serverless):** El CDN de Vercel sirve `dist/` y ejecuta `api/index.py` bajo demanda mediante Vercel Functions.
  * **Docker / AWS EC2 (Contenedor único):** Un único contenedor ejecuta `uvicorn` en `0.0.0.0:8000`; FastAPI sirve tanto los endpoints `/api/*` como los archivos estáticos compilados en `dist/`.

## 4. Requisitos e Instalación Local

Para levantar el entorno de desarrollo y pruebas en local, se requiere **Node.js (18.x o superior)**, **Python (3.10 o superior)** y **Docker (24.x o superior)**.

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

Ejecutar desde la raíz del proyecto para instalar dependencias y levantar el servidor de desarrollo de Vite:

```bash
# 1. Instalar dependencias de Node.js
npm install

# 2. Arrancar el servidor de desarrollo (con proxy a /api)
npm run dev
```

## 5. Variables de Entorno

La configuración inyectada mediante variables de entorno garantiza el confinamiento de secretos. En desarrollo local, se utiliza un archivo `.env` (excluido en `.gitignore` y `.dockerignore`). La plantilla de referencia pública es `.env.example`.

| **Variable** | **Finalidad** | **Tipo** | **Ubicación / Entorno** | **Momento de uso** |
| :--- | :--- | :--- | :--- | :--- |
| `OPENAI_API_KEY` | Credencial de acceso a la API del LLM (Groq/OpenAI). | **Secreto** | `.env` / Runtime Backend (`--env-file` en Docker, Vercel Env) | Ejecución (Runtime) |
| `OPENAI_BASE_URL` | URL base para derivar el tráfico a proveedores compatibles (ej. Groq). | Pública | `.env` / Runtime Backend (`--env-file` en Docker, Vercel Env) | Ejecución (Runtime) |
| `AI_MODEL` | Nombre del modelo a instanciar (ej. `openai/gpt-oss-120b`). | Pública | `.env` / Runtime Backend (`--env-file` en Docker, Vercel Env) | Ejecución (Runtime) |
| `FITADAPT_MODE` | Modo de operación del backend (`ia` por defecto o `demo` local). | Pública | `.env` / Runtime Backend | Ejecución (Runtime) |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clave publicable de Clerk incrustada en el bundle de la SPA Vue. | Pública | `.env.local` / `--build-arg` en Docker / Vercel Env | **Compilación (Build)** |
| `CLERK_SECRET_KEY` | Clave secreta de Clerk para validación en el backend FastAPI. | **Secreto** | `.env` / Runtime Backend (`--env-file` en Docker, Vercel Env) | Ejecución (Runtime) |

## 6. Despliegue en Vercel (Fase 3 · Serverless)

La aplicación se despliega como un **único proyecto en Vercel**, unificando la SPA (Vue 3 + Vite) y el Backend (FastAPI) bajo el mismo dominio de producción para eliminar la necesidad de configurar CORS externo y reducir la latencia de red.

### 6.1. Arquitectura Serverless y Enrutamiento

* **Frontend:** Compilado a activos estáticos optimizados (`dist/`) servidos desde el CDN/Edge Network de Vercel.
* **Backend:** Empaquetado automáticamente como **Vercel Serverless Function** con runtime Python a partir del punto de entrada `api/index.py`. No requiere contenedor Docker ni procesos permanentes (`uvicorn` en bucle).
* **Límites de Ejecución:** Ajustado a `maxDuration: 15` segundos conforme a los límites del plan Hobby de Vercel para ejecuciones serverless.
* **Reglas de Enrutamiento (`vercel.json`):**
  ```json
  {
    "$schema": "https://openapi.vercel.sh/vercel.json",
    "framework": "vite",
    "rewrites": [
      { "source": "/api/:path*", "destination": "/api/index.py" }
    ],
    "functions": {
      "api/index.py": {
        "maxDuration": 15
      }
    }
  }
  ```

### 6.2. Registro de Operaciones con Vercel CLI

Se utilizó **Vercel CLI v64.x** para la vinculación, configuración de secretos, despliegue y monitorización:

| Operación | Comando ejecutado | Finalidad | Resultado / Evidencia |
| :--- | :--- | :--- | :--- |
| **Vincular proyecto** | `vercel link` | Enlazar el directorio local con el proyecto en Vercel y generar `.vercel/project.json`. | `✅ Linked to ricardos-projects-***/fitadaptai` |
| **Consultar proyecto** | `vercel project ls` | Verificar la vinculación y proyectos asociados al usuario. | Proyecto `fitadaptai` listado correctamente. |
| **Añadir variables** | `vercel env add <VAR>` | Inyectar secretos en Vercel para entornos `Production` y `Preview` de forma interactiva. | Añadidas `OPENAI_API_KEY`, `OPENAI_BASE_URL` y `AI_MODEL`. |
| **Consultar variables** | `vercel env ls` | Auditar la configuración de entornos **sin exponer los valores secretos**. | Tabla con nombres y entornos asignados (`Production, Preview`), valores ocultos. |
| **Despliegue Preview** | `vercel` | Construir el frontend y empaquetar la función serverless en un entorno de pruebas. | Generada URL de despliegue preliminar (`Ready in 48s`). |
| **Publicar Producción** | `vercel --prod` | Asignar el despliegue al alias canónico de producción. | Alias asignado: `https://fitadaptai-seven.vercel.app`. |
| **Inspeccionar despliegue** | `vercel inspect fitadaptai-seven.vercel.app` | Consultar estado, tiempos de compilación, especificaciones y lambdas creadas. | Estado `● Ready`, artefacto generado: `λ api/index (35.3MB)`. |
| **Consultar logs de runtime** | `vercel logs --deployment fitadaptai-seven.vercel.app` | Diagnosticar y verificar en vivo las invocaciones a FastAPI. | Registros HTTP de invocación (`GET /api/health 200 OK`). |

### 6.3. URLs de Despliegue y Verificación

* **Frontend (Producción):** [https://fitadaptai-seven.vercel.app](https://fitadaptai-seven.vercel.app)
* **Backend Health Check:** [https://fitadaptai-seven.vercel.app/api/health](https://fitadaptai-seven.vercel.app/api/health)
* **Petición funcional comprobada:** Generación de rutinas mediante llamada POST a `/api/generate-routine` validando la integración del frontend con el backend y el proveedor de IA.

## 7. Autenticación (Clerk)

La aplicación requiere autenticación con **Clerk** para poder utilizarla.

- **Frontend (Vue 3 + `@clerk/vue`):** Se integra con `clerkPlugin` en `src/main.ts`. La aplicación muestra una pantalla de inicio de sesión cuando no hay sesión (`SignIn`). Una vez autenticado, se muestra el `UserButton` y se puede generar la rutina.
- **Backend (FastAPI):** Middleware `ClerkAuthMiddleware` en `api/auth_middleware.py` protege las rutas `/api/*` excepto `/api/health`. Las peticiones deben incluir `Authorization: Bearer <token>` obtenido con `getToken()` desde el frontend. El endpoint `/api/me` devuelve información del usuario autenticado.
- **Variables de entorno necesarias:**
  - `VITE_CLERK_PUBLISHABLE_KEY` (frontend · pública en compilación)
  - `CLERK_SECRET_KEY` (backend · secreta en ejecución)
- **Protección:** Solo usuarios autenticados pueden acceder a la funcionalidad de generación de rutinas. Una llamada directa a `POST /api/generate-routine` sin token devuelve `HTTP 401 Unauthorized`.

## 8. Contenerización (Docker · Fase 5)

La aplicación completa se empaqueta y ejecuta en **un único contenedor Docker** mediante una construcción multi-etapa (`Dockerfile`):

1. **Etapa 1 (`frontend-builder` · `node:22-alpine`):** instala dependencias con `npm ci` y compila la SPA Vue 3 + TypeScript + Tailwind en `/app/dist`. Recibe únicamente la clave pública `VITE_CLERK_PUBLISHABLE_KEY` mediante `--build-arg` para que Vite la incorpore al bundle estático.
2. **Etapa 2 (`runtime` · `python:3.14-slim`):** instala las dependencias de `requirements.txt`, copia `api/` y los estáticos compilados `/app/dist`, crea un usuario sin privilegios (`appuser`) y expone el puerto `8000` ejecutando `uvicorn api.index:app --host 0.0.0.0 --port 8000`. FastAPI sirve tanto los endpoints `/api/*` como la SPA compilada (`dist/`).
3. **Exclusión de secretos (`.dockerignore`):** los archivos `.env`, `.env.*`, `node_modules`, `.venv` y `.git` están excluidos del contexto de construcción (`~255 KB`). Ningún secreto privado forma parte del `Dockerfile` ni de las capas de la imagen.

### 8.1. Construcción de la Imagen

```bash
docker build \
  --build-arg VITE_CLERK_PUBLISHABLE_KEY="pk_test_..." \
  -t fitadaptai:v0.5-docker .
```

### 8.2. Ejecución del Contenedor e Inyección de Secretos

Los secretos (`OPENAI_API_KEY`, `CLERK_SECRET_KEY`) se inyectan exclusivamente en tiempo de ejecución mediante `--env-file .env`, publicando el puerto `8000` del contenedor en el host:

```bash
docker run -d \
  --name fitadaptai \
  -p 8000:8000 \
  --env-file .env \
  fitadaptai:v0.5-docker
```

### 8.3. Operación, Logs, Parada y Reinicio

| Operación | Comando | Resultado verificado |
| :--- | :--- | :--- |
| **Consultar estado** | `docker ps` | Contenedor `fitadaptai` en estado `Up` (`0.0.0.0:8000->8000/tcp`). |
| **Consultar logs** | `docker logs --tail 50 fitadaptai` | Arranque de Uvicorn en `http://0.0.0.0:8000` y trazas HTTP `200 OK` / `401 Unauthorized`. |
| **Detener contenedor** | `docker stop fitadaptai` | Contenedor detenido limpiamente (`Exited (0)`). |
| **Iniciar contenedor** | `docker start fitadaptai` | Servicio restaurado conservando su configuración de red y variables. |
| **Reiniciar contenedor** | `docker restart fitadaptai` | Reinicio inmediato del proceso Uvicorn. |

### 8.4. Verificación del Contenedor Completo en Local

* **Interfaz SPA y autenticación:** accesible en `http://localhost:8000`, mostrando el flujo de inicio de sesión de Clerk y el generador de rutinas tras autenticarse.
* **Salud pública (`GET /api/health`):**
  ```bash
  curl -i http://localhost:8000/api/health
  # HTTP/1.1 200 OK -> {"status":"ok","service":"FitAdaptAI API (Python/FastAPI)","modo":"ia"}
  ```
* **Rechazo sin autenticación (`POST /api/generate-routine`):**
  ```bash
  curl -i -X POST http://localhost:8000/api/generate-routine \
    -H "Content-Type: application/json" \
    -d '{"objetivo":"hipertrofia","tiempo_minutos":45,"equipamiento":["mancuernas"],"nivel":"intermedio"}'
  # HTTP/1.1 401 Unauthorized -> {"detail":"No autorizado. Inicia sesión con Clerk."}
  ```

### 8.5. Estrategia de Construcción y Traslado a AWS EC2

Para el despliegue en **AWS EC2** (Fase 6), no se requiere un registro externo de imágenes: se clonará el repositorio público directamente en la instancia EC2 situándose en el tag versionado (`v0.5-docker` / `v1.0-aws`), se construirá la imagen localmente en la instancia con `docker build` y se ejecutará el contenedor inyectando un archivo `.env` privado en el servidor con permisos restringidos (`chmod 600 .env`) y política de reinicio `--restart unless-stopped`.

## 9. Despliegue en AWS EC2

*(Documentación correspondiente a la Fase 6)*

## 10. Operación, Verificación y Tests

El proyecto incluye un entorno de pruebas automatizadas en ambos extremos (frontend y backend) para garantizar la solidez de los esquemas de validación, la protección de rutas y el renderizado de la interfaz.

### 10.1. Ejecución en Entorno Local

Para operar la aplicación en modo desarrollo, es necesario levantar ambos servicios en terminales separadas desde la raíz del proyecto:

1. **Backend (FastAPI):**
   ```bash
   source .venv/bin/activate
   uvicorn api.index:app --reload --port 8000
   ```

2. **Frontend (Vite + Vue 3):**
   ```bash
   npm run dev
   ```
   *(La aplicación estará disponible en `http://localhost:5173` y enrutará las peticiones `/api` al puerto 8000 mediante el proxy de Vite).*

### 10.2. Pruebas Automatizadas del Backend (Pytest)

El backend utiliza `pytest` y `TestClient` para validar la lógica y los endpoints sin necesidad de levantar el servidor ni realizar llamadas de pago al proveedor de IA.

* **Ejecución de la suite:**
  ```bash
  .venv/bin/python -m pytest -v
  ```
* **Casos de prueba cubiertos (`5 passed`):**
  * `test_health_check`: Verifica la disponibilidad pública de `/api/health` (`200 OK`) y el modo de ejecución actual.
  * `test_rechazo_sin_autenticacion`: Verifica que una petición directa a `POST /api/generate-routine` sin token de Clerk sea rechazada con `HTTP 401 Unauthorized`.
  * `test_pydantic_validation_tiempo_fuera_de_rango` y `test_pydantic_validation_equipamiento_vacio`: Comprueban el rechazo de entradas inválidas devolviendo `HTTP 422`.
  * `test_generate_routine_mock_success`: Evalúa el flujo completo autenticado aislando al proveedor de IA mediante `unittest.mock.patch`, comprobando la respuesta `HTTP 200` y el contrato JSON.

### 10.3. Pruebas Automatizadas del Frontend (Vitest)

El frontend emplea `vitest` junto a `@vue/test-utils` sobre un entorno emulado (`jsdom`).

* **Ejecución de pruebas de interfaz:**
  ```bash
  npm test
  ```
* **Verificación estricta de tipado (TypeScript):**
  ```bash
  npx vue-tsc --noEmit
  ```

### 10.4. Comprobaciones Manuales y Modo Demo

Para evitar consumir la cuota (tokens) de OpenAI/Groq durante el desarrollo de la interfaz, el sistema incluye un **Modo Demo** determinista (`FITADAPT_MODE=demo`).

## 11. Registro de Problemas y Soluciones

* **Incidencia 1:** Conflicto de entornos virtuales locales (Conda vs Venv) al ejecutar `uvicorn`.
  * **Síntoma:** Error `ModuleNotFoundError: No module named 'fastapi'`.
  * **Solución:** Ejecutar Uvicorn a través del binario de Python del entorno virtual activo (`python -m uvicorn api.index:app --reload --port 8000`).
* **Incidencia 2:** Fallo en la generación de rutinas por retirada de modelos en el proveedor Groq.
  * **Síntoma:** El servidor devuelve `HTTP 502/500` y el log muestra `The model has been decommissioned`.
  * **Solución:** Se actualizaron los identificadores de modelo en la variable `AI_MODEL` en `.env` por un modelo activo compatible.
* **Incidencia 3:** Ubicación de `.dockerignore` y advertencia de BuildKit sobre `VITE_CLERK_PUBLISHABLE_KEY`.
  * **Síntoma:** Inicialmente `.dockerignore` se creó dentro de `api/.dockerignore`, por lo que Docker no filtraba el contexto de la raíz; además, BuildKit mostraba un aviso `SecretsUsedInArgOrEnv` sobre `VITE_CLERK_PUBLISHABLE_KEY`.
  * **Diagnóstico y Solución:** Se movió `.dockerignore` a la raíz del repositorio (reduciendo el contexto transferido al daemon a `254 KB` y garantizando la exclusión de `.env`). Respecto al aviso de BuildKit, se verificó que `VITE_CLERK_PUBLISHABLE_KEY` (`pk_test_...`) es una clave **pública** que Vite requiere en tiempo de compilación, mientras que las claves **secretas** (`OPENAI_API_KEY`, `CLERK_SECRET_KEY`) jamás se declaran en el `Dockerfile` y solo se inyectan en ejecución con `--env-file`.

## 12. Historial de Versiones (Git y Evidencias)

* `v0.5-docker`: Aplicación completa contenerizada en una única imagen Docker multi-etapa (Vue 3 compilado + FastAPI sirviendo estáticos y API protegida con Clerk), verificada localmente.
* `v0.4-auth`: Integración de autenticación con Clerk en frontend Vue y middleware de verificación en FastAPI.
* `v0.3.0` / `v0.3-vercel`: Despliegue *full-stack serverless* completado en Vercel (Fase 3). SPA Vue 3 y FastAPI unificados en un único proyecto, configuración de enrutamiento en `vercel.json`, variables de entorno protegidas y monitorización mediante Vercel CLI.
* `v0.1-backend`: Estructura base de FastAPI, modelos Pydantic y lógica de IA completada y probada.
