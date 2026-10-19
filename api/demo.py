"""Generador local de rutinas para el modo demo de FitAdaptAI.

Construye la sesión con reglas deterministas a partir de un catálogo
estático: no realiza llamadas de red ni consume la clave del proveedor.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import TYPE_CHECKING, Dict, List, Sequence, Tuple

if TYPE_CHECKING:
    from api.index import WorkoutRequest

# Presupuesto temporal de cada ejercicio
SEGUNDOS_POR_REPETICION = 3
TRANSICION_SEGUNDOS = 30

# Repeticiones, descanso y series según el objetivo de la sesión
_PLAN: Dict[str, Dict[str, object]] = {
    "hipertrofia": {"repeticiones": "8-10", "descanso_segundos": 90, "series": 3},
    "fuerza": {"repeticiones": "5", "descanso_segundos": 120, "series": 3},
    "perdida_grasa": {"repeticiones": "12-15", "descanso_segundos": 45, "series": 3},
    "resistencia": {"repeticiones": "15-20", "descanso_segundos": 30, "series": 3},
}

_DELTA_SERIES_POR_NIVEL: Dict[str, int] = {"principiante": -1, "intermedio": 0, "avanzado": 1}

_RPE_POR_NIVEL: Dict[str, str] = {"principiante": "RPE 6", "intermedio": "RPE 7", "avanzado": "RPE 8"}

_CALENTAMIENTOS: Dict[str, str] = {
    "hipertrofia": (
        "2 minutos de movilidad de hombros y cadera seguidos de 2 rondas de 12 sentadillas al aire, "
        "10 remos con banda y 8 flexiones lentas para activar la musculatura de la sesión."
    ),
    "fuerza": (
        "2 minutos de movilidad de tobillo, cadera y torácica seguidos de 2 rondas de 8 sentadillas "
        "con pausa abajo, 8 puentes de glúteos y 6 press de hombros con carga ligera."
    ),
    "perdida_grasa": (
        "3 minutos de marcha en el sitio con elevaciones de rodilla seguidos de 2 rondas de 10 "
        "sentadillas al aire, 10 giros de tronco y 8 zancadas suaves."
    ),
    "resistencia": (
        "2 minutos de movilidad dinámica de cadera y hombros seguidos de 2 rondas de 15 sentadillas "
        "al aire, 10 zancadas con la rodilla en alto y 20 segundos de plancha."
    ),
}


@dataclass(frozen=True)
class CatalogItem:
    """Ejercicio fijo del catálogo local."""

    nombre: str
    equipamiento: str
    objetivos: Tuple[str, ...]
    consejo: str


# Cada categoría dispone de más de 7 ejercicios para poder cubrir
# cualquier sesión de hasta 65-75 minutos con material solo de esa categoría.
CATALOGO: Tuple[CatalogItem, ...] = (
    # mancuernas
    CatalogItem("Press de mancuernas inclinado", "mancuernas", ("hipertrofia", "fuerza"),
                "Lleva los codos a 45 grados y controla la bajada sin rebotar."),
    CatalogItem("Sentadilla búlgara", "mancuernas", ("hipertrofia", "fuerza", "perdida_grasa"),
                "Apoya el pie trasero en un banco y mantén el peso sobre el talón delantero."),
    CatalogItem("Remo con mancuerna a una mano", "mancuernas", ("hipertrofia", "fuerza"),
                "Tira del codo hacia atrás sin girar el tronco."),
    CatalogItem("Zancadas caminando con mancuernas", "mancuernas", ("perdida_grasa", "resistencia", "hipertrofia"),
                "Mantén el torso erguido y la rodilla trasera a un palmo del suelo."),
    CatalogItem("Press de hombros con mancuernas", "mancuernas", ("fuerza", "hipertrofia"),
                "Empuja hacia arriba sin arquear la zona lumbar."),
    CatalogItem("Peso muerto rumano con mancuernas", "mancuernas", ("fuerza", "hipertrofia"),
                "Desliza las mancuernas por los muslos con la espalda neutra."),
    CatalogItem("Elevaciones laterales", "mancuernas", ("hipertrofia", "perdida_grasa"),
                "Sube hasta la altura del hombro sin balancear el cuerpo."),
    CatalogItem("Curl de bíceps con mancuernas", "mancuernas", ("hipertrofia",),
                "Fija los codos al costado y evita balancear el torso."),
    # maquinas
    CatalogItem("Press de pecho en máquina", "maquinas", ("hipertrofia", "fuerza"),
                "Ajusta el asiento para que los mangos queden a la altura del pecho."),
    CatalogItem("Jalón al pecho agarre ancho", "maquinas", ("hipertrofia", "fuerza"),
                "Lleva los codos hacia abajo sin arquear la espalda."),
    CatalogItem("Prensa de piernas", "maquinas", ("fuerza", "hipertrofia"),
                "No despegues la zona lumbar del respaldo durante el empuje."),
    CatalogItem("Remo en máquina", "maquinas", ("hipertrofia", "resistencia"),
                "Saca el pecho y junta los omóplatos al tirar."),
    CatalogItem("Extensión de cuádriceps", "maquinas", ("hipertrofia",),
                "Sube de forma controlada y pausa un instante arriba."),
    CatalogItem("Curl de isquiotibios tumbado", "maquinas", ("hipertrofia", "fuerza"),
                "Evita levantar la cadera del banco al flexionar."),
    CatalogItem("Peso muerto en máquina Smith", "maquinas", ("fuerza", "hipertrofia"),
                "Mantén la barra cerca de las piernas y los hombros hacia atrás."),
    CatalogItem("Elíptica", "maquinas", ("resistencia", "perdida_grasa"),
                "Mantén la espalda recta y pedalea sin martillear el paso."),
    # poleas
    CatalogItem("Cruzado de polea alta", "poleas", ("hipertrofia",),
                "Lleva las manos al centro del pecho sin encoger los hombros."),
    CatalogItem("Remo con polea baja", "poleas", ("hipertrofia", "fuerza", "resistencia"),
                "Mantén el pecho alto y lleva los codos por detrás del cuerpo."),
    CatalogItem("Extensión de tríceps en polea", "poleas", ("hipertrofia",),
                "Fija los codos al cuerpo y extiende por completo."),
    CatalogItem("Curl de bíceps en polea", "poleas", ("hipertrofia",),
                "No muevas los codos durante toda la flexión."),
    CatalogItem("Pullover en polea", "poleas", ("hipertrofia", "resistencia"),
                "Mantén los brazos casi rectos y controla la vuelta."),
    CatalogItem("Paso trasero con polea", "poleas", ("perdida_grasa", "resistencia"),
                "Lleva la pierna hacia atrás manteniendo el tronco estable."),
    CatalogItem("Giros de tronco con polea", "poleas", ("resistencia", "fuerza", "perdida_grasa"),
                "Gira desde la cadera sin despegar los pies del suelo."),
    CatalogItem("Elevación de gemelos en polea", "poleas", ("fuerza", "resistencia"),
                "Sube hasta el máximo recorrido y baja de forma lenta."),
    # barras y discos
    CatalogItem("Sentadilla con barra", "barras_discos", ("fuerza", "hipertrofia"),
                "Mantén el pecho alto y los pies firmes en el suelo."),
    CatalogItem("Press de banca con barra", "barras_discos", ("fuerza", "hipertrofia"),
                "Retracta los omóplatos y toca el pecho con control."),
    CatalogItem("Peso muerto con barra", "barras_discos", ("fuerza", "hipertrofia"),
                "Empuja el suelo con los pies y mantén la espalda neutra."),
    CatalogItem("Remo con barra", "barras_discos", ("hipertrofia", "fuerza"),
                "Inclina el tronco a 45 grados y tira llevando el omóplato."),
    CatalogItem("Press militar con barra", "barras_discos", ("fuerza", "hipertrofia"),
                "Aprieta glúteos y abdomen para no arquear la espalda."),
    CatalogItem("Curl de bíceps con barra", "barras_discos", ("hipertrofia",),
                "Mantén los codos pegados al torso durante todo el movimiento."),
    CatalogItem("Zancadas con barra", "barras_discos", ("perdida_grasa", "resistencia"),
                "Controla la bajada y mantén el tronco vertical."),
    CatalogItem("Remo al mentón con barra", "barras_discos", ("hipertrofia", "resistencia"),
                "Lleva la barra a la clavícula con los codos altos."),
    # peso corporal
    CatalogItem("Flexiones de pecho", "peso_corporal", ("fuerza", "hipertrofia", "resistencia"),
                "Mantén el cuerpo en línea desde la cabeza hasta los talones."),
    CatalogItem("Sentadillas al aire", "peso_corporal", ("perdida_grasa", "resistencia", "hipertrofia"),
                "Lleva las caderas hacia atrás y mantén los talones en el suelo."),
    CatalogItem("Plancha abdominal", "peso_corporal", ("resistencia", "perdida_grasa"),
                "Evita que la cadera se hunda o se eleve durante la apnea."),
    CatalogItem("Zancadas sin peso", "peso_corporal", ("perdida_grasa", "resistencia"),
                "Dobla ambas rodillas a 90 grados sin rebotar en el suelo."),
    CatalogItem("Puente de glúteos", "peso_corporal", ("hipertrofia", "resistencia"),
                "Aprieta los glúteos arriba y no arquees la espalda."),
    CatalogItem("Burpees", "peso_corporal", ("perdida_grasa", "resistencia"),
                "Mantén la espalda recta al apoyar las manos y sal de forma suave."),
    CatalogItem("Mountain climbers", "peso_corporal", ("perdida_grasa", "resistencia"),
                "Lleva las rodillas al pecho con el abdomen activado."),
    CatalogItem("Flexiones diamante", "peso_corporal", ("fuerza", "hipertrofia"),
                "Junta las manos bajo el pecho y mantén los codos cerca del cuerpo."),
)


def _cantidad_ejercicios(tiempo_minutos: int) -> int:
    """Reparte la sesión en bloques coherentes con la duración disponible."""
    if tiempo_minutos <= 30:
        return 4
    if tiempo_minutos <= 45:
        return 5
    if tiempo_minutos <= 60:
        return 6
    return 7


def _pool_disponible(objetivo: str, equipamiento: Sequence[str]) -> List[CatalogItem]:
    """Ejercicios compatibles con el material disponible, con el objetivo primero."""
    elegibles = [item for item in CATALOGO if item.equipamiento in equipamiento]
    # El orden es estable: los compatibles con el objetivo conservan el orden del catálogo.
    elegibles.sort(key=lambda item: 0 if objetivo in item.objetivos else 1)
    return elegibles


def _media_repeticiones(repeticiones: str) -> float:
    """Valor medio del rango de repeticiones, p. ej. '8-10' -> 9.0."""
    if "-" in repeticiones:
        bajo, alto = repeticiones.split("-", 1)
        return (float(bajo) + float(alto)) / 2
    return float(repeticiones)


def _coste_ejercicio(series: int, repeticiones: str, descanso_segundos: int) -> float:
    """Segundos que ocupa un ejercicio incluyendo su transición."""
    trabajo = series * _media_repeticiones(repeticiones) * SEGUNDOS_POR_REPETICION
    descansos = (series - 1) * descanso_segundos
    return trabajo + descansos + TRANSICION_SEGUNDOS


def _plan_ejercicio(objetivo: str, nivel: str, presupuesto: int) -> Tuple[int, str, int]:
    """Series, repeticiones y descanso que caben en el presupuesto del bloque.

    Se recortan primero las series (mínimo 2) conservando el descanso propio
    del objetivo; la duración de la sesión manda sobre la carga inicial.
    """
    plan = _PLAN[objetivo]
    repeticiones = str(plan["repeticiones"])
    descanso = int(plan["descanso_segundos"])
    series = max(2, int(plan["series"]) + _DELTA_SERIES_POR_NIVEL[nivel])

    while series > 2:
        coste = _coste_ejercicio(series, repeticiones, descanso)
        if coste <= presupuesto:
            break
        series -= 1

    return series, repeticiones, descanso


def generar_rutina_demo(payload: WorkoutRequest) -> Dict[str, object]:
    """Construye una rutina local para los parámetros indicados.

    Devuelve un diccionario con las claves de ``RutinaResponse`` excepto
    ``modo``: lo asigna el endpoint según la variable ``FITADAPT_MODE``.
    """
    objetivo = payload.objetivo.value
    nivel = payload.nivel.value
    equipamiento = [item.value for item in payload.equipamiento]
    tiempo_minutos = payload.tiempo_minutos

    cantidad = _cantidad_ejercicios(tiempo_minutos)
    seleccionados = _pool_disponible(objetivo, equipamiento)[:cantidad]

    calentamiento_segundos = min(300, max(180, (tiempo_minutos * 60) // 10))
    presupuesto_bloque = (tiempo_minutos * 60 - calentamiento_segundos) // cantidad

    ejercicios: List[Dict[str, object]] = []
    for item in seleccionados:
        series, repeticiones, descanso = _plan_ejercicio(objetivo, nivel, presupuesto_bloque)
        ejercicios.append(
            {
                "nombre": item.nombre,
                "series": series,
                "repeticiones": repeticiones,
                "descanso_segundos": descanso,
                "rpe_sugerido": _RPE_POR_NIVEL[nivel],
                "consejo_tecnico": item.consejo,
            }
        )

    total_segundos = calentamiento_segundos + sum(
        _coste_ejercicio(int(e["series"]), str(e["repeticiones"]), int(e["descanso_segundos"]))
        for e in ejercicios
    )
    tiempo_total_estimado = min(tiempo_minutos, max(1, ceil(total_segundos / 60)))

    # Alternativa: el siguiente ejercicio del pool que no se ha utilizado.
    usados = {str(e["nombre"]) for e in ejercicios}
    alternativa = next((item for item in _pool_disponible(objetivo, equipamiento) if item.nombre not in usados), None)
    if alternativa is None:
        alternativa = seleccionados[0]
    alternativa_rapida = (
        f"Si la estación de {alternativa.equipamiento.replace('_', ' ')} está ocupada, haz {alternativa.nombre}. "
        f"{alternativa.consejo}"
    )

    return {
        "calentamiento": _CALENTAMIENTOS[objetivo],
        "ejercicios": ejercicios,
        "alternativa_rapida": alternativa_rapida,
        "tiempo_total_estimado": tiempo_total_estimado,
    }
