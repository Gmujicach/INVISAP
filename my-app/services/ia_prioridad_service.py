import json
import os
import re
import subprocess
import time

import requests

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
OLLAMA_BIN = os.environ.get("OLLAMA_BIN", r"C:\Users\Eliot\ollama_portable\ollama.exe")
_REQUEST_TIMEOUT = 120
_OLLAMA_MODEL = "llama3.2:1b"

OBRA_VALOR_TEXTO = {3: "Obra Mayor", 1: "Obra Menor"}
GRAVEDAD_VALOR_TEXTO = {3: "Alta", 1: "Baja"}
ZONA_AGRICOLA_VALOR_TEXTO = {3: "Si", 1: "No"}

PESOS_SOLICITANTE = {"comunidad": 3, "institucion": 2, "institución": 2, "particular": 1}
PESOS_GRAVEDAD = {3: 3, 1: 1}
PESOS_TIPO_OBRA = {"Obra Mayor": 3, "Obra Menor": 1}
PESOS_ZONA_AGRICOLA = {3: 3, 1: 1}

SYSTEM_PROMPT = (
    "Eres un clasificador determinista. Analiza la descripción y la ubicación de la obra "
    "y responde EXCLUSIVAMENTE con un JSON válido y compacto con esta estructura exacta: "
    '{"tipo_obra_valor": 3 | 1, "gravedad_valor": 3 | 1, "es_zona_agricola": 3 | 1}. '
    "Reglas obligatorias (sin valores intermedios, sin decimales, sin texto fuera del JSON): "
    "1) tipo_obra_valor: si la descripción menciona puentes, fallas de borde, avenidas "
    "principales, carreteras, drenaje profundo o infraestructura crítica -> 3 (Obra Mayor). "
    "Si describe bacheo, limpieza, aceras, señalización o mantenimiento menor -> 1 (Obra Menor). "
    "2) gravedad_valor: si el riesgo es inminente, colapso o afecta a personas -> 3 (Alta). "
    "Si es mantenimiento preventivo -> 1 (Baja). "
    "3) es_zona_agricola: si municipio, parroquia, sector o ámbito describen zona rural "
    "con producción agrícola, alimentos, finca, potrero, comunidad campesina -> 3. "
    "Si es zona urbana -> 1. "
    "Cada campo es estrictamente 3 o 1. Nunca decimales, nunca otro número."
)


def _generar_prompt_usuario(descripcion, municipio=None, parroquia=None,
                            sector=None, ambito=None,
                            gravedad_nivel=None, color_semaforo=None,
                            tipo_solicitante=None):
    contexto = []
    if municipio:
        contexto.append(f"Municipio: {municipio}.")
    if parroquia:
        contexto.append(f"Parroquia: {parroquia}.")
    if sector:
        contexto.append(f"Sector: {sector}.")
    if ambito:
        contexto.append(f"Ámbito: {ambito}.")
    if gravedad_nivel:
        contexto.append(f"Gravedad registrada: {gravedad_nivel}.")
    if color_semaforo:
        contexto.append(f"Semáforo de la obra: {color_semaforo}.")
    if tipo_solicitante:
        contexto.append(f"Tipo de solicitante: {tipo_solicitante}.")
    contexto_texto = " ".join(contexto)
    return f"Descripción de la obra: \"{descripcion}\". {contexto_texto}"


def _servidor_disponible():
    try:
        r = requests.get(f"http://{OLLAMA_HOST}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def _arrancar_ollama():
    if _servidor_disponible() or not os.path.exists(OLLAMA_BIN):
        return
    try:
        subprocess.Popen(
            [OLLAMA_BIN, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            | getattr(subprocess, "DETACHED_PROCESS", 0),
        )
    except Exception:
        return
    for _ in range(20):
        time.sleep(1)
        if _servidor_disponible():
            return


def _parsear_respuesta(data):
    raw = (data.get("response") or "{}").strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return {}


def _coercer_entero(valor, permitidos=(3, 1), por_defecto=1):
    """Convierte a int y valida contra el conjunto permitido. Defensa contra respuestas
    mal formadas (decimales, strings, nulos)."""
    try:
        n = int(valor)
    except (TypeError, ValueError):
        try:
            n = int(float(valor))
        except (TypeError, ValueError):
            return por_defecto
    return n if n in permitidos else por_defecto


def _validar_resultado(resultado):
    tipo_valor = _coercer_entero(resultado.get("tipo_obra_valor"), (3, 1), 1)
    grav_valor = _coercer_entero(resultado.get("gravedad_valor"), (3, 1), 1)
    zona_valor = _coercer_entero(resultado.get("es_zona_agricola"), (3, 1), 1)
    return {
        "tipo_obra_valor": tipo_valor,
        "gravedad_valor": grav_valor,
        "es_zona_agricola": zona_valor,
        "tipo_obra": OBRA_VALOR_TEXTO[tipo_valor],
        "gravedad_sugerida": GRAVEDAD_VALOR_TEXTO[grav_valor],
        "zona_agricola": ZONA_AGRICOLA_VALOR_TEXTO[zona_valor],
        "origen": "ia",
        "justificacion": (
            f"IA: tipo_obra_valor={tipo_valor}, "
            f"gravedad_valor={grav_valor}, "
            f"es_zona_agricola={zona_valor}."
        ),
    }


def _clasificar_con_ollama(descripcion, municipio=None, parroquia=None,
                           sector=None, ambito=None,
                           gravedad_nivel=None, color_semaforo=None,
                           tipo_solicitante=None):
    _arrancar_ollama()
    payload = {
        "model": _OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": _generar_prompt_usuario(
            descripcion, municipio, parroquia, sector, ambito,
            gravedad_nivel, color_semaforo, tipo_solicitante,
        ),
        "stream": False,
        "format": "json",
        "options": {"num_predict": 120, "temperature": 0},
    }
    try:
        response = requests.post(
            f"http://{OLLAMA_HOST}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    resultado = _parsear_respuesta(data)
    if not resultado:
        return None
    return _validar_resultado(resultado)


def _clasificacion_heuristica(descripcion, municipio=None, parroquia=None,
                              sector=None, ambito=None,
                              gravedad_nivel=None, color_semaforo=None,
                              tipo_solicitante=None):
    desc = (descripcion or "").lower()
    texto_ubicacion = " ".join([
        (municipio or "").lower(),
        (parroquia or "").lower(),
        (sector or "").lower(),
        (ambito or "").lower(),
    ])
    color = (color_semaforo or "").lower()
    gravedad = (gravedad_nivel or "").lower()

    obra_mayor_keywords = [
        "colapso", "colapsar", "falla de borde", "borde", "puente", "viaducto",
        "avenida principal", "reconstrucción", "reconstruir", "carretera",
        "drenaje profundo", "colector pluvial", "infraestructura crítica",
        "maquinaria pesada", "excavadora", "asfaltado",
    ]
    obra_menor_keywords = [
        "bacheo", "bache", "limpieza", "acera", "aceras", "señalización",
        "pintura", "barrido", "desmalezamiento", "luminaria",
        "jornada de vacunación", "vacunación",
    ]
    zona_agricola_keywords = [
        "rural", "agro", "agrícola", "agricola", "agrop", "campesina",
        "campesino", "productor", "cosecha", "finca", "potrero", "parcela",
        "comunidad campesina", "producción de alimentos",
    ]

    tipo_valor = 1
    grav_valor = 1
    if any(p in desc for p in obra_mayor_keywords):
        tipo_valor = 3
        grav_valor = 3
    elif any(p in desc for p in obra_menor_keywords):
        tipo_valor = 1
        grav_valor = 1

    if color in ("rojo", "roja") or gravedad in ("alta", "critica", "crítica"):
        grav_valor = 3

    zona_valor = 1
    if any(p in texto_ubicacion for p in zona_agricola_keywords):
        zona_valor = 3

    if tipo_solicitante and tipo_solicitante.lower() in ("comunidad", "institucion", "institución"):
        if tipo_valor == 1 and grav_valor == 3:
            tipo_valor = 3

    return {
        "tipo_obra_valor": tipo_valor,
        "gravedad_valor": grav_valor,
        "es_zona_agricola": zona_valor,
        "tipo_obra": OBRA_VALOR_TEXTO[tipo_valor],
        "gravedad_sugerida": GRAVEDAD_VALOR_TEXTO[grav_valor],
        "zona_agricola": ZONA_AGRICOLA_VALOR_TEXTO[zona_valor],
        "origen": "heuristica",
        "justificacion": (
            f"Heurística: tipo={tipo_valor}, gravedad={grav_valor}, zona_agricola={zona_valor}."
        ),
    }


def clasificar_solicitud_ia(descripcion, municipio=None, parroquia=None,
                            sector=None, ambito=None,
                            gravedad_nivel=None, color_semaforo=None,
                            tipo_solicitante=None):
    resultado = _clasificar_con_ollama(
        descripcion, municipio, parroquia, sector, ambito,
        gravedad_nivel, color_semaforo, tipo_solicitante,
    )
    if resultado is not None:
        return resultado
    return _clasificacion_heuristica(
        descripcion, municipio, parroquia, sector, ambito,
        gravedad_nivel, color_semaforo, tipo_solicitante,
    )


def calcular_puntaje_prioridad(tipo_solicitante, gravedad_valor, tipo_obra,
                               es_zona_agricola_valor):
    """Puntaje ponderado con conversión explícita a int. Defensa contra valores mal
    formateados: cualquier no-entero cae al peso por defecto (1)."""
    solicitante_lower = (tipo_solicitante or "").lower()
    peso_solicitante = int(PESOS_SOLICITANTE.get(solicitante_lower, 1))
    peso_gravedad = int(PESOS_GRAVEDAD.get(int(gravedad_valor), 1))
    peso_tipo_obra = int(PESOS_TIPO_OBRA.get(tipo_obra, 1))
    peso_zona = int(PESOS_ZONA_AGRICOLA.get(int(es_zona_agricola_valor), 1))

    puntaje = (
        peso_solicitante * 0.20
        + peso_gravedad * 0.35
        + peso_tipo_obra * 0.30
        + peso_zona * 0.15
    )
    rango = round((3 - puntaje) / 2, 3)
    return {
        "puntaje_ponderado": round(puntaje, 3),
        "rango_prioridad": round(min(max(rango, 0.0), 1.0), 3),
        "peso_solicitante": peso_solicitante,
        "peso_gravedad": peso_gravedad,
        "peso_tipo_obra": peso_tipo_obra,
        "peso_zona_agricola": peso_zona,
    }


def calcular_prioridad_con_ia(descripcion, municipio=None, parroquia=None,
                              sector=None, ambito=None,
                              gravedad_nivel=None, color_semaforo=None,
                              tipo_solicitante=None):
    resultado = clasificar_solicitud_ia(
        descripcion, municipio, parroquia, sector, ambito,
        gravedad_nivel, color_semaforo, tipo_solicitante,
    )
    calculo = calcular_puntaje_prioridad(
        tipo_solicitante,
        resultado["gravedad_valor"],
        resultado["tipo_obra"],
        resultado["es_zona_agricola"],
    )
    return {
        "prioridad": calculo["rango_prioridad"],
        "justificacion": resultado["justificacion"],
        "tipo_obra": resultado["tipo_obra"],
        "gravedad_sugerida": resultado["gravedad_sugerida"],
        "zona_agricola": resultado["zona_agricola"],
        "tipo_obra_valor": resultado["tipo_obra_valor"],
        "gravedad_valor": resultado["gravedad_valor"],
        "es_zona_agricola": resultado["es_zona_agricola"],
        "origen": resultado.get("origen", "desconocido"),
        "calculo": calculo,
    }
