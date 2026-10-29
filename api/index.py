import os
import json
import logging
from enum import Enum
from typing import List, Literal
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
import openai
from openai import OpenAI

try:
    from .demo import generar_rutina_demo
    from .auth_middleware import ClerkAuthMiddleware
except ImportError:  # pragma: no cover - solo aplica si se ejecuta como módulo suelto (p. ej. Vercel)
    # Vercel ejecuta este archivo como módulo suelto desde el directorio api/.
    from demo import generar_rutina_demo
    from auth_middleware import ClerkAuthMiddleware

load_dotenv()

logger = logging.getLogger("fitadapt.api")

app = FastAPI(
    title="FitAdaptAI API",
    description="Backend serverless para la generación de planes de entrenamiento personalizados",
    version="1.0.0",
)

# 1. Configuracion de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Autenticación Clerk (protege /api/* excepto /api/health)
app.add_middleware(ClerkAuthMiddleware)


# 2. Esquema de validación de entrda de datos

class ObjetivoEnum(str, Enum):
    hipertrofia = "hipertrofia"
    fuerza = "fuerza"
    perdida_grasa = "perdida_grasa"
    resistencia = "resistencia"

class NivelEnum(str, Enum):
    principiante = "principiante"
    intermedio = "intermedio"
    avanzado = "avanzado"

class EquipamientoEnum(str, Enum):
    mancuernas = "mancuernas"
    maquinas = "maquinas"
    poleas = "poleas"
    barras_discos = "barras_discos"
    peso_corporal = "peso_corporal"

class WorkoutRequest(BaseModel):
    objetivo: ObjetivoEnum
    tiempo_minutos: int = Field(..., ge=20, le=75, description="Duración en minutos (20-75)")
    equipamiento: List[EquipamientoEnum] = Field(..., min_length=1, description="Mínimo un equipamiento")
    nivel: NivelEnum

# 3. Esquemas de respuesta estructurada

class Ejercicio(BaseModel):
    nombre: str
    series: int
    repeticiones: str
    descanso_segundos: int
    rpe_sugerido: str
    consejo_tecnico: str

class RutinaResponse(BaseModel):
    modo: Literal["demo", "ia"] = Field(..., description="Origen de la rutina: catálogo local (demo) o proveedor de IA")
    calentamiento: str
    ejercicios: List[Ejercicio]
    alternativa_rapida: str
    tiempo_total_estimado: int

# 4. Configuración de la API de Groq

def get_run_mode() -> Literal["demo", "ia"]:
    # Si la variable no existe o tiene un valor desconocido, se opera en modo IA
    modo = (os.getenv("FITADAPT_MODE", "ia") or "ia").strip().lower()
    return modo if modo in ("demo", "ia") else "ia"

def get_ai_client() -> OpenAI:
    # Leemos la clave de la API de Groq desde las variables de entorno
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "La clave de la API de Groq no está configurada en las variables de entorno."
        )
    
    # Leemos la URL base de la API de Groq desde las variables de entorno
    base_url = os.getenv("OPENAI_BASE_URL", None)
    
    # Devolvemos un cliente de la API de Groq configurado con la clave y la URL base
    return OpenAI(api_key=api_key, base_url=base_url)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "FitAdaptAI API (Python/FastAPI)", "modo": get_run_mode()}


@app.get("/api/me")
def get_current_user(request: Request):
    return {
        "user_id": getattr(request.state, "user_id", None),
        "session_id": getattr(request.state, "session_id", None),
    }


@app.post("/api/generate-routine", response_model=RutinaResponse)
def generate_routine(payload: WorkoutRequest):

    modo = get_run_mode()

    # Modo demo: rutina local determinista, sin cliente ni red.
    if modo == "demo":
        rutina = generar_rutina_demo(payload)
        return RutinaResponse(modo = "demo", **rutina)

    client = get_ai_client()
    
    system_prompt = (
        "Eres un entrenador de fuerza y especialista en biomecánica con titulación internacional. "
        "Tu objetivo es diseñar una sesión de entrenamiento adaptada a las restricciones indicadas. "
        "Debes responder EXCLUSIVAMENTE con un JSON válido con la siguiente estructura exacta:\n"
        "{\n"
        '  "calentamiento": "descripción de 2-3 frases de movilidad y activación articular",\n'
        '  "ejercicios": [\n'
        '    {\n'
        '      "nombre": "Nombre del ejercicio",\n'
        '      "series": 3,\n'
        '      "repeticiones": "8-10",\n'
        '      "descanso_segundos": 90,\n'
        '      "rpe_sugerido": "RPE 8",\n'
        '      "consejo_tecnico": "Instrucción biomecánica clave de seguridad y ejecución"\n'
        '    }\n'
        '  ],\n'
        '  "alternativa_rapida": "Sustituto rápido por si el equipamiento principal está ocupado",\n'
        '  "tiempo_total_estimado": 30\n'
        "}\n"
        "No incluyas texto conversacional ni explicaciones fuera del bloque JSON.\n"
        "El valor de tiempo_total_estimado debe ser la suma estimada en minutos de la sesión "
        "propuesta (calentamiento, ejercicios y descansos) y NUNCA debe superar el tiempo "
        "total disponible indicado por el usuario."
    )
    
    user_prompt = (
        f"Genera una sesión de gimnasio con estos parámetros:\n"
        f"- Objetivo: {payload.objetivo.value}\n"
        f"- Tiempo total disponible: {payload.tiempo_minutos} minutos\n"
        f"- Nivel del practicante: {payload.nivel.value}\n"
        f"- Equipamiento disponible: {', '.join([e.value for e in payload.equipamiento])}\n\n"
        f"Ajusta el volumen para no exceder los {payload.tiempo_minutos} minutos."
    )
    
    try:
        completion = client.chat.completions.create(
            model = os.getenv("AI_MODEL", "openai/gpt-oss-120b"),
            messages = [
                {"role" : "system", "content" : system_prompt},
                {"role" : "user", "content" : user_prompt}
            ],
            temperature = 0.3,
            # Los modelos de razonamiento emiten su cadena interna antes del JSON:
            # con 1000 la respuesta se truncaba y el parseo fallaba de forma intermitente.
            max_tokens = int(os.getenv("AI_MAX_TOKENS", "4000")),
        )
        
        raw_content = completion.choices[0].message.content.strip()
        
        # Intentamos parsear la respuesta como JSON
        if raw_content.startswith("```"):
            lines = raw_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_content = "\n".join(lines).strip()

        parsed_data = json.loads(raw_content)
        return RutinaResponse(modo = "ia", **parsed_data)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="La respuesta del modelo de IA no cumplió con el formato JSON requerido."
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="La respuesta del modelo de IA no tiene la estructura esperada."
        )
    except openai.AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La credencial del proveedor de IA no es válida. Contacta con el administrador."
        )
    except openai.RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Se ha excedido la cuota o el límite de peticiones del proveedor de IA. Inténtalo más tarde."
        )
    except openai.APITimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="El proveedor de IA ha excedido el tiempo de espera. Inténtalo más tarde."
        )
    except openai.APIConnectionError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se ha podido conectar con el proveedor de IA. Inténtalo más tarde."
        )
    except openai.APIStatusError:
        # Errores 4xx/5xx del proveedor que no encajan con los casos anteriores
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El proveedor de IA ha devuelto un error inesperado. Inténtalo más tarde."
        )
    except HTTPException:
        raise
    except Exception:
        # Se registra el detalle completo solo en el servidor; nunca se filtra al cliente
        logger.exception("Error inesperado durante la generación de la rutina")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar la rutina. Inténtalo más tarde."
        )
