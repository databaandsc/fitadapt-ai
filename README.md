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

Ejecutar desde la raíz del proyecto para instalar dependencias y levantar el servidor de desarrollo de Vite:

```bash
# 1. Instalar dependencias de Node.js
npm install

# 2. Arrancar el servidor de desarrollo (con proxy a /api)
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

- **Frontend (Vue 3 + @clerk/vue):** Se integra con `clerkPlugin` en `src/main.ts`. La aplicación muestra una pantalla de inicio de sesión cuando no hay sesión (`SignInButton` en modo modal). Una vez autenticado, se muestra el `UserButton` y se puede generar la rutina.
- **Backend (FastAPI):** Middleware `ClerkAuthMiddleware` en `api/auth_middleware.py` protege las rutas `/api/*` excepto `/api/health`. Las peticiones deben incluir `Authorization: Bearer <token>` obtenido con `getToken()` desde el frontend. El endpoint `/api/me` devuelve información del usuario autenticado.
- **Variables de entorno necesarias:**
  - `VITE_CLERK_PUBLISHABLE_KEY` (frontend)
  - `CLERK_SECRET_KEY` (backend)
- **Protección:** Solo usuarios autenticados pueden acceder a la funcionalidad de generación de rutinas. Las rutas públicas son `/api/health`.


## 8. Contenerización (Docker)

*(Documentación pendiente)*

## 9. Despliegue en AWS EC2

*(Documentación pendiente)*

## 10. Operación, Verificación y Tests

El proyecto incluye un entorno de pruebas automatizadas en ambos extremos (frontend y backend) para garantizar la solidez de los esquemas de validación y el renderizado de la interfaz.

### 10.1. Ejecución en Entorno Local

Para operar la aplicación en modo desarrollo, es necesario levantar ambos servicios en terminales separadas desde la raíz del proyecto:

1. **Backend (FastAPI):**
   ```bash
   source .venv/bin/activate
   uvicorn api.index:app --reload --port 8000
   ```

2. **Frontend (Vite + Vue 3):**
   **Bash**

   ```
   npm run dev
   ```

   *(La aplicación estará disponible en `http://localhost:5173` y enrutará las peticiones `/api` al puerto 8000 mediante el proxy de Vite).*

### 10.2. Pruebas Automatizadas del Backend (Pytest)

El backend utiliza `pytest` y `TestClient` para validar la lógica y los endpoints sin necesidad de levantar el servidor.

* **Ejecución de la suite:**
  **Bash**

  ```
  pytest -v
  ```
* **Casos de prueba cubiertos:**

  * `test_health_check`: Verifica la disponibilidad de la API y el modo de ejecución actual.
  * `test_pydantic_validation`: Comprueba el rechazo de peticiones inválidas (ej. tiempo fuera de rango o equipamiento vacío) devolviendo HTTP 422.
  * `test_generate_routine_mock_success`: Evalúa el flujo completo de generación de rutinas aislando al proveedor de IA mediante `unittest.mock.patch`, comprobando la respuesta HTTP 200 y la estructura del JSON.

### 10.3. Pruebas Automatizadas del Frontend (Vitest)

El frontend emplea `vitest` junto a `@vue/test-utils` sobre un entorno emulado (`jsdom`).

* **Ejecución de pruebas de interfaz:**
  **Bash**

  ```
  npm test
  ```
* **Verificación estricta de tipado (TypeScript):** Asegura que el contrato de datos coincida con los esquemas de Pydantic sin emitir errores de compilación:
  **Bash**

  ```
  npx vue-tsc --noEmit
  ```

### 10.4. Comprobaciones Manuales y Modo Demo

Para evitar consumir la cuota (tokens) de OpenAI/Groq durante el desarrollo de la interfaz, el sistema incluye un **Modo Demo** determinista.

* Si la variable de entorno `FITADAPT_MODE=demo` (o si no se configura una API Key válida en desarrollo), el backend generará rutinas instantáneas de un catálogo local.
* **Verificaciones UI:** Al probar manualmente la SPA, se debe comprobar que el formulario se bloquea y el spinner se activa durante la petición asíncrona, y que los componentes de error renderizan correctamente ante fallos de red simulados.

## 11. Registro de Problemas y Soluciones

* **Incidencia 1:** Conflicto de entornos virtuales locales (Conda vs Venv) al ejecutar `uvicorn`.

  * **Síntoma:** Error `ModuleNotFoundError: No module named 'fastapi'`.
  * **Solución:** Forzar la ejecución de Uvicorn a través del binario de Python del entorno virtual activo mediante el comando `python -m uvicorn api.index:app --reload --port 8000`.
* **Incidencia 2:** Fallo en la generación de rutinas por retirada de modelos en el proveedor Groq.

  * **Síntoma:** El servidor devuelve `HTTP 500 Internal Server Error` y el log de FastAPI muestra `Error code: 400 - The model has been decommissioned`.
  * **Solución:** El backend manejó la excepción correctamente evitando el bloqueo. Se acudió a la consola de Groq para consultar los *Model IDs* vigentes y se actualizó la variable `AI_MODEL` en el archivo `.env` por una versión operativa (ej. `mixtral-8x7b-32768`), resolviendo la petición con éxito.

## 12. Historial de Versiones (Git y Evidencias)

* `v0.3.0` / `v0.3-vercel`: Despliegue *full-stack serverless* completado en Vercel (Fase 3). SPA Vue 3 y FastAPI unificados en un único proyecto, configuración de enrutamiento en `vercel.json`, variables de entorno protegidas y monitorización mediante Vercel CLI.
* `v0.1-backend`: Estructura base de FastAPI, modelos Pydantic y lógica de IA completada y probada.
