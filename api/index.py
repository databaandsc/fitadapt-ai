import os
import json
from enum import Enum
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = FastAPI(
    title = "FitAdaptAI API",
    description = "Backend serverless para la generación de planes de entrenamiento personalizados",
    version = "1.0.0"
)

# 1. Configuracion de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

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
    calentamiento: str
    ejercicios: List[Ejercicio]
    alternativa_rapida: str
    tiempo_total_estimado: int
    
# 4. Configuración de la API de Groq

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
    return {"status": "ok", "service": "FitAdaptAI API (Python/FastAPI)"}


@app.post("/api/generate-routine", response_model = RutinaResponse)
def generate_routine(payload: WorkoutRequest):
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
        '  "tiempo_total_estimado": 45\n'
        "}\n"
        "No incluyas texto conversacional ni explicaciones fuera del bloque JSON."
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
            max_tokens = 1000,
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
        return RutinaResponse(**parsed_data)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="La respuesta del modelo de IA no cumplió con el formato JSON requerido."
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el procesamiento de la rutina: {str(exc)}"
        )
