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
* **Autenticación (Clerk):** El frontend gestiona el inicio de sesión con Clerk y adjunta un token JWT a cada petición. El backend verifica criptográficamente la firma de ese token antes de atender cualquier ruta protegida (ver sección 7).

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

> **Nota:** el script `start.ps1` automatiza el arranque conjunto de backend y frontend, pero solo funciona en Windows (PowerShell). En macOS/Linux deben arrancarse ambos servicios manualmente en terminales separadas (ver sección 10.1).

### 4.2. Configuración del Frontend (Vue 3)

Ejecutar desde la raíz del proyecto para instalar dependencias y levantar el servidor de desarrollo de Vite:

```bash
# 1. Instalar dependencias de Node.js
npm install

# 2. Arrancar el servidor de desarrollo (con proxy a /api)
npm run dev
```

## 5. Variables de Entorno

La configuración inyectada mediante variables de entorno garantiza el confinamiento de secretos. En desarrollo local se utilizan dos archivos, ambos excluidos del control de versiones mediante `.gitignore` (regla `.env*`):

* **`.env`** → lo lee el **backend** (`load_dotenv()` en `api/index.py`).
* **`.env.local`** → lo lee el **frontend** (Vite). Solo las variables con prefijo `VITE_` se incorporan al código que se envía al navegador.

| **Variable**                 | **Finalidad**                                                                 | **Tipo**    | **Ubicación / Entorno**                |
| ---------------------------- | ----------------------------------------------------------------------------- | ----------- | -------------------------------------- |
| `OPENAI_API_KEY`             | Credencial de acceso a la API del LLM (Groq/OpenAI).                          | **Secreto** | `.env` / Runtime Backend               |
| `OPENAI_BASE_URL`            | URL base para derivar el tráfico a proveedores compatibles (ej. Groq).        | Pública     | `.env` / Runtime Backend               |
| `AI_MODEL`                   | Nombre del modelo a instanciar (ej. `llama-3.3-70b-versatile`).               | Pública     | `.env` / Runtime Backend               |
| `AI_MAX_TOKENS`              | Límite de tokens de la respuesta del modelo (opcional, por defecto `4000`).   | Pública     | `.env` / Runtime Backend               |
| `FITADAPT_MODE`              | Modo de ejecución: `ia` (por defecto) o `demo` (catálogo local, sin IA).      | Pública     | `.env` / Runtime Backend               |
| `CLERK_SECRET_KEY`           | Clave secreta de Clerk. Permite al backend obtener las claves públicas (JWKS) con las que verifica los tokens. | **Secreto** | `.env` / Runtime Backend |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clave publicable de Clerk. Inicializa el SDK en el navegador. Es pública por diseño. | Pública | `.env.local` / Build Frontend |

> ⚠️ `CLERK_SECRET_KEY` **nunca** debe llevar el prefijo `VITE_`: si lo llevara, Vite la incluiría en el JavaScript público y quedaría expuesta a cualquier visitante.

*(Las siguientes secciones se irán completando a medida que se superen las fases de despliegue y configuración exigidas en la práctica).*

## 6. Despliegue en Vercel (Fase 3 · Serverless)

La aplicación se despliega como un **único proyecto en Vercel**, unificando la SPA (Vue 3 + Vite) y el Backend (FastAPI) bajo el mismo dominio de producción para eliminar la necesidad de configurar CORS externo y reducir la latencia de red.

### 6.1. Arquitectura Serverless y Enrutamiento

* **Frontend:** Compilado a activos estáticos optimizados (`dist/`) servidos desde el CDN/Edge Network de Vercel.
* **Backend:** Empaquetado automáticamente como **Vercel Serverless Function** con runtime Python a partir del punto de entrada `api/index.py`. No requiere contenedor Docker ni procesos permanentes (`uvicorn` en bucle).
* **Límites de Ejecución:** Ajustado a `maxDuration: 15` segundos conforme a los límites del plan Hobby de Vercel para ejecuciones serverless.
* **Cabeceras de seguridad:** Todas las respuestas incluyen HSTS, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` y una `Content-Security-Policy` (CSP) restrictiva que solo autoriza el propio dominio y los dominios estrictamente necesarios para Clerk (ver sección 7.5).
* **Reglas de Enrutamiento y cabeceras (`vercel.json`):**
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
    },
    "headers": [
      {
        "source": "/(.*)",
        "headers": [
          { "key": "Strict-Transport-Security", "value": "max-age=31536000" },
          { "key": "X-Content-Type-Options", "value": "nosniff" },
          { "key": "X-Frame-Options", "value": "DENY" },
          { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
          { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" },
          { "key": "Content-Security-Policy", "value": "default-src 'self'; ... (ver sección 7.5)" }
        ]
      }
    ]
  }
  ```

### 6.2. Registro de Operaciones con Vercel CLI

Se utilizó **Vercel CLI v64.x** para la vinculación, configuración de secretos, despliegue y monitorización:

| Operación | Comando ejecutado | Finalidad | Resultado / Evidencia |
| :--- | :--- | :--- | :--- |
| **Vincular proyecto** | `vercel link` | Enlazar el directorio local con el proyecto en Vercel y generar `.vercel/project.json`. | `✅ Linked to ricardos-projects-***/fitadaptai` |
| **Consultar proyecto** | `vercel project ls` | Verificar la vinculación y proyectos asociados al usuario. | Proyecto `fitadaptai` listado correctamente. |
| **Añadir variables** | `vercel env add <VAR>` | Inyectar secretos en Vercel para entornos `Production` y `Preview` de forma interactiva. | Añadidas `OPENAI_API_KEY`, `OPENAI_BASE_URL` y `AI_MODEL`. |
| **Añadir variables de Clerk** | `vercel env add <VAR> --environment=production` | Inyectar las claves de Clerk en el entorno de producción. | Añadidas `VITE_CLERK_PUBLISHABLE_KEY` (tipo `Config`) y `CLERK_SECRET_KEY` (tipo `Secret`). |
| **Consultar variables** | `vercel env ls` | Auditar la configuración de entornos **sin exponer los valores secretos**. | Tabla con nombres y entornos asignados (`Production, Preview`), valores ocultos. |
| **Despliegue Preview** | `vercel` | Construir el frontend y empaquetar la función serverless en un entorno de pruebas. | Generada URL de despliegue preliminar (`Ready in 48s`). |
| **Publicar Producción** | `vercel --prod` | Asignar el despliegue al alias canónico de producción. | Alias asignado: `https://fitadaptai-seven.vercel.app`. |
| **Inspeccionar despliegue** | `vercel inspect fitadaptai-seven.vercel.app` | Consultar estado, tiempos de compilación, especificaciones y lambdas creadas. | Estado `● Ready`, artefacto generado: `λ api/index (35.3MB)`. |
| **Consultar logs de runtime** | `vercel logs --deployment fitadaptai-seven.vercel.app` | Diagnosticar y verificar en vivo las invocaciones a FastAPI. | Registros HTTP de invocación (`GET /api/health 200 OK`). |

> **Nota:** las variables con prefijo `VITE_` se incorporan al código **durante la compilación**. Tras añadirlas o modificarlas en Vercel es obligatorio volver a desplegar (`vercel --prod`) para que surtan efecto.

### 6.3. URLs de Despliegue y Verificación

* **Frontend (Producción):** [https://fitadaptai-seven.vercel.app](https://fitadaptai-seven.vercel.app)
* **Backend Health Check:** [https://fitadaptai-seven.vercel.app/api/health](https://fitadaptai-seven.vercel.app/api/health)
* **Petición funcional comprobada:** Generación de rutinas mediante llamada POST a `/api/generate-routine` validando la integración del frontend con el backend y el proveedor de IA.

> **Deployment Protection:** las URLs con hash de cada despliegue (`fitadaptai-<hash>-....vercel.app`) están protegidas por *Vercel Authentication*. El alias de producción `fitadaptai-seven.vercel.app` es público.

## 7. Autenticación (Clerk)

La aplicación requiere autenticación con **Clerk** para poder utilizarla. La protección se aplica en dos capas independientes: la interfaz (frontend) y la API (backend).

### 7.1. Flujo de autenticación

```mermaid
sequenceDiagram
    participant U as Usuario (navegador)
    participant C as Clerk
    participant F as Frontend (Vue)
    participant B as Backend (FastAPI)
    U->>C: Inicia sesión (email o Google)
    C-->>F: Sesión activa
    F->>C: getToken()
    C-->>F: JWT firmado (RS256)
    F->>B: POST /api/generate-routine + Authorization: Bearer JWT
    B->>C: Descarga claves públicas JWKS (solo la primera vez, luego caché)
    B->>B: Verifica firma, caducidad y usuario
    B-->>F: 200 (rutina) o 401 (no autorizado)
```

### 7.2. Frontend (Vue 3 + `@clerk/vue`)

* Se integra con `clerkPlugin` en `src/main.ts`, inicializado con `VITE_CLERK_PUBLISHABLE_KEY`.
* Cuando no hay sesión, la aplicación muestra una pantalla de inicio de sesión (`SignInButton` en modo modal). Una vez autenticado, se muestra el `UserButton` y se puede generar la rutina.
* El composable `src/composables/useApi.ts` obtiene el token con `getToken()` y lo adjunta en la cabecera `Authorization: Bearer <token>` de cada petición a la API.
* Dependencia declarada en `package.json`: `@clerk/vue`.

### 7.3. Backend (FastAPI · verificación JWT)

El middleware `ClerkAuthMiddleware` (`api/auth_middleware.py`) protege todas las rutas `/api/*` excepto las públicas (`/api/health`, `/docs`, `/openapi.json`, `/redoc`). Para cada petición protegida:

1. Exige la cabecera `Authorization: Bearer <token>`. Si falta → `401`.
2. Si el servidor no tiene `CLERK_SECRET_KEY` configurada, deniega por defecto → `401 "Falta configuración de Clerk en el servidor"`.
3. Descarga las **claves públicas (JWKS)** de la instancia de Clerk desde `https://api.clerk.com/v1/jwks`, autenticándose con `CLERK_SECRET_KEY`. Las claves se cachean, por lo que la descarga solo ocurre la primera vez.
4. **Verifica la firma** del token con la librería `PyJWT[crypto]`, restringiendo el algoritmo a `RS256` y exigiendo los campos `exp` (caducidad) y `sub` (usuario). Se tolera un desfase de reloj de 5 segundos.
5. Si el token es inválido, está alterado o ha caducado → `401 "Sesión inválida o caducada"`.
6. Solo si la verificación es correcta, guarda `user_id` y `session_id` en `request.state` y deja pasar la petición.

El endpoint `GET /api/me` devuelve el `user_id` y `session_id` del usuario autenticado y sirve para comprobar la autenticación.

> **Por qué es necesaria la verificación de firma:** el contenido de un JWT está codificado en base64, no cifrado, por lo que cualquiera puede fabricar uno con el `user_id` que quiera. Solo la firma, generada con la clave privada de Clerk, garantiza su autenticidad. Sin esta verificación la API aceptaría tokens inventados y cualquiera podría consumir la cuota del proveedor de IA.

### 7.4. Configuración

| Variable | Dónde (local) | Dónde (Vercel) | Uso |
| :--- | :--- | :--- | :--- |
| `VITE_CLERK_PUBLISHABLE_KEY` | `.env.local` | Variable de entorno (`Config`) | Frontend |
| `CLERK_SECRET_KEY` | `.env` | Variable de entorno (`Secret`) | Backend |

* Se utilizan claves de una **instancia de desarrollo** de Clerk (`pk_test_...` / `sk_test_...`), que funcionan en cualquier dominio (`localhost`, `*.vercel.app`). Las claves de producción (`pk_live_...`) quedan restringidas al dominio configurado en Clerk.
* Varios despliegues (por ejemplo, en cuentas de Vercel distintas de cada integrante) pueden compartir la misma aplicación de Clerk utilizando las mismas claves; los usuarios registrados son comunes.
* Proveedores de acceso habilitados: email + contraseña y Google.

### 7.5. Política de Seguridad de Contenido (CSP) para Clerk

Clerk carga su SDK, su interfaz y su protección anti-bots desde dominios externos, por lo que la CSP de `vercel.json` debe autorizarlos explícitamente:

| Directiva | Dominios añadidos | Motivo |
| :--- | :--- | :--- |
| `script-src` | `https://*.clerk.accounts.dev`, `https://challenges.cloudflare.com`, `https://cdn.protect.clerk.com` | SDK de Clerk, captcha de Cloudflare y script de protección anti-bots. |
| `connect-src` | `https://*.clerk.accounts.dev`, `https://clerk-telemetry.com`, `https://cdn.protect.clerk.com`, `https://*.protect.clerk.com:*` | API de Clerk, telemetría y sondas anti-bots (usan puertos no estándar, de ahí `:*`). |
| `img-src` | `https://img.clerk.com` | Avatares e iconos (ej. logo de Google). |
| `style-src` | `'unsafe-inline'` | Clerk inyecta sus estilos en tiempo de ejecución. |
| `frame-src` | `https://challenges.cloudflare.com` | Captcha de Cloudflare Turnstile. |
| `worker-src` | `'self' blob:` | Web workers internos del SDK. |

> **Importante:** con `npm run dev` Vite no aplica las cabeceras de `vercel.json`, por lo que los errores de CSP **solo se manifiestan en el despliegue**. Deben revisarse en la consola del navegador (F12) tras cada despliegue.

### 7.6. Verificación

Comprobaciones realizadas contra el backend local y contra producción (`https://fitadaptai-seven.vercel.app`):

| Prueba | Comando | Resultado esperado | Resultado obtenido |
| :--- | :--- | :--- | :--- |
| Ruta pública | `curl -i <URL>/api/health` | `200` | ✅ `200` |
| Ruta protegida sin token | `curl -i <URL>/api/me` | `401` | ✅ `401 "Inicia sesión con Clerk"` |
| Token inventado | `curl -i -H "Authorization: Bearer a.eyJzdWIiOiJmYWtlIn0.b" <URL>/api/me` | `401` | ✅ `401 "Sesión inválida o caducada"` |
| Token real con la firma alterada | — | `401` | ✅ `401 "Sesión inválida o caducada"` |
| Token real emitido por Clerk | `curl -i -H "Authorization: Bearer <JWT>" <URL>/api/me` | `200` + `user_id` | ✅ `200 {"user_id":"user_...","session_id":"sess_..."}` |
| Login en la web (email y Google) | Navegador | Acceso a la aplicación | ✅ Correcto |

Para obtener un token real manualmente, iniciar sesión en la web y ejecutar en la consola del navegador (F12):

```js
copy(await window.Clerk.session.getToken())
```

El token queda copiado en el portapapeles y caduca en unos 60 segundos. En macOS puede usarse directamente con `curl -i -H "Authorization: Bearer $(pbpaste)" <URL>/api/me`.

## 8. Contenerización (Docker)

*(Documentación pendiente)*

## 9. Despliegue en AWS EC2

*(Documentación pendiente)*

## 10. Operación, Verificación y Tests

El proyecto incluye un entorno de pruebas automatizadas en ambos extremos (frontend y backend) para garantizar la solidez de los esquemas de validación y el renderizado de la interfaz.

### 10.1. Ejecución en Entorno Local

Para operar la aplicación en modo desarrollo, es necesario configurar las variables de entorno (sección 5) y levantar ambos servicios en terminales separadas desde la raíz del proyecto:

1. **Backend (FastAPI):**
   ```bash
   source .venv/bin/activate
   python -m uvicorn api.index:app --reload --port 8000
   ```

2. **Frontend (Vite + Vue 3):**
   ```bash
   npm run dev
   ```

   *(La aplicación estará disponible en `http://127.0.0.1:5173` y enrutará las peticiones `/api` al puerto 8000 mediante el proxy de Vite).*

> **Nota:** `--reload` reinicia el backend al modificar archivos `.py`, pero **no** al modificar `.env`. Tras cambiar una variable de entorno hay que detener el servidor (`Ctrl + C`) y volver a arrancarlo.

### 10.2. Pruebas Automatizadas del Backend (Pytest)

El backend utiliza `pytest` y `TestClient` para validar la lógica y los endpoints sin necesidad de levantar el servidor.

* **Ejecución de la suite:**
  ```bash
  pytest -v
  ```
* **Casos de prueba cubiertos:**

  * `test_health_check`: Verifica la disponibilidad de la API y el modo de ejecución actual.
  * `test_pydantic_validation`: Comprueba el rechazo de peticiones inválidas (ej. tiempo fuera de rango o equipamiento vacío) devolviendo HTTP 422.
  * `test_generate_routine_mock_success`: Evalúa el flujo completo de generación de rutinas aislando al proveedor de IA mediante `unittest.mock.patch`, comprobando la respuesta HTTP 200 y la estructura del JSON.

> ⚠️ **Estado actual:** desde la incorporación de la autenticación con Clerk, las pruebas que llaman a `/api/generate-routine` envían peticiones sin token y reciben `401` en lugar de `422`/`200`. Solo `test_health_check` (ruta pública) pasa. Queda pendiente adaptar la suite simulando la verificación del token (ver incidencia 8 en la sección 11).

### 10.3. Pruebas Automatizadas del Frontend (Vitest)

El frontend emplea `vitest` junto a `@vue/test-utils` sobre un entorno emulado (`jsdom`).

* **Ejecución de pruebas de interfaz:**
  ```bash
  npm test
  ```
* **Verificación estricta de tipado (TypeScript):** Asegura que el contrato de datos coincida con los esquemas de Pydantic sin emitir errores de compilación:
  ```bash
  npx vue-tsc --noEmit
  ```

### 10.4. Comprobaciones Manuales y Modo Demo

Para evitar consumir la cuota (tokens) de OpenAI/Groq durante el desarrollo de la interfaz, el sistema incluye un **Modo Demo** determinista.

* Con la variable de entorno `FITADAPT_MODE=demo`, el backend genera rutinas instantáneas a partir de un catálogo local, sin contactar con el proveedor de IA. Si la variable no existe o tiene otro valor, se opera en modo `ia`, que requiere una `OPENAI_API_KEY` válida (sin ella, la API devuelve `500`).
* **Verificaciones UI:** Al probar manualmente la SPA, se debe comprobar que el formulario se bloquea y el spinner se activa durante la petición asíncrona, y que los componentes de error renderizan correctamente ante fallos de red simulados.

## 11. Registro de Problemas y Soluciones

* **Incidencia 1:** Conflicto de entornos virtuales locales (Conda vs Venv) al ejecutar `uvicorn`.

  * **Síntoma:** Error `ModuleNotFoundError: No module named 'fastapi'`.
  * **Solución:** Forzar la ejecución de Uvicorn a través del binario de Python del entorno virtual activo mediante el comando `python -m uvicorn api.index:app --reload --port 8000`.
* **Incidencia 2:** Fallo en la generación de rutinas por retirada de modelos en el proveedor Groq.

  * **Síntoma:** El servidor devuelve `HTTP 500 Internal Server Error` y el log de FastAPI muestra `Error code: 400 - The model has been decommissioned`.
  * **Solución:** El backend manejó la excepción correctamente evitando el bloqueo. Se acudió a la consola de Groq para consultar los *Model IDs* vigentes y se actualizó la variable `AI_MODEL` en el archivo `.env` por una versión operativa (ej. `mixtral-8x7b-32768`), resolviendo la petición con éxito.
* **Incidencia 3:** Fallo de compilación en Vercel tras integrar Clerk.

  * **Síntoma:** `vercel --prod` termina con `Error: Command "npm run build" exited with 2`. En local, `npm run build` muestra `error TS2307: Cannot find module '@clerk/vue'`.
  * **Causa:** `@clerk/vue` se había instalado en local pero no se había registrado en `package.json`/`package-lock.json`, por lo que Vercel no lo instalaba.
  * **Solución:** `npm install @clerk/vue` y commit de `package.json` y `package-lock.json`.
* **Incidencia 4:** La aplicación desplegada se queda indefinidamente en "Cargando…".

  * **Síntoma:** En producción no aparece la pantalla de login. En la consola: `Clerk: Failed to load Clerk JS, failed to load script: https://<instancia>.clerk.accounts.dev/npm/@clerk/clerk-js@6/dist/clerk.browser.js`. En local funcionaba.
  * **Causa:** La CSP de `vercel.json` solo permitía scripts y conexiones del propio dominio (`'self'`) y bloqueaba el SDK de Clerk. Vite no aplica estas cabeceras en desarrollo, por eso el fallo solo aparecía en el despliegue.
  * **Solución:** Autorizar los dominios de Clerk en la CSP (sección 7.5).
* **Incidencia 5:** Error al iniciar sesión con Google.

  * **Síntoma:** Tras volver de Google, la pantalla `/#/sso-callback` muestra `This action couldn't be completed. Please try again later or contact support if this persists.`
  * **Causa:** La protección anti-bots de Clerk necesita cargar `https://cdn.protect.clerk.com/.../bootstrap.js` y conectarse a `*.client.protect.clerk.com` en puertos no estándar (`:8443`, `:18443`, `:2082`, `:992`). La CSP lo bloqueaba (`Refused to connect because it violates the document's Content Security Policy`).
  * **Solución:** Añadir `https://cdn.protect.clerk.com` a `script-src` y `connect-src`, y `https://*.protect.clerk.com:*` (cualquier puerto) a `connect-src`.
* **Incidencia 6:** La API aceptaba tokens inventados.

  * **Síntoma:** `curl -H "Authorization: Bearer a.eyJzdWIiOiJmYWtlIn0.b" <URL>/api/me` devolvía `200 {"user_id":"fake"}`.
  * **Causa:** El middleware solo decodificaba el contenido del JWT (base64) sin verificar su firma; `CLERK_SECRET_KEY` se leía pero no se utilizaba. Se había simplificado así porque la versión anterior dependía del SDK `clerk_backend_api`, que no estaba en `requirements.txt`.
  * **Solución:** Verificación de la firma con `PyJWT[crypto]` y las claves públicas JWKS de Clerk (sección 7.3).
* **Incidencia 7:** Los tokens reales eran rechazados tras implementar la verificación.

  * **Síntoma:** Con un token válido emitido por Clerk, la API devolvía `401 "No se pudo validar la sesión con Clerk"`.
  * **Causa:** `PyJWKClient` descarga las claves con `urllib`, que se identifica como `User-Agent: Python-urllib/3.x`. El cortafuegos de la API de Clerk bloquea ese agente con `403 Forbidden`.
  * **Solución:** Enviar una cabecera `User-Agent` propia (`fitadaptai-backend`) en las peticiones a JWKS.
* **Incidencia 8 (pendiente):** Suite de Pytest desactualizada respecto a la autenticación.

  * **Síntoma:** `pytest` → `3 failed, 1 passed`; las pruebas reciben `401` en lugar de `422`/`200`.
  * **Causa:** Las pruebas llaman a rutas protegidas sin token.
  * **Solución propuesta:** Simular (*mock*) la verificación del token en las pruebas o enviar un token de prueba.
* **Incidencia 9:** El backend local respondía `401 "Falta configuración de Clerk en el servidor"`.

  * **Causa:** `CLERK_SECRET_KEY` se había añadido a `.env.local`, que solo lee Vite; el backend únicamente carga `.env`.
  * **Solución:** Mover la variable a `.env` y reiniciar `uvicorn` (`--reload` no detecta cambios en `.env`).

## 12. Historial de Versiones (Git y Evidencias)

* `v0.4-clerk`: Autenticación con Clerk operativa en producción. Dependencia `@clerk/vue` registrada, CSP adaptada a Clerk (SDK, login con Google y protección anti-bots) y verificación criptográfica de la firma JWT en el backend con `PyJWT`.
* `v0.3.0` / `v0.3-vercel`: Despliegue *full-stack serverless* completado en Vercel (Fase 3). SPA Vue 3 y FastAPI unificados en un único proyecto, configuración de enrutamiento en `vercel.json`, variables de entorno protegidas y monitorización mediante Vercel CLI.
* `v0.1-backend`: Estructura base de FastAPI, modelos Pydantic y lógica de IA completada y probada.
