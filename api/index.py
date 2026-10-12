import os
import json
from enum import Enum
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

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

