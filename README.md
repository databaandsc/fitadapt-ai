# FitAdapt AI · Explotación y Despliegue Cloud de una Aplicación con IA

Aplicación web de pantalla única (SPA) enfocada en el acondicionamiento físico personalizado mediante Inteligencia Artificial. Este repositorio contiene el código fuente, la configuración de seguridad y la documentación operativa reproducible para su explotación en dos arquitecturas: **Full-Stack Serverless (Vercel)** y **Contenedor Único sobre Instancia Cloud (Docker en AWS EC2)**.

---

## Índice de Contenidos

1. [Identificación y Reparto de Tareas](#1-identificación-y-reparto-de-tareas)
2. [Plan de Documentación](#2-plan-de-documentación)
3. [Arquitectura del Sistema y Estructura del Proyecto](#3-arquitectura-del-sistema-y-estructura-del-proyecto)
4. [Requisitos e Instalación Local](#4-requisitos-e-instalación-local)
5. [Variables de Entorno y Seguridad de Configuración](#5-variables-de-entorno-y-seguridad-de-configuración)
6. [Despliegue en Vercel (Fase 3 · Serverless)](#6-despliegue-en-vercel-fase-3--serverless)
7. [Autenticación con Clerk (Fase 4 · Frontend y Verificación JWT)](#7-autenticación-con-clerk-fase-4--frontend-y-verificación-jwt)
8. [Contenerización en Docker (Fase 5 · Contenedor Único)](#8-contenerización-en-docker-fase-5--contenedor-único)
9. [Despliegue en AWS EC2 (Fase 6 · AWS Academy Learner Lab)](#9-despliegue-en-aws-ec2-fase-6--aws-academy-learner-lab)
10. [Operación, Verificación y Tests](#10-operación-verificación-y-tests)
11. [Registro de Problemas y Soluciones](#11-registro-de-problemas-y-soluciones)
12. [Historial de Versiones (Git, Tags y Evidencias)](#12-historial-de-versiones-git-tags-y-evidencias)

---

## 1. Identificación y Reparto de Tareas

* **Práctica:** UD1 · Explotación y despliegue de una aplicación con IA
* **Módulo:** Explotación de Servicios de Procesamiento y Analítica de Datos (ESPAD)
* **Enseñanza:** Curso de Especialización en Inteligencia Artificial y Big Data
* **Aplicación:** **FitAdapt AI** (Generador de sesiones de entrenamiento personalizadas mediante LLM)
* **Repositorio Público:** [https://github.com/databaandsc/fitadaptai](https://github.com/databaandsc/fitadaptai)
* **Despliegue Serverless (Vercel):** [https://fitadaptai-seven.vercel.app](https://fitadaptai-seven.vercel.app)
* **Despliegue en Contenedor (AWS EC2):** Instancia EC2 Linux (`http://<IP_PUBLICA_EC2>`, puerto `80` · IP pública efímera del *AWS Academy Learner Lab*)

### 1.1. Integrantes del Grupo y Aportaciones Individuales

El desarrollo, despliegue y verificación se ha realizado de forma incremental mediante ramas temáticas, *Pull Requests* y revisiones cruzadas, garantizando que ambos integrantes comprendan y operen la solución completa:

| Integrante | Usuario GitHub | Áreas Principales y Aportaciones Verificables en Git |
| :--- | :--- | :--- |
| **Ricardo Fernández Chamorro** | `@databaandsc` | • Diseño e implementación inicial del backend FastAPI (`api/index.py`), validación Pydantic v2 y conexión con Groq (PR #1).<br>• Suite de pruebas unitarias con `pytest` y cobertura del backend (PR #3).<br>• Renovación de la interfaz SPA en Vue 3 + Tailwind CSS (PR #4) y configuración del despliegue Serverless en Vercel + CLI (PR #5).<br>• Endurecimiento de seguridad en Clerk: verificación criptográfica JWT con `PyJWT[crypto]` contra JWKS y ajuste de la política CSP en `vercel.json` (PR #7).<br>• Contenerización multi-etapa (`Dockerfile`, `.dockerignore`), servicio de estáticos desde FastAPI y documentación técnica de Docker (PR #8). |
| **Carlos Madrid** | `@Nozferatu` | • Implementación del modo determinista local (`api/demo.py`) y mapeo defensivo de excepciones del proveedor de IA (PR #2).<br>• Integración inicial de autenticación con Clerk en el frontend Vue (`@clerk/vue`, `src/main.ts`, `src/composables/useApi.ts`) y middleware en backend (PR #6).<br>• Sincronización de dependencias (`package-lock.json`) para compilación reproducible con `npm ci` en contenedor.<br>• Aprovisionamiento, despliegue, verificación de extremo a extremo y documentación operativa del contenedor único en **AWS EC2 (Learner Lab)** (`v1.0-aws`). |

---

## 2. Plan de Documentación

Este documento está dirigido a **ingenieros de sistemas, desarrolladores y profesorado evaluador** que necesiten comprender la arquitectura, auditar las decisiones de seguridad o reproducir desde cero el despliegue de **FitAdapt AI** tanto en Vercel como en AWS EC2.

### 2.1. Metodología y Guías de Referencia

Antes de redactar la documentación se diseñó un plan documental basado en dos referencias estándar:
* **[Marco Diátaxis](https://diataxis.fr/):** estructura el contenido separando claramente la comprensión teórica (*Explicación*: arquitectura y decisiones de seguridad), la puesta en marcha (*Guías prácticas / Runbooks*: instalación local, Vercel CLI, Docker y AWS EC2) y la consulta técnica exacta (*Referencia*: tablas de variables, puertos, CSP y matriz de pruebas).
* **[Guía de escritura y formato en GitHub (GFM)](https://docs.github.com/en/get-started/writing-on-github):** uso de tablas estructuradas, bloques de código con resaltado, alertas contextuales y **diagramas Mermaid** integrados en el propio repositorio para evitar depender de herramientas externas de diagramación.

| Cuadrante Diátaxis | Objetivo | Secciones correspondientes en este `README.md` |
| :--- | :--- | :--- |
| **Explicación (*Explanation*)** | Justificar la arquitectura, la seguridad JWT/CSP y las diferencias entre Serverless y Contenedor. | Secciones **3**, **7.1–7.3** y **9.1** |
| **Guías Cómo Hacerlo (*How-To Guides*)** | Procedimientos reproducibles paso a paso de instalación, compilación, despliegue, reinicio y actualización. | Secciones **4**, **6.2**, **8.1–8.5**, **9.3–9.6** y **9.8** |
| **Referencia (*Reference*)** | Especificación exacta de variables de entorno, reglas de red, cabeceras CSP, pruebas e historial de tags. | Secciones **5**, **6.1**, **7.4–7.6**, **9.2**, **10** y **12** |
| **Diagnóstico (*Troubleshooting*)** | Síntomas reales encontrados en cada fase, causa raíz y solución aplicada. | Secciones **9.9** y **11** |

### 2.2. Flujo de Actualización Documental por Hitos

La documentación no se redactó al final del proyecto, sino que evolucionó en paralelo con cada hito de infraestructura:

```mermaid
flowchart LR
    H1["Fase 1-2: Local<br/>(v0.1 / v0.2)<br/>Arquitectura y Setup"] --> H2["Fase 3: Vercel<br/>(v0.3-vercel)<br/>Serverless y CLI"]
    H2 --> H3["Fase 4: Clerk<br/>(v0.4-clerk)<br/>Flujo JWT, JWKS y CSP"]
    H3 --> H4["Fase 5: Docker<br/>(v0.5-docker)<br/>Multi-stage y .dockerignore"]
    H4 --> H5["Fase 6: AWS EC2<br/>(v1.0-aws)<br/>Runbook Cloud y Verificación"]
```

---

## 3. Arquitectura del Sistema y Estructura del Proyecto

### 3.1. Alcance Mínimo Deliberado y Flujo de Datos

**FitAdapt AI** mantiene un alcance funcional deliberadamente acotado (una única pantalla, un único formulario, sin base de datos ni almacenamiento de historial) para concentrar el diseño en la **seguridad de credenciales, la validación de sesiones y la operación cloud**:

1. **Frontend (Cliente SPA):** construido con **Vue 3 (Composition API)**, **TypeScript** y **Tailwind CSS**, compilado a estáticos mediante **Vite**. Presenta la pantalla de acceso de Clerk si no hay sesión activa y el formulario de configuración de entrenamiento una vez autenticado.
2. **Autenticación y Propagación de Identidad (Clerk):** el cliente obtiene un token de sesión JWT firmado con `RS256` mediante `getToken()` y lo adjunta en la cabecera `Authorization: Bearer <token>`.
3. **Backend (FastAPI + Pydantic v2):** valida criptográficamente el token JWT contra el endpoint JWKS de Clerk en `ClerkAuthMiddleware`, valida los parámetros del entrenamiento con `WorkoutRequest` y construye un *System Prompt* defensivo.
4. **Proveedor de IA (Groq / OpenAI API):** el backend invoca el modelo LLM usando la clave privada `OPENAI_API_KEY` confinada en el servidor, parsea la salida JSON y la valida contra el esquema `RutinaResponse` antes de responder al navegador.

```mermaid
flowchart LR
    subgraph Cliente["Navegador del Usuario (Cliente)"]
        UI["SPA Vue 3 + TS + Tailwind<br/>(Formulario único + Estados UI)"]
        ClerkSDK["SDK @clerk/vue<br/>(SignIn / UserButton / getToken)"]
    end

    subgraph Externos["Servicios Cloud Externos"]
        ClerkCloud["Clerk Auth API<br/>(Emisión JWT RS256 + JWKS)"]
        GroqAPI["Proveedor IA (Groq API)<br/>Modelo LLM (openai/gpt-oss-120b)"]
    end

    subgraph Servidor["Servidor de Aplicación (Vercel Function / Contenedor EC2)"]
        MW["ClerkAuthMiddleware<br/>(Verifica firma RS256, exp y sub)"]
        API["FastAPI (api/index.py)<br/>Validación Pydantic v2"]
        Demo["Catálogo Local (api/demo.py)<br/>(Si FITADAPT_MODE=demo)"]
    end

    UI <-->|"1. Login OAuth / Email"| ClerkSDK
    ClerkSDK <-->|"2. Sesión y JWT"| ClerkCloud
    UI -->|"3. POST /api/generate-routine<br/>Authorization: Bearer JWT"| MW
    MW <-->|"4. Descarga y caché de<br/>claves públicas JWKS"| ClerkCloud
    MW -->|"5. JWT válido"| API
    API <-->|"6a. Modo IA (HTTPS)<br/>OPENAI_API_KEY en servidor"| GroqAPI
    API <-->|"6b. Modo Demo (Sin red)"| Demo
    API -->|"7. JSON validado<br/>(RutinaResponse)"| UI
```

### 3.2. Comparativa de las Dos Arquitecturas de Despliegue

El mismo código fuente se explota en dos arquitecturas cloud complementarias sin modificar la lógica de negocio:

```mermaid
flowchart TB
    subgraph VercelArch["Arquitectura 1: Vercel Full-Stack Serverless (Fase 3 y 4)"]
        direction LR
        VUser["Navegador<br/>(HTTPS)"] --> VEdge["Vercel Edge Network<br/>(vercel.json + Cabeceras CSP)"]
        VEdge -->|"Rutas estáticas /*"| VCDN["CDN Estáticos<br/>(dist/index.html + assets)"]
        VEdge -->|"Rewrite /api/:path*"| VFunc["Vercel Serverless Function<br/>(Runtime Python · api/index.py)"]
    end

    subgraph AWSArch["Arquitectura 2: AWS EC2 Contenedor Único (Fase 5 y 6)"]
        direction LR
        AUser["Navegador<br/>(HTTP :80)"] --> ASG["Security Group (fitadaptai-sg)<br/>TCP 80 (0.0.0.0/0) | TCP 22 (Mi IP)"]
        ASG -->|"Puerto 80 -> 8000"| ADocker["Contenedor Único (fitadaptai:v1.0-aws)<br/>Uvicorn + FastAPI (0.0.0.0:8000)"]
        ADocker -->|"Rutas /api/*"| AAPI["Endpoints FastAPI<br/>(/api/health, /api/generate-routine)"]
        ADocker -->|"Fallback SPA /*"| AStatic["StaticFiles + FileResponse<br/>(Sirve /app/dist compilado)"]
    end
```

| Característica | Despliegue 1: Vercel (Serverless) | Despliegue 2: AWS EC2 (Docker) |
| :--- | :--- | :--- |
| **Modelo de computación** | Funciones efímeras bajo demanda (*Serverless Functions*). | Proceso permanente (`uvicorn`) dentro de un único contenedor Linux. |
| **Entrega del Frontend (`dist/`)** | Servido directamente por el CDN global de Vercel. | Servido por el propio FastAPI (`StaticFiles` y `FileResponse`). |
| **Enrutamiento** | Definido en `vercel.json` (`rewrites` de `/api/:path*` a `/api/index.py`). | Gestionado internamente por FastAPI (prioridad a `/api/*` y *fallback* a `dist/index.html`). |
| **Protocolo y Puerto público** | `HTTPS` (`443`) gestionado automáticamente por Vercel. | `HTTP` (`80` en host mapeado al `8000` del contenedor). |
| **Inyección de secretos** | Panel / CLI de Vercel (`vercel env add`). | Archivo privado `~/fitadapt-ai/.env` (`chmod 600`) inyectado con `--env-file`. |

### 3.3. Estructura del Proyecto

```text
fitadaptai/
├── api/                          # Backend Python (FastAPI)
│   ├── __init__.py
│   ├── index.py                  # Punto de entrada FastAPI, endpoints /api/* y montaje condicional de dist/
│   ├── auth_middleware.py        # Middleware de verificación criptográfica JWT (RS256 + JWKS de Clerk)
│   ├── demo.py                   # Generador determinista local para FITADAPT_MODE=demo
│   └── test_api.py               # Suite de pruebas unitarias de backend (Pytest + TestClient)
├── src/                          # Frontend SPA (Vue 3 + TypeScript + Tailwind CSS)
│   ├── App.vue                   # Pantalla única: login con Clerk, formulario validado y vista de rutina
│   ├── main.ts                   # Inicialización de Vue y registro de clerkPlugin
│   ├── style.css                 # Directivas de Tailwind CSS y estilos globales
│   ├── composables/
│   │   └── useApi.ts             # Wrapper fetch que inyecta Authorization: Bearer <token>
│   └── types/
│       └── workout.ts            # Contratos TypeScript alineados con los modelos de Pydantic
├── tests/                        # Pruebas de componentes frontend (Vitest)
├── Dockerfile                    # Construcción multi-etapa (Node 22 Alpine -> Python 3.14 Slim)
├── .dockerignore                 # Exclusión de secretos (.env*) y artefactos pesados del contexto Docker
├── vercel.json                   # Enrutamiento Serverless, maxDuration (15s) y cabeceras HTTP/CSP
├── requirements.txt              # Dependencias fijadas del backend Python
├── package.json                  # Dependencias y scripts del frontend Vue/Vite
├── .env.example                  # Plantilla pública de variables de entorno (sin secretos reales)
└── README.md                     # Documentación técnica y operativa única del proyecto
```

---

## 4. Requisitos e Instalación Local

Para levantar el entorno de desarrollo y pruebas en local se requieren las siguientes herramientas:

| Herramienta / Tecnología | Versión Utilizada | Finalidad |
| :--- | :--- | :--- |
| **Node.js / npm** | `v22.x` / `v24.x` (mínimo `18.x`) | Compilación de la SPA Vue 3, TypeScript y Tailwind CSS con Vite. |
| **Python** | `3.14` (compatible `3.10+`) | Ejecución del backend FastAPI, validación Pydantic y tests `pytest`. |
| **Docker Engine / Desktop** | `28.x` (mínimo `24.x`) | Construcción de la imagen multi-etapa y ejecución del contenedor único. |
| **Vercel CLI** | `64.x` | Vinculación, gestión de variables, despliegue e inspección en Vercel. |

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

---

## 5. Variables de Entorno y Seguridad de Configuración

La configuración inyectada mediante variables de entorno garantiza el confinamiento de secretos. En desarrollo local se utilizan dos archivos, ambos excluidos del control de versiones mediante `.gitignore` y `.dockerignore` (con `.env.example` como plantilla pública de referencia):

* **`.env`** → lo lee el **backend** (`load_dotenv()` en `api/index.py` o `--env-file` en Docker).
* **`.env.local`** → lo lee el **frontend** (Vite). Solo las variables con prefijo `VITE_` se incorporan al código que se envía al navegador.

### 5.1. Tabla de Variables de Entorno

| **Variable**                 | **Finalidad**                                                                 | **Tipo**    | **Ubicación / Entorno**                              | **Momento de uso**      |
| ---------------------------- | ----------------------------------------------------------------------------- | ----------- | ---------------------------------------------------- | ----------------------- |
| `OPENAI_API_KEY`             | Credencial de acceso a la API del LLM (Groq/OpenAI).                          | **Secreto** | `.env` / `--env-file` en Docker / Vercel Env         | Ejecución (Runtime)     |
| `OPENAI_BASE_URL`            | URL base para derivar el tráfico a proveedores compatibles (ej. Groq).        | Pública     | `.env` / `--env-file` en Docker / Vercel Env         | Ejecución (Runtime)     |
| `AI_MODEL`                   | Nombre del modelo a instanciar (ej. `openai/gpt-oss-120b`).                   | Pública     | `.env` / `--env-file` en Docker / Vercel Env         | Ejecución (Runtime)     |
| `AI_MAX_TOKENS`              | Límite de tokens de la respuesta del modelo (opcional, por defecto `4000`).   | Pública     | `.env` / `--env-file` en Docker / Vercel Env         | Ejecución (Runtime)     |
| `FITADAPT_MODE`              | Modo de ejecución: `ia` (por defecto) o `demo` (catálogo local, sin IA).      | Pública     | `.env` / `--env-file` en Docker / Vercel Env         | Ejecución (Runtime)     |
| `CLERK_SECRET_KEY`           | Clave secreta de Clerk. Permite al backend obtener las claves públicas (JWKS) con las que verifica los tokens. | **Secreto** | `.env` / `--env-file` en Docker / Vercel Env | Ejecución (Runtime) |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clave publicable de Clerk. Inicializa el SDK en el navegador. Es pública por diseño. | Pública | `.env.local` / `--build-arg` en Docker / Vercel Env | **Compilación (Build)** |

> ⚠️ `CLERK_SECRET_KEY` y `OPENAI_API_KEY` **nunca** deben llevar el prefijo `VITE_`: si lo llevaran, Vite las incrustaría en el bundle JavaScript público y quedarían visibles para cualquier visitante en las herramientas de desarrollo del navegador.

### 5.2. Esquema de Separación entre Compilación (Build) y Ejecución (Runtime)

```mermaid
flowchart LR
    subgraph Publicas["Configuración Pública (Build Time)"]
        PK["VITE_CLERK_PUBLISHABLE_KEY<br/>(pk_test_...)"]
    end

    subgraph Secretos["Secretos Privados (Runtime)"]
        SK1["OPENAI_API_KEY<br/>(gsk_...)"]
        SK2["CLERK_SECRET_KEY<br/>(sk_test_...)"]
        CFG["OPENAI_BASE_URL / AI_MODEL"]
    end

    PK -->|"Vite Build / docker build --build-arg"| Bundle["Bundle Estático (dist/assets/*.js)<br/>Visible en el navegador"]
    SK1 & SK2 & CFG -->|"docker run --env-file .env<br/>o Vercel Secret Env"| FastAPI["Proceso FastAPI en Servidor<br/>NUNCA sale al navegador ni a la imagen"]
```

---

## 6. Despliegue en Vercel (Fase 3 · Serverless)

La aplicación se despliega como un **único proyecto en Vercel**, unificando la SPA (Vue 3 + Vite) y el Backend (FastAPI) bajo el mismo dominio de producción para eliminar la necesidad de configurar CORS externo y reducir la latencia de red.

### 6.1. Arquitectura Serverless y Enrutamiento

```mermaid
flowchart LR
    Client["Cliente Web<br/>https://fitadaptai-seven.vercel.app"] --> Edge["Vercel Edge Network<br/>Aplica cabeceras HSTS, CSP, X-Frame-Options"]
    Edge -->|"GET / o /assets/*"| Static["Activos Estáticos Vite<br/>(Carpeta compilada dist/)"]
    Edge -->|"Rewrite /api/:path*"| Lambda["Vercel Serverless Function<br/>api/index.py (Python Runtime · maxDuration 15s)"]
    Lambda -->|"GET /api/health"| Health["Respuesta 200 OK (Pública)"]
    Lambda -->|"POST /api/generate-routine"| Protected["ClerkAuthMiddleware -> Groq API"]
```

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

---

## 7. Autenticación con Clerk (Fase 4 · Frontend y Verificación JWT)

La aplicación requiere autenticación con **Clerk** para poder utilizarla. La protección se aplica en dos capas independientes: la interfaz (frontend) y la API (backend).

### 7.1. Flujo de Autenticación de Extremo a Extremo

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

### 7.3. Backend (FastAPI · Árbol de Decisión y Verificación JWT)

El middleware `ClerkAuthMiddleware` (`api/auth_middleware.py`) protege todas las rutas `/api/*` excepto las públicas (`/api/health`, `/docs`, `/openapi.json`, `/redoc`).

```mermaid
flowchart TD
    Req["Petición entrante a FastAPI"] --> IsOpt{"¿Método OPTIONS o<br/>ruta fuera de /api/* o<br/>en PUBLIC_PATHS?"}
    IsOpt -->|"Sí (ej. /, /assets/*, /api/health)"| Pass["Pasa directamente al handler"]
    IsOpt -->|"No (ej. /api/generate-routine, /api/me)"| HasBearer{"¿Existe cabecera<br/>Authorization: Bearer <JWT>?"}
    HasBearer -->|"No"| Err401A["401 Unauthorized<br/>'Inicia sesión con Clerk'"]
    HasBearer -->|"Sí"| HasSecret{"¿CLERK_SECRET_KEY<br/>configurada en servidor?"}
    HasSecret -->|"No"| Err401B["401 Unauthorized<br/>'Falta configuración de Clerk'"]
    HasSecret -->|"Sí"| VerifyJWKS["PyJWKClient obtiene clave pública (JWKS)<br/>y PyJWT verifica firma RS256, exp y sub"]
    VerifyJWKS --> IsValid{"¿Firma RS256 válida<br/>y token no expirado?"}
    IsValid -->|"No (Token falso o caducado)"| Err401C["401 Unauthorized<br/>'Sesión inválida o caducada'"]
    IsValid -->|"Sí"| OkState["Guarda user_id y session_id<br/>en request.state y ejecuta endpoint"]
```

Para cada petición protegida:
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

---

## 8. Contenerización en Docker (Fase 5 · Contenedor Único)

La aplicación completa se empaqueta y ejecuta en **un único contenedor Docker** mediante una construcción multi-etapa (`Dockerfile`):

```mermaid
flowchart LR
    subgraph Contexto["Contexto de Build (~255 KB)"]
        Ignore[".dockerignore<br/>Excluye .env*, .venv,<br/>node_modules, .git"]
        SrcFrontend["package*.json, src/,<br/>index.html, vite/ts configs"]
        SrcBackend["requirements.txt,<br/>api/"]
    end

    subgraph Stage1["Etapa 1: frontend-builder (node:22-alpine)"]
        NPM["RUN npm ci"]
        BuildArg["ARG VITE_CLERK_PUBLISHABLE_KEY<br/>(Clave pública)"]
        ViteBuild["RUN npm run build<br/>Genera /app/dist"]
        NPM --> BuildArg --> ViteBuild
    end

    subgraph Stage2["Etapa 2: runtime (python:3.14-slim)"]
        Pip["RUN pip install -r requirements.txt"]
        CopyArtifacts["COPY api ./api<br/>COPY --from=frontend-builder /app/dist ./dist"]
        User["USER appuser (Sin privilegios)<br/>EXPOSE 8000"]
        Cmd["CMD uvicorn api.index:app<br/>--host 0.0.0.0 --port 8000"]
        Pip --> CopyArtifacts --> User --> Cmd
    end

    SrcFrontend --> NPM
    SrcBackend --> Pip
    ViteBuild ==>|"Copia solo estáticos compilados<br/>(Node.js se descarta)"| CopyArtifacts
    EnvFile["Archivo privado .env<br/>(OPENAI_API_KEY, CLERK_SECRET_KEY)"] -.->|"Inyección en Runtime<br/>(docker run --env-file)"| Cmd
```

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

Para el despliegue en **AWS EC2** (Fase 6), no se requiere un registro externo de imágenes: se clona el repositorio público directamente en la instancia EC2 situándose en el tag versionado (`v0.5-docker` / `v1.0-aws`), se construye la imagen localmente en la instancia con `docker build` y se ejecuta el contenedor inyectando un archivo `.env` privado en el servidor con permisos restringidos (`chmod 600 .env`) y política de reinicio `--restart unless-stopped`.

---

## 9. Despliegue en AWS EC2 (Fase 6 · AWS Academy Learner Lab)

Esta fase despliega la aplicación completa en **una única instancia EC2** que ejecuta el contenedor Docker descrito en la sección 8. FastAPI sirve en el mismo origen tanto la API (`/api/*`) como la SPA compilada (`dist/`), por lo que no se necesita configurar CORS ni un segundo servicio.

### 9.1. Arquitectura de Red y Contenedor en AWS EC2

```mermaid
flowchart TB
    subgraph Internet["Clientes Externos e Internet"]
        Browser["Navegador Evaluador / Usuario<br/>(http://IP_PUBLICA)"]
        AdminSSH["Equipo Administrador<br/>(SSH / SCP con fitadaptai-key.pem)"]
        ExtAPIs["APIs Externas (HTTPS :443)<br/>• api.groq.com (LLM)<br/>• api.clerk.com (JWKS)"]
    end

    subgraph AWSCloud["AWS Cloud · Región us-east-1 (VPC por defecto · Subred Pública)"]
        subgraph SG["Security Group: fitadaptai-sg"]
            Rule80["Regla Entrada HTTP: TCP 80<br/>Origen: 0.0.0.0/0"]
            Rule22["Regla Entrada SSH: TCP 22<br/>Origen: Mi IP (Restringido)"]
            RuleOut["Regla Salida: Todo el tráfico<br/>Destino: 0.0.0.0/0"]
        end

        subgraph EC2["Instancia EC2 Linux (t3.small · 2 vCPU, 2 GiB RAM · EBS 16 GiB gp3)"]
            EnvPriv["Archivo ~/fitadapt-ai/.env<br/>Permisos: chmod 600 (-rw-------)"]
            subgraph DockerEngine["Docker Engine (systemd enabled)"]
                Container["Contenedor Único: fitadaptai (fitadaptai:v1.0-aws)<br/>Política: --restart unless-stopped | Usuario: appuser<br/>Mapeo de puerto: 0.0.0.0:80 -> 8000/tcp"]
                UvicornApp["Uvicorn + FastAPI (api/index.py)<br/>• GET /* -> Sirve SPA compilada (/app/dist)<br/>• GET /api/health -> 200 OK Público<br/>• POST /api/generate-routine -> ClerkAuthMiddleware + IA"]
                Container --> UvicornApp
            end
            EnvPriv -.->|"--env-file .env"| Container
        end
    end

    Browser -->|"HTTP Puerto 80"| Rule80 --> Container
    AdminSSH -->|"SSH Puerto 22"| Rule22 --> EC2
    UvicornApp -->|"HTTPS Saliente"| RuleOut --> ExtAPIs
```

### 9.2. Decisiones de Arquitectura para el Laboratorio

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

### 9.3. Recursos Aprovisionados y Reglas del Security Group

| Recurso | Especificación | Finalidad |
| :--- | :--- | :--- |
| Instancia EC2 | `t3.small` (2 vCPU, 2 GiB RAM), Amazon Linux 2023 o Ubuntu 24.04 | Ejecutar el contenedor. |
| Volumen EBS | 16 GiB gp3 | Sistema operativo, Docker e imagen. |
| Par de claves | `fitadaptai-key.pem` | Acceso SSH. |
| Security Group | `fitadaptai-sg` | Puertos 22 y 80. |
| IP pública | Auto-asignada por el laboratorio | URL de acceso. |
| Docker Engine | Última versión del repositorio de la distribución | Construcción y ejecución del contenedor. |

Reglas de entrada (*Inbound rules*) del Security Group:

| Puerto | Protocolo | Origen | Motivo |
| :--- | :--- | :--- | :--- |
| `22` | TCP | *Mi IP* (recomendado) | Administración por SSH. |
| `80` | TCP | `0.0.0.0/0` | Acceso público a la aplicación. |

El tráfico de salida permanece abierto (regla por defecto): la instancia necesita contactar con `api.groq.com` (proveedor de IA) y `api.clerk.com` (claves JWKS de autenticación).

### 9.4. Pre-flight Local

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

### 9.5. Aprovisionamiento en el Learner Lab y Preparación del Host

1. Pulsar **Start Lab** y esperar a que el indicador esté en verde.
2. Seleccionar la región del laboratorio (normalmente **N. Virginia, `us-east-1`**).
3. En **EC2 → Key Pairs**, crear `fitadaptai-key` y descargar el archivo `.pem`.
4. En **EC2 → Launch instance**:
   * Nombre: `fitadaptai`
   * AMI: **Amazon Linux 2023** (alternativa: Ubuntu Server 24.04 LTS)
   * Tipo: **t3.small**
   * Key pair: `fitadaptai-key`
   * Red: VPC por defecto, subred pública y **Auto-assign public IP: Enable**
   * Security Group: crear `fitadaptai-sg` con las reglas de la sección 9.3
   * Almacenamiento: **16 GiB gp3**
5. Anotar la **IP pública** de la instancia.

Proteger la clave privada y conectar por SSH:

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

Verificar la instalación:

```bash
docker --version
sudo systemctl is-enabled docker   # enabled
```

### 9.6. Flujo y Comandos de Despliegue de la Aplicación en EC2

```mermaid
sequenceDiagram
    participant Dev as Equipo Local (Mac)
    participant GH as GitHub (Repositorio Público)
    participant EC2 as Instancia EC2 (Host Linux)
    participant Dk as Docker Engine (EC2)

    Dev->>EC2: 1. ssh -i fitadaptai-key.pem (chmod 400)
    EC2->>GH: 2. git clone + git checkout v1.0-aws
    GH-->>EC2: Código fuente + Dockerfile + .dockerignore
    Dev->>EC2: 3. scp .env -> ~/fitadapt-ai/.env
    EC2->>EC2: 4. chmod 600 ~/fitadapt-ai/.env
    EC2->>Dk: 5. docker build --build-arg VITE_CLERK_PUBLISHABLE_KEY -t fitadaptai:v1.0-aws .
    Dk-->>EC2: Imagen construida (Node compilado + FastAPI)
    EC2->>Dk: 6. docker run -d --name fitadaptai --restart unless-stopped -p 80:8000 --env-file .env
    Dev->>EC2: 7. Verificación externa (http://IP_PUBLICA y /api/health)
```

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

### 9.7. Verificación del Despliegue en AWS EC2

Despliegue verificado el **7 de noviembre de 2026** en una instancia EC2 del Learner Lab.

> La **IP pública del laboratorio es efímera**: cambia cada vez que se detiene e inicia la instancia. Por ese motivo no se fija como constante estática; se consulta en la consola de EC2 (durante la sesión de validación inicial correspondió a `54.237.138.20`) y se usa como `IP_PUBLICA` en los comandos siguientes.

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
| Salud pública | `curl -i http://IP_PUBLICA/api/health` | `200` + `{"status":"ok",...,"modo":"ia"}` | ✅ `200` · `{"status":"ok","service":"FitAdaptAI API (Python/FastAPI)","modo":"ia"}` |
| Ruta protegida sin token | `curl -i http://IP_PUBLICA/api/me` | `401` + `"No autorizado. Inicia sesión con Clerk."` | ✅ `401` · `"No autorizado. Inicia sesión con Clerk."` |
| Token inventado | `curl -i -H "Authorization: Bearer a.eyJzdWIiOiJmYWtlIn0.b" http://IP_PUBLICA/api/me` | `401` | ✅ `401` · `"Sesión inválida o caducada."` |
| SPA servida | `curl -i http://IP_PUBLICA/` | `200` + HTML de la SPA | ✅ `200 text/html` (485 bytes) |
| Login | Navegador: pantalla de Clerk | Acceso al formulario | ✅ Pantalla de Clerk y acceso correctos |
| Generación de rutina | Completar formulario y enviar | Rutina renderizada en menos de 55 s | ✅ Rutina generada y mostrada en la interfaz |
| Token válido | Consola del navegador: `copy(await window.Clerk.session.getToken())` y `curl -H "Authorization: Bearer <JWT>" .../api/me` | `200` + `user_id` | ⬜ Comprobación opcional no realizada |
| Persistencia | `docker ps` | Contenedor `Up` con `0.0.0.0:80->8000/tcp` | ✅ `8fd1953e2d31` · `fitadaptai:v1.0-aws` · `Up 7 minutes` |

> El primer acceso puede tardar unos segundos mientras se descarga el SDK de Clerk y se inicializa la sesión; las cargas posteriores son inmediatas. Si `curl` desde fuera falla pero `localhost` responde, revisar el Security Group y que la instancia tenga IP pública. Las URLs de los servicios deben ser accesibles desde Internet.

### 9.8. Operación y Ciclo de Vida en el Laboratorio

| Situación | Acción |
| :--- | :--- |
| Fin de la práctica | Detener la instancia desde la consola de EC2 (`Instance state → Stop`) para no consumir presupuesto. |
| Reinicio de la instancia | La **IP pública cambia** (salvo Elastic IP); actualizar la URL y volver a verificar `/api/health`. El contenedor arranca solo gracias a `--restart unless-stopped` y a Docker habilitado en el arranque. |
| Fin de la sesión del laboratorio (≈4 h) | Las credenciales temporales dejan de ser válidas. La instancia y su volumen EBS pueden seguir existiendo: detenerla explícitamente. |
| Reinicio del laboratorio por el profesor | Se pierden los recursos. Recrear la instancia siguiendo las secciones 9.5–9.6 (el repositorio y el `.env` local permiten reconstruirlo). |
| Actualizar la aplicación | `git fetch --tags && git checkout <tag>`, reconstruir la imagen, `docker rm -f fitadaptai` y volver a ejecutar `docker run`. |
| Cambiar variables de entorno | Editar `.env`, `chmod 600` y **recrear** el contenedor. |
| Cambiar la clave publicable de Clerk | Reconstruir la imagen con el nuevo `--build-arg` y recrear el contenedor. |
| Revisar logs | `docker logs --tail 100 -f fitadaptai`. |
| Fallback si el puerto 80 no está permitido | Publicar con `-p 8000:8000`, abrir el 8000 en el Security Group y acceder con `http://IP_PUBLICA:8000`. |

Opcionalmente, una **Elastic IP** evita el cambio de dirección al reiniciar, pero puede consumir presupuesto cuando la instancia está detenida; para esta práctica no es necesaria.

### 9.9. Diagnóstico de Problemas en EC2

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

### 9.10. Costes y Buenas Prácticas

* `t3.small` cuesta aproximadamente **0,021 USD/h** y 16 GiB gp3 alrededor de **1,3 USD/mes** (tarifas orientativas de `us-east-1`); el gasto se descuenta del presupuesto del laboratorio.
* Detener la instancia al terminar cada sesión; el volumen EBS sigue generando un coste mínimo, pero conserva la instalación para la siguiente práctica.
* No subir `.env` al repositorio ni copiarlo dentro de la imagen.
* Mantener el usuario `appuser` sin privilegios dentro del contenedor (ya definido en el `Dockerfile`).
* Etiquetar el commit desplegado (`v1.0-aws`) para poder reconstruir exactamente la misma versión.

---

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

### 10.4. Comprobaciones Manuales, Modo Demo y Matriz de Verificación Multi-Entorno

Para evitar consumir la cuota (tokens) de OpenAI/Groq durante el desarrollo de la interfaz, el sistema incluye un **Modo Demo** determinista (`FITADAPT_MODE=demo`).

| Caso de Verificación | Desarrollo Local (`:5173` / `:8000`) | Vercel Serverless (`https://fitadaptai-seven.vercel.app`) | Docker Local (`http://localhost:8000`) | AWS EC2 Docker (`http://IP_PUBLICA`) |
| :--- | :---: | :---: | :---: | :---: |
| **Carga de SPA Vue 3 (`GET /`)** | ✅ `200 OK` | ✅ `200 OK` (CDN) | ✅ `200 OK` (FastAPI) | ✅ `200 OK` (FastAPI) |
| **Health Check (`GET /api/health`)** | ✅ `200 OK` | ✅ `200 OK` | ✅ `200 OK` | ✅ `200 OK` |
| **Rechazo sin token (`POST /api/generate-routine`)** | ✅ `401 Unauthorized` | ✅ `401 Unauthorized` | ✅ `401 Unauthorized` | ✅ `401 Unauthorized` |
| **Rechazo con JWT manipulado (`/api/me`)** | ✅ `401 Unauthorized` | ✅ `401 Unauthorized` | ✅ `401 Unauthorized` | ✅ `401 Unauthorized` |
| **Login con Clerk + Generación real de rutina IA** | ✅ Verificado | ✅ Verificado | ✅ Verificado | ✅ Verificado |

---

## 11. Registro de Problemas y Soluciones

* **Incidencia 1:** Conflicto de entornos virtuales locales (Conda vs Venv) al ejecutar `uvicorn`.
  * **Síntoma:** Error `ModuleNotFoundError: No module named 'fastapi'`.
  * **Solución:** Forzar la ejecución de Uvicorn a través del binario de Python del entorno virtual activo mediante el comando `python -m uvicorn api.index:app --reload --port 8000`.
* **Incidencia 2:** Fallo en la generación de rutinas por retirada de modelos en el proveedor Groq.
  * **Síntoma:** El servidor devuelve `HTTP 500 Internal Server Error` y el log de FastAPI muestra `Error code: 400 - The model has been decommissioned`.
  * **Solución:** El backend manejó la excepción correctamente evitando el bloqueo. Se acudió a la consola de Groq para consultar los *Model IDs* vigentes y se actualizó la variable `AI_MODEL` en el archivo `.env` por una versión operativa (ej. `openai/gpt-oss-120b`), resolviendo la petición con éxito.
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

---

## 12. Historial de Versiones (Git, Tags y Evidencias)

### 12.1. Evolución Incremental de Hitos y Tags

```mermaid
flowchart LR
    T1["v0.1-backend<br/>Commit: 69a1b31<br/>FastAPI + Groq + Pytest"] --> T2["v0.2-frontend<br/>Commit: 1de3be9<br/>SPA Vue 3 + TS + Tailwind"]
    T2 --> T3["v0.3-vercel<br/>Commit: 16ff673<br/>Serverless + Vercel CLI"]
    T3 --> T4["v0.4-clerk<br/>Commit: 8045ec4<br/>Clerk Auth + JWT JWKS + CSP"]
    T4 --> T5["v0.5-docker<br/>Commit: ca22ecd<br/>Dockerfile Multi-Stage Único"]
    T5 --> T6["v1.0-aws<br/>Commit: caa2c30<br/>Despliegue Final AWS EC2"]
```

### 12.2. Tabla Resumen de Versiones Publicadas

| Tag / Versión | Commit | Fase | Descripción Técnica y Evidencias Asociadas |
| :--- | :---: | :---: | :--- |
| **`v0.1-backend`** | `69a1b31` | Fase 1 | Estructura base de FastAPI (`api/index.py`), validación Pydantic v2, conexión con Groq, modo demo local (`api/demo.py`) y suite de pruebas unitarias con `pytest` (`api/test_api.py`). |
| **`v0.2-frontend`** | `1de3be9` | Fase 2 | Interfaz SPA en Vue 3 + TypeScript + Tailwind CSS (`src/App.vue`), formulario único validado, estados de carga/error y conexión local con FastAPI. |
| **`v0.3-vercel`** | `16ff673` | Fase 3 | Despliegue *full-stack serverless* en un único proyecto Vercel (`vercel.json`), configuración de variables protegidas y operaciones reales con Vercel CLI (`https://fitadaptai-seven.vercel.app`). |
| **`v0.4-clerk`** | `8045ec4` | Fase 4 | Autenticación con Clerk operativa en producción (`@clerk/vue`), ajuste de cabeceras CSP (SDK, Google OAuth y protección anti-bots) y verificación criptográfica de firma JWT RS256 en el backend con `PyJWT[crypto]` y JWKS. |
| **`v0.5-docker`** | `ca22ecd` | Fase 5 | Aplicación completa contenerizada en una única imagen Docker multi-etapa (`Dockerfile` + `.dockerignore`), sirviendo estáticos compilados (`dist/`) y API protegida desde FastAPI. |
| **`v1.0-aws`** | `caa2c30` | Fase 6 | Despliegue final en instancia EC2 (`t3.small`) del *AWS Academy Learner Lab* mediante un único contenedor Docker (`fitadaptai:v1.0-aws`, contenedor `8fd1953e2d31`), publicado en el puerto `80`, con secretos inyectados en ejecución (`chmod 600 .env`) y verificado extremo a extremo (`200` en `/` y `/api/health`, `401` sin token y con token inválido, login de Clerk y generación real de rutina con IA). |
