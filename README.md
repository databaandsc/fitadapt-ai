# FitAdaptAI

Aplicación local de rutinas de entrenamiento basada en `pract01-vercel.md`: Vue 3, TypeScript, Tailwind y FastAPI. El documento original se conserva fuera del proyecto.

## Abrir en Windows

Las dependencias se instalan en esta carpeta. Haz doble clic en **Iniciar FitAdaptAI.cmd** y abre **http://127.0.0.1:5173**. Mantén la ventana abierta mientras utilizas la aplicación; Ctrl+C detiene la sesión.

En una instalación nueva necesitas Node.js 20.18 o superior y Python 3.12 (versión comprobada). Desde esta carpeta:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

## Modos de generación

El modo **demo** funciona sin cuenta, sin clave y sin llamadas externas. Usa un catálogo de ejercicios y reglas según objetivo, nivel, equipamiento y tiempo. La duración es una estimación calculada con calentamiento, series, descansos y transiciones; puede ser inferior al tiempo disponible. La pantalla identifica cada resultado demo.

Para usar un proveedor de IA, copia `.env.example` a `.env`, cambia `FITADAPT_MODE=ia` e introduce tu clave en `OPENAI_API_KEY`. Reinicia el servidor. La clave permanece en Python y nunca se incluye en el cliente. El uso del proveedor puede tener coste. `OPENAI_BASE_URL` permite configurar un endpoint compatible y `AI_MODEL` su modelo.

Si el proveedor falla se muestra un error; no se sustituye silenciosamente la respuesta por una demo. La integración real necesita una clave válida y no se comprueba mediante llamadas de pago durante las pruebas.

## Inicio manual (Windows)

En una terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8000
```

En otra:

```powershell
npm run dev
```

En Linux/macOS: `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`, `npm ci`; inicia el servidor con `.venv/bin/python -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8000` y el cliente con `npm run dev` en otra terminal.

## Comprobaciones

La batería completa de Vue, FastAPI y Playwright, su instalación y sus informes están descritos en [TESTING.md](TESTING.md). Una vez instaladas las dependencias de desarrollo y los navegadores, ejecuta `npm run test:all`.

```powershell
npm run build
npm test
.\.venv\Scripts\python.exe -m pytest -q
```

La documentación interactiva de la API está en http://127.0.0.1:8000/docs. Vite redirige `/api` al servidor local. `npm run preview` solo muestra la compilación estática; para el flujo completo utiliza el inicio local anterior.

## Cambios respecto al ejemplo

- Corregido `str` a `string` en TypeScript y actualizada la herramienta de comprobación de tipos.
- Duración entera de 20 a 75 minutos en pasos de 5, equipamiento no vacío, sin duplicados, y rechazo de campos desconocidos.
- Respuestas del proveedor validadas; errores sin revelar datos internos y tiempos de espera acotados.
- Carga de `.env`, sin CORS abierto: el navegador utiliza el proxy del mismo origen.
- Formulario bloqueado durante la petición; mensajes accesibles y parámetros del resultado conservados aunque se cambien los controles.
- Modo demo explícito, arranque Windows y pruebas sin consumo de API.

`vercel.json` está preparado con el preset Vite y la función Python; el despliegue real en Vercel sigue pendiente de verificación. Consulta `despliegue-vercel.md` antes de publicar. En local, los puertos solo escuchan en la propia máquina.
