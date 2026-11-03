import json
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

# Token JWT simulado (header.payload.signature) para pruebas autenticadas con ClerkAuthMiddleware
AUTH_HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyX3Rlc3RfMTIzIiwic2lkIjoic2Vzc190ZXN0XzEyMyJ9.sig"
}


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "modo" in response.json()


def test_rechazo_sin_autenticacion():
    """Verifica que una petición directa al endpoint de IA sin token sea rechazada con 401."""
    payload = {
        "objetivo": "hipertrofia",
        "tiempo_minutos": 45,
        "equipamiento": ["mancuernas"],
        "nivel": "intermedio"
    }
    response = client.post("/api/generate-routine", json=payload)
    assert response.status_code == 401
    assert "No autorizado" in response.json()["detail"]


@patch(
    "api.auth_middleware.ClerkAuthMiddleware._verify",
    return_value={"sub": "user_test_123", "sid": "sess_test_123"},
)
def test_pydantic_validation_tiempo_fuera_de_rango(_mock_verify):
    """Verifica que tiempos inferiores a 20 o superiores a 75 sean rechazados con 422."""
    payload = {
        "objetivo": "hipertrofia",
        "tiempo_minutos": 10,
        "equipamiento": ["mancuernas"],
        "nivel": "intermedio"
    }
    response = client.post("/api/generate-routine", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422


@patch(
    "api.auth_middleware.ClerkAuthMiddleware._verify",
    return_value={"sub": "user_test_123", "sid": "sess_test_123"},
)
def test_pydantic_validation_equipamiento_vacio(_mock_verify):
    """Verifica que una lista de equipamiento vacía sea rechazada con 422."""
    payload = {
        "objetivo": "fuerza",
        "tiempo_minutos": 45,
        "equipamiento": [],
        "nivel": "avanzado"
    }
    response = client.post("/api/generate-routine", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422


@patch(
    "api.auth_middleware.ClerkAuthMiddleware._verify",
    return_value={"sub": "user_test_123", "sid": "sess_test_123"},
)
@patch("api.index.get_ai_client")
def test_generate_routine_mock_success(mock_get_client, _mock_verify):
    """Comprueba el flujo de generación exitoso aislando el servicio de IA mediante un mock."""
    mock_payload = {
        "calentamiento": "Movilidad escapular y 5 minutos de cinta suave.",
        "ejercicios": [
            {
                "nombre": "Press militar con mancuernas sentado",
                "series": 3,
                "repeticiones": "8-10",
                "descanso_segundos": 90,
                "rpe_sugerido": "RPE 8",
                "consejo_tecnico": "Mantén el core firme y no arquees excesivamente la zona lumbar."
            }
        ],
        "alternativa_rapida": "Press de hombros en máquina si las mancuernas no están disponibles.",
        "tiempo_total_estimado": 45
    }

    # Configuramos el mock para simular la respuesta de OpenAI
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(mock_payload)
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
    mock_get_client.return_value = mock_client

    request_data = {
        "objetivo": "hipertrofia",
        "tiempo_minutos": 45,
        "equipamiento": ["mancuernas"],
        "nivel": "intermedio"
    }

    response = client.post("/api/generate-routine", json=request_data, headers=AUTH_HEADERS)
    assert response.status_code == 200
    
    data = response.json()
    assert data["tiempo_total_estimado"] == 45
    assert data["modo"] == "ia"
    assert len(data["ejercicios"]) == 1
    assert data["ejercicios"][0]["nombre"] == "Press militar con mancuernas sentado"