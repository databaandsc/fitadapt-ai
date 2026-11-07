# FitAdapt AI · Explotación y Despliegue

Aplicación web de pantalla única (SPA) enfocada en el acondicionamiento físico personalizado mediante Inteligencia Artificial. Este repositorio contiene el código y la documentación operativa para su despliegue en arquitectura *full-stack serverless* (Vercel) y mediante contenedores (AWS EC2).

## 1. Identificación

* **Práctica:** UD1 · Explotación y despliegue de una aplicación con IA
* **Módulo:** Explotación de Servicios de Procesamiento y Analítica de Datos (ESPAD)
* **Aplicación:** FitAdapt AI (Generador de rutinas mediante LLM)
* **Integrantes del Grupo: Ricardo Fernández Chamorro | Carlos Madrid**

## 2. Plan de Documentación

Este documento está dirigido a ingenieros de sistemas, desarrolladores y evaluadores que necesiten reproducir, desplegar o diagnosticar la aplicación. Sigue un enfoque incremental ([Diátaxis](https://diataxis.fr/)): la documentación técnica se actualizará a medida que se completen los hitos de infraestructura (Vercel, Clerk, Docker, AWS). Se priorizan instrucciones reproducibles, comandos exactos y tablas de configuración.

## 3. Arquitectura del Sistema

La aplicación sigue un modelo de desacoplamiento entre cliente y servidor, unificados bajo un mismo origen en producción para evitar problemas de CORS:

* **Frontend (Cliente):** SPA construida con Vue 3, TypeScript y Tailwind CSS. Compilada a estáticos mediante Vite.
* **Backend (API):** Servicio desarrollado en Python con FastAPI. Expone endpoints REST y valida los contratos de datos (entradas y salidas) de forma estricta utilizando Pydantic v2.
* **Proveedor de IA:** El backend actúa como intermediario seguro, inyectando un *System Prompt* defensivo y comunicándose con la API de Groq/OpenAI. Las claves privadas nunca viajan al navegador del cliente.
* **Autenticación (Clerk):** El frontend gestiona el inicio de sesión con Clerk y adjunta un token JWT a cada petición. El backend verifica criptográficamente la firma de ese token antes de atender cualquier ruta protegida (ver sección 7).
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

La configuración inyectada mediante variables de entorno garantiza el confinamiento de secretos. En desarrollo local se utilizan dos archivos, ambos excluidos del control de versiones mediante `.gitignore` y `.dockerignore` (con `.env.example` como plantilla pública de referencia):

* **`.env`** → lo lee el **backend** (`load_dotenv()` en `api/index.py` o `--env-file` en Docker).
* **`.env.local`** → lo lee el **frontend** (Vite). Solo las variables con prefijo `VITE_` se incorporan al código que se envía al navegador.

| **Variable**                 | **Finalidad**                                                                 | **Tipo**    | **Ubicación / Entorno**                              | **Momento de uso**      |
| ---------------------------- | ----------------------------------------------------------------------------- | ----------- | ---------------------------------------------------- | ----------------------- |
| `OPENAI_API_KEY`             | Credencial de acceso a la API del LLM (Groq/OpenAI).                          | **Secreto** | `.env` / `--env-file` en Docker / Vercel Env         | Ejecución (Runtime)     |
| `OPENAI_BASE_URL`            | URL base para derivar el tráfico a proveedores compatibles (ej. Groq).        | Pública     | `.env` / `--env-file` en Docker / Vercel Env         | Ejecución (Runtime)     |
| `AI_MODEL`                   | Nombre del modelo a instanciar (ej. `openai/gpt-oss-120b`).                   | Pública     | `.env` / `--env-file` en Docker / Vercel Env         | Ejecución (Runtime)     |
| `AI_MAX_TOKENS`              | Límite de tokens de la respuesta del modelo (opcional, por defecto `4000`).   | Pública     | `.env` / `--env-file` en Docker / Vercel Env         | Ejecución (Runtime)     |
| `FITADAPT_MODE`              | Modo de ejecución: `ia` (por defecto) o `demo` (catálogo local, sin IA).      | Pública     | `.env` / `--env-file` en Docker / Vercel Env         | Ejecución (Runtime)     |
| `CLERK_SECRET_KEY`           | Clave secreta de Clerk. Permite al backend obtener las claves públicas (JWKS) con las que verifica los tokens. | **Secreto** | `.env` / `--env-file` en Docker / Vercel Env | Ejecución (Runtime) |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clave publicable de Clerk. Inicializa el SDK en el navegador. Es pública por diseño. | Pública | `.env.local` / `--build-arg` en Docker / Vercel Env | **Compilación (Build)** |

> ⚠️ `CLERK_SECRET_KEY` **nunca** debe llevar el prefijo `VITE_`: si lo llevara, Vite la incluiría en el JavaScript público y quedaría expuesta a cualquier visitante.

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
* Cuando no hay sesión, la aplicación muestra una pantalla de inicio de sesión (`SignIn`). Una vez autenticado, se muestra el `UserButton` y se puede generar la rutina.
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

| Variable | Dónde (local) | Dónde (Vercel) | Dónde (Docker / EC2) | Uso |
| :--- | :--- | :--- | :--- | :--- |
| `VITE_CLERK_PUBLISHABLE_KEY` | `.env.local` | Variable de entorno (`Config`) | `--build-arg` al construir imagen | Frontend (Build) |
| `CLERK_SECRET_KEY` | `.env` | Variable de entorno (`Secret`) | `--env-file .env` al ejecutar | Backend (Runtime) |

* Se utilizan claves de una **instancia de desarrollo** de Clerk (`pk_test_...` / `sk_test_...`), que funcionan en cualquier dominio (`localhost`, `*.vercel.app`, IP pública de EC2). Las claves de producción (`pk_live_...`) quedan restringidas al dominio configurado en Clerk.
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

## 8. Contenerización (Docker · Fase 5)

La aplicación completa se empaqueta y ejecuta en **un único contenedor Docker** mediante una construcción multi-etapa (`Dockerfile`):

1. **Etapa 1 (`frontend-builder` · `node:22-alpine`):** instala dependencias con `npm ci` y compila la SPA Vue 3 + TypeScript + Tailwind en `/app/dist`. Recibe únicamente la clave pública `VITE_CLERK_PUBLISHABLE_KEY` mediante `--build-arg` para que Vite la incorpore al bundle estático.
2. **Etapa 2 (`runtime` · `python:3.14-slim`):** instala las dependencias de `requirements.txt` (incluyendo `PyJWT[crypto]` para la verificación de firma de Clerk), copia `api/` y los estáticos compilados `/app/dist`, crea un usuario sin privilegios (`appuser`) y expone el puerto `8000` ejecutando `uvicorn api.index:app --host 0.0.0.0 --port 8000`. FastAPI sirve tanto los endpoints `/api/*` como la SPA compilada (`dist/`).
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

## 9. Despliegue en AWS EC2 (AWS Academy Learner Lab)

Esta fase despliega la aplicación completa en **una única instancia EC2** que ejecuta el contenedor Docker descrito en la sección 8. FastAPI sirve en el mismo origen tanto la API (`/api/*`) como la SPA compilada (`dist/`), por lo que no se necesita configurar CORS ni un segundo servicio.

### 9.1. Decisiones de arquitectura para el laboratorio

El entorno de AWS Academy Learner Lab impone restricciones que condicionan el diseño:

| Restricción del laboratorio | Decisión adoptada |
| :--- | :--- |
| Credenciales temporales que caducan al terminar la sesión | No se usa ECR: la imagen se construye dentro de la propia instancia a partir del repositorio público. |
| ECS, ECR, Elastic Beanstalk, App Runner y balanceadores no disponibles o restringidos | Se descarta la orquestación gestionada; un único contenedor en EC2 es suficiente. |
| Presupuesto de laboratorio limitado | Instancia `t3.small` y volumen gp3 de 16 GiB; la instancia se detiene al terminar cada práctica. |
| Recursos efímeros si el profesor reinicia el laboratorio | Todo el despliegue es reproducible con este documento, el repositorio y el archivo `.env`. |
| Sin dominio propio ni certificado gestionado | Se publica por HTTP en el puerto 80. Las claves de **desarrollo** de Clerk (`pk_test_` / `sk_test_`) funcionan sobre una IP pública. |
| Región fijada por el laboratorio | Todos los recursos se crean en la misma región (habitualmente `us-east-1`). |

> **Limitación conocida:** al no haber HTTPS, el navegador mostrará el aviso de conexión no segura. Es aceptable para la práctica porque Clerk se usa en modo desarrollo. Con un dominio propio se podría añadir un proxy inverso (por ejemplo, Caddy) para obtener TLS automático.

### 9.2. Recursos aprovisionados

| Recurso | Especificación | Finalidad |
| :--- | :--- | :--- |
| Instancia EC2 | `t3.small` (2 vCPU, 2 GiB RAM), Amazon Linux 2023 o Ubuntu 24.04 | Ejecutar el contenedor. |
| Volumen EBS | 16 GiB gp3 | Sistema operativo, Docker e imagen. |
| Par de claves | `fitadaptai-key.pem` | Acceso SSH. |
| Security Group | `fitadaptai-sg` | Puertos 22 y 80. |
| IP pública | Auto-asignada por el laboratorio | URL de acceso. |
| Docker Engine | Última versión del repositorio de la distribución | Construcción y ejecución del contenedor. |

Reglas de entrada del Security Group:

| Puerto | Protocolo | Origen | Motivo |
| :--- | :--- | :--- | :--- |
| `22` | TCP | *Mi IP* (recomendado) | Administración por SSH. |
| `80` | TCP | `0.0.0.0/0` | Acceso público a la aplicación. |

El tráfico de salida permanece abierto (regla por defecto): la instancia necesita contactar con `api.groq.com` (proveedor de IA) y `api.clerk.com` (claves JWKS de autenticación).

### 9.3. Pre-flight local

Antes de crear recursos en AWS, se valida el repositorio en local para no descubrir fallos durante la construcción en la instancia:

```bash
npm ci                     # debe resolver el lockfile sin errores
npm run build              # vue-tsc + vite build
.venv/bin/python -m pytest -v
docker build --build-arg VITE_CLERK_PUBLISHABLE_KEY="pk_test_..." -t fitadaptai:preflight .
```

Resultados obtenidos en la validación local:

| Comprobación | Resultado |
| :--- | :--- |
| `npm ci` | ✅ Sin conflictos entre `package.json` y `package-lock.json`. |
| `npm run build` | ✅ `dist/` generado (JS ≈ 120 kB, CSS ≈ 13 kB). |
| `pytest` | ✅ 5 pruebas superadas, cobertura 51 %. |
| `docker build` | ✅ Imagen construida correctamente. |
| Contenedor local (`/api/health`, `/api/me`, `/`) | ✅ `200`, `401`, `200` respectivamente. |
| `npm test` (Vitest) | ⚠️ Suite desactualizada respecto a la UI actual (busca `<form>` y atributos `aria-*` que ya no existen). No afecta al build ni al despliegue. |

### 9.4. Aprovisionamiento en el Learner Lab

1. Pulsar **Start Lab** y esperar a que el indicador esté en verde.
2. Seleccionar la región del laboratorio (normalmente **N. Virginia, `us-east-1`**).
3. En **EC2 → Key Pairs**, crear `fitadaptai-key` y descargar el archivo `.pem`.
4. En **EC2 → Launch instance**:
   * Nombre: `fitadaptai`
   * AMI: **Amazon Linux 2023** (alternativa: Ubuntu Server 24.04 LTS)
   * Tipo: **t3.small**
   * Key pair: `fitadaptai-key`
   * Red: VPC por defecto, subred pública y **Auto-assign public IP: Enable**
   * Security Group: crear `fitadaptai-sg` con las reglas de la sección 9.2
   * Almacenamiento: **16 GiB gp3**
5. Anotar la **IP pública** de la instancia.

### 9.5. Preparación del host

Proteger la clave privada y conectar:

```bash
chmod 400 fitadaptai-key.pem
ssh -i fitadaptai-key.pem ec2-user@IP_PUBLICA
```

Instalar Docker según la distribución:

```bash
# Amazon Linux 2023
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
newgrp docker

# Ubuntu 24.04
sudo apt-get update
sudo apt-get install -y docker.io git
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
newgrp docker
```

Verificar:

```bash
docker --version
sudo systemctl is-enabled docker   # enabled
```

### 9.6. Despliegue de la aplicación

**1. Clonar el repositorio** (público, sin credenciales):

```bash
git clone https://github.com/databaandsc/fitadapt-ai.git
cd fitadapt-ai
git checkout main          # en despliegues posteriores: git checkout v1.0-aws
git rev-parse --short HEAD # anotar el commit desplegado
```

**2. Crear el archivo `.env`** con los secretos. Se recomienda copiarlo desde el equipo local para no dejarlo en el historial de la shell:

```bash
# En el equipo local, desde la raíz del proyecto:
scp -i fitadaptai-key.pem .env ec2-user@IP_PUBLICA:~/fitadapt-ai/.env

# En la instancia:
chmod 600 ~/fitadapt-ai/.env
```

Contenido mínimo (ver sección 5):

```dotenv
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.groq.com/openai/v1
AI_MODEL=openai/gpt-oss-120b
FITADAPT_MODE=ia
CLERK_SECRET_KEY=...
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

> ⚠️ `.env` está excluido por `.gitignore` y `.dockerignore`. Nunca debe commitearse ni incluirse en la imagen. `CLERK_SECRET_KEY` y `OPENAI_API_KEY` son secretos; `VITE_CLERK_PUBLISHABLE_KEY` es pública por diseño.

**3. Construir la imagen.** La clave publicable se incorpora al bundle en tiempo de compilación:

```bash
cd ~/fitadapt-ai
export VITE_CLERK_PUBLISHABLE_KEY=$(grep '^VITE_CLERK_PUBLISHABLE_KEY=' .env | cut -d= -f2-)

docker build \
  --build-arg VITE_CLERK_PUBLISHABLE_KEY="$VITE_CLERK_PUBLISHABLE_KEY" \
  -t fitadaptai:v1.0-aws .
```

**4. Ejecutar el contenedor.** El puerto 80 del host se publica sobre el 8000 interno; los secretos se inyectan en tiempo de ejecución:

```bash
docker run -d \
  --name fitadaptai \
  --restart unless-stopped \
  -p 80:8000 \
  --env-file .env \
  fitadaptai:v1.0-aws
```

**5. Comprobar el arranque:**

```bash
docker ps
docker logs --tail 50 fitadaptai
```

> **Nota:** `--env-file` se lee al **crear** el contenedor. Si se modifica `.env`, hay que recrearlo (`docker rm -f fitadaptai` y volver a ejecutar `docker run`); `docker restart` conserva las variables antiguas. La variable `VITE_CLERK_PUBLISHABLE_KEY` se embebe en el build, por lo que cambiarla exige reconstruir la imagen.

### 9.7. Verificación del despliegue

Despliegue verificado el **7 de noviembre de 2026** sobre la IP pública `54.237.138.20` (la IP cambia si se detiene e inicia la instancia):

* **URL de la aplicación:** <http://54.237.138.20>
* **Imagen desplegada:** `fitadaptai:v1.0-aws`
* **Contenedor:** `8fd1953e2d31` (`Up`, `0.0.0.0:80->8000/tcp`)

Comprobaciones desde la instancia:

```bash
curl -i http://localhost/api/health
curl -i http://localhost/api/me
```

Y desde el equipo local:

```bash
curl -i http://IP_PUBLICA/api/health
```

| Prueba | Comando / acción | Resultado esperado | Resultado obtenido |
| :--- | :--- | :--- | :--- |
| Salud pública | `curl -i http://54.237.138.20/api/health` | `200` + `{"status":"ok",...,"modo":"ia"}` | ✅ `200` · `{"status":"ok","service":"FitAdaptAI API (Python/FastAPI)","modo":"ia"}` |
| Ruta protegida sin token | `curl -i http://54.237.138.20/api/me` | `401` + `"No autorizado. Inicia sesión con Clerk."` | ✅ `401` · `"No autorizado. Inicia sesión con Clerk."` |
| Token inventado | `curl -i -H "Authorization: Bearer a.eyJzdWIiOiJmYWtlIn0.b" http://54.237.138.20/api/me` | `401` | ✅ `401` · `"Sesión inválida o caducada."` |
| SPA servida | `curl -i http://54.237.138.20/` | `200` + HTML de la SPA | ✅ `200 text/html` (485 bytes) |
| Login | Navegador: email y Google | Acceso al formulario | ⬜ Pendiente de comprobar en navegador |
| Generación de rutina | Completar formulario y enviar | Rutina renderizada en menos de 55 s | ⬜ Pendiente |
| Token válido | Consola del navegador: `copy(await window.Clerk.session.getToken())` y `curl -H "Authorization: Bearer <JWT>" .../api/me` | `200` + `user_id` | ⬜ Pendiente |
| Persistencia | `docker ps` | Contenedor `Up` con `0.0.0.0:80->8000/tcp` | ✅ `8fd1953e2d31` · `fitadaptai:v1.0-aws` · `Up 7 minutes` |

> Las URLs de los servicios deben ser accesibles desde Internet. Si `curl` desde fuera falla pero `localhost` responde, revisar el Security Group y que la instancia tenga IP pública.

### 9.8. Operación y ciclo de vida en el laboratorio

| Situación | Acción |
| :--- | :--- |
| Fin de la práctica | Detener la instancia desde la consola de EC2 (`Instance state → Stop`) para no consumir presupuesto. |
| Reinicio de la instancia | La **IP pública cambia** (salvo Elastic IP); actualizar la URL y volver a verificar `/api/health`. El contenedor arranca solo gracias a `--restart unless-stopped` y a Docker habilitado en el arranque. |
| Fin de la sesión del laboratorio (≈4 h) | Las credenciales temporales dejan de ser válidas. La instancia y su volumen EBS pueden seguir existiendo: detenerla explícitamente. |
| Reinicio del laboratorio por el profesor | Se pierden los recursos. Recrear la instancia siguiendo las secciones 9.4–9.6 (el repositorio y el `.env` local permiten reconstruirlo). |
| Actualizar la aplicación | `git fetch --tags && git checkout <tag>`, reconstruir la imagen, `docker rm -f fitadaptai` y volver a ejecutar `docker run`. |
| Cambiar variables de entorno | Editar `.env`, `chmod 600` y **recrear** el contenedor. |
| Cambiar la clave publicable de Clerk | Reconstruir la imagen con el nuevo `--build-arg` y recrear el contenedor. |
| Revisar logs | `docker logs --tail 100 -f fitadaptai`. |
| Fallback si el puerto 80 no está permitido | Publicar con `-p 8000:8000`, abrir el 8000 en el Security Group y acceder con `http://IP_PUBLICA:8000`. |

Opcionalmente, una **Elastic IP** evita el cambio de dirección al reiniciar, pero puede consumir presupuesto cuando la instancia está detenida; para esta práctica no es necesaria.

### 9.9. Diagnóstico de problemas

| Síntoma | Causa probable | Solución |
| :--- | :--- | :--- |
| `docker build` se queda sin memoria o el proceso muere | `t3.micro` con 1 GiB durante `npm ci` + `vue-tsc` | Usar `t3.small` o añadir 2 GiB de swap. |
| Falla `npm ci` en la instancia | `package-lock.json` desincronizado | Desplegar desde un commit con el lock corregido (`npm ci --dry-run` en local). |
| `curl` desde fuera no conecta | Security Group sin la regla 80 o instancia sin IP pública | Revisar reglas de entrada y `Auto-assign public IP`. |
| `502` / conexión rechazada en `/api/*` | Contenedor detenido o caído | `docker ps`, `docker logs fitadaptai`, revisar `docker run`. |
| `500` «La clave de la API de Groq no está configurada» | `.env` ausente o mal montado | Verificar `--env-file .env` y recrear el contenedor. |
| `401` «Falta configuración de Clerk en el servidor» | `CLERK_SECRET_KEY` ausente en `.env` | Añadir la variable y recrear el contenedor. |
| `401` «No se pudo validar la sesión con Clerk» | Sin salida a `api.clerk.com` | Comprobar conectividad saliente de la instancia. |
| La web no carga tras reiniciar la instancia | IP pública nueva | Usar la IP actual o asociar una Elastic IP. |
| Error de CSP en el navegador | En EC2 no se aplica `vercel.json`; no debería ocurrir | Revisar la consola; si se añade un proxy inverso, replicar las cabeceras de seguridad. |

### 9.10. Costes y buenas prácticas

* `t3.small` cuesta aproximadamente **0,021 USD/h** y 16 GiB gp3 alrededor de **1,3 USD/mes** (tarifas orientativas de `us-east-1`); el gasto se descuenta del presupuesto del laboratorio.
* Detener la instancia al terminar cada sesión; el volumen EBS sigue generando un coste mínimo, pero conserva la instalación para la siguiente práctica.
* No subir `.env` al repositorio ni copiarlo dentro de la imagen.
* Mantener el usuario `appuser` sin privilegios dentro del contenedor (ya definido en el `Dockerfile`).
* Etiquetar el commit desplegado (`v1.0-aws`) para poder reconstruir exactamente la misma versión.

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

El backend utiliza `pytest` y `TestClient` para validar la lógica y los endpoints sin necesidad de levantar el servidor ni realizar llamadas de pago al proveedor de IA.

* **Ejecución de la suite:**
  ```bash
  .venv/bin/python -m pytest -v
  ```
* **Casos de prueba cubiertos (`5 passed`):**
  * `test_health_check`: Verifica la disponibilidad de la API (`/api/health`) y el modo de ejecución actual.
  * `test_rechazo_sin_autenticacion`: Verifica que una petición directa a `POST /api/generate-routine` sin token de Clerk sea rechazada con `HTTP 401 Unauthorized`.
  * `test_pydantic_validation_tiempo_fuera_de_rango` y `test_pydantic_validation_equipamiento_vacio`: Comprueban el rechazo de peticiones inválidas devolviendo `HTTP 422`.
  * `test_generate_routine_mock_success`: Evalúa el flujo completo autenticado aislando la verificación JWT y al proveedor de IA mediante `unittest.mock.patch`, comprobando la respuesta `HTTP 200` y la estructura del JSON.

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

> ⚠️ **Estado de la suite de frontend:** los tests actuales de Vitest fueron escritos para una versión anterior de `App.vue` (esperan un elemento `<form>`, `fieldset` y atributos `aria-*` que la interfaz actual ya no utiliza), por lo que hoy fallan aunque `vue-tsc` y `vite build` terminan correctamente. No bloquea la compilación ni el despliegue; queda pendiente actualizar la suite a la UI vigente. El backend, en cambio, mantiene sus `5 passed`.

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
* **Incidencia 8:** Suite de Pytest desactualizada respecto a la autenticación.

  * **Síntoma:** `pytest` → `3 failed, 1 passed`; las pruebas recibían `401` en lugar de `422`/`200`.
  * **Causa:** Las pruebas llamaban a rutas protegidas sin token tras integrar `ClerkAuthMiddleware`.
  * **Solución:** Se añadió `test_rechazo_sin_autenticacion` (`401`) y se simuló (`unittest.mock.patch`) la verificación `ClerkAuthMiddleware._verify` en las pruebas autenticadas de validación y generación (`5 passed`).
* **Incidencia 9:** El backend local respondía `401 "Falta configuración de Clerk en el servidor"`.

  * **Causa:** `CLERK_SECRET_KEY` se había añadido a `.env.local`, que solo lee Vite; el backend únicamente carga `.env`.
  * **Solución:** Mover la variable a `.env` y reiniciar `uvicorn` (`--reload` no detecta cambios en `.env`).
* **Incidencia 10:** Ubicación de `.dockerignore` y advertencia de BuildKit sobre `VITE_CLERK_PUBLISHABLE_KEY`.

  * **Síntoma:** Inicialmente `.dockerignore` se creó dentro de `api/.dockerignore`, por lo que Docker no filtraba el contexto de la raíz; además, BuildKit mostraba un aviso `SecretsUsedInArgOrEnv` sobre `VITE_CLERK_PUBLISHABLE_KEY`.
  * **Diagnóstico y Solución:** Se movió `.dockerignore` a la raíz del repositorio (reduciendo el contexto transferido al daemon a `254 KB` y garantizando la exclusión de `.env`). Respecto al aviso de BuildKit, se verificó que `VITE_CLERK_PUBLISHABLE_KEY` (`pk_test_...`) es una clave **pública** que Vite requiere en tiempo de compilación, mientras que las claves **secretas** (`OPENAI_API_KEY`, `CLERK_SECRET_KEY`) jamás se declaran en el `Dockerfile` y solo se inyectan en ejecución con `--env-file`.

## 12. Historial de Versiones (Git y Evidencias)

* `v1.0-aws`: Despliegue en una instancia EC2 del AWS Academy Learner Lab mediante un único contenedor Docker, con publicación en el puerto 80, secretos inyectados en ejecución y runbook reproducible documentado en la sección 9. Desplegado en `http://54.237.138.20` y verificado externamente: health `200`, SPA `200`, `401` sin token y `401` con token inválido; contenedor `fitadaptai:v1.0-aws` en estado `Up`.
* `v0.5-docker`: Aplicación completa contenerizada en una única imagen Docker multi-etapa (Vue 3 compilado + FastAPI sirviendo estáticos y API protegida con Clerk), verificada localmente.
* `v0.4-clerk`: Autenticación con Clerk operativa en producción. Dependencia `@clerk/vue` registrada, CSP adaptada a Clerk (SDK, login con Google y protección anti-bots) y verificación criptográfica de la firma JWT en el backend con `PyJWT`.
* `v0.3.0` / `v0.3-vercel`: Despliegue *full-stack serverless* completado en Vercel (Fase 3). SPA Vue 3 y FastAPI unificados en un único proyecto, configuración de enrutamiento en `vercel.json`, variables de entorno protegidas y monitorización mediante Vercel CLI.
* `v0.1-backend`: Estructura base de FastAPI, modelos Pydantic y lógica de IA completada y probada.
