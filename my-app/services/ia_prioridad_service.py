import json
import os
import re
import shutil
import subprocess
import threading
import time
from datetime import datetime

import requests

from conexion.conexionBD import connectionBD

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434").rstrip("/")
if not OLLAMA_HOST.startswith(("http://", "https://")):
    OLLAMA_HOST = f"http://{OLLAMA_HOST}"
OLLAMA_BIN = os.environ.get("OLLAMA_BIN")
_REQUEST_TIMEOUT = 120
_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
_ollama_lock = threading.Lock()

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


def _localizar_ollama():
    candidatas = [
        OLLAMA_BIN,
        shutil.which("ollama"),
    ]
    local_app_data = os.environ.get("LOCALAPPDATA")
    program_files = os.environ.get("ProgramFiles")
    if local_app_data:
        candidatas.append(os.path.join(local_app_data, "Programs", "Ollama", "ollama.exe"))
    if program_files:
        candidatas.append(os.path.join(program_files, "Ollama", "ollama.exe"))

    for candidata in candidatas:
        if candidata and os.path.isfile(candidata):
            return candidata
    return None


def _servidor_disponible():
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def _modelo_disponible():
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        if response.status_code != 200:
            return False
        nombres = {
            modelo.get('name')
            for modelo in response.json().get('models', [])
            if modelo.get('name')
        }
        if ':' in _OLLAMA_MODEL:
            return _OLLAMA_MODEL in nombres
        return _OLLAMA_MODEL in nombres or f'{_OLLAMA_MODEL}:latest' in nombres
    except Exception:
        return False


def _arrancar_ollama():
    with _ollama_lock:
        if _servidor_disponible():
            return
        ejecutable = _localizar_ollama()
        if not ejecutable:
            return

        opciones = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if os.name == "nt":
            opciones["creationflags"] = (
                subprocess.CREATE_NEW_PROCESS_GROUP
                | getattr(subprocess, "DETACHED_PROCESS", 0)
            )

        try:
            subprocess.Popen([ejecutable, "serve"], **opciones)
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
    if not _modelo_disponible():
        print(f"[Ollama] Modelo no disponible: {_OLLAMA_MODEL}")
        return None

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
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=(5, _REQUEST_TIMEOUT),
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[Ollama] Error al clasificar: {e}")
        return None

    resultado = _parsear_respuesta(data)
    campos_requeridos = {'tipo_obra_valor', 'gravedad_valor', 'es_zona_agricola'}
    if not campos_requeridos.issubset(resultado):
        print("[Ollama] Respuesta incompleta; se usará clasificación heurística.")
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


# ============================================
# WORKER EN SEGUNDO PLANO (APScheduler + Threads)
# ============================================

_scheduler = None
_scheduler_lock = threading.Lock()
_worker_active = False


class PrioridadWorkerModel:
    """Modelo del worker — encapsulamiento POO con atributos privados y setters validados por regex."""

    _RE_JUSTIFICACION = re.compile(r'^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ\s.,;:!?\'"\-]{3,150}$')
    _RE_RESPONSABLE = re.compile(r'^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ\s]{2,30}$')
    _RE_ID = re.compile(r'^\d+$')

    def __init__(self):
        self.__id_prioridad = None
        self.__solicitud_id = None
        self.__rango_prioridad = 0.0
        self.__justificacion = ""
        self.__responsable = "Sistema"
        self.__estado = 1
        self.__tipo_obra = None
        self.__gravedad_sugerida = None
        self.__origen = "ia"

    @property
    def id_prioridad(self):
        return self.__id_prioridad

    @id_prioridad.setter
    def id_prioridad(self, valor):
        if not self._RE_ID.match(str(valor or '')):
            raise ValueError("ID de prioridad debe ser entero válido.")
        self.__id_prioridad = int(valor)

    @property
    def solicitud_id(self):
        return self.__solicitud_id

    @solicitud_id.setter
    def solicitud_id(self, valor):
        if not self._RE_ID.match(str(valor or '')):
            raise ValueError("ID de solicitud debe ser entero válido.")
        self.__solicitud_id = int(valor)

    @property
    def rango_prioridad(self):
        return self.__rango_prioridad

    @rango_prioridad.setter
    def rango_prioridad(self, valor):
        try:
            v = float(valor)
            if not (0.0 <= v <= 1.0):
                raise ValueError("Rango fuera de [0.0, 1.0].")
            self.__rango_prioridad = round(v, 3)
        except (TypeError, ValueError):
            raise ValueError("Prioridad debe ser número entre 0 y 1.")

    @property
    def justificacion(self):
        return self.__justificacion

    @justificacion.setter
    def justificacion(self, valor):
        if not self._RE_JUSTIFICACION.match(str(valor or '')):
            raise ValueError("Justificación inválida (3-150 caracteres alfanuméricos).")
        self.__justificacion = valor

    @property
    def responsable(self):
        return self.__responsable

    @responsable.setter
    def responsable(self, valor):
        if not self._RE_RESPONSABLE.match(str(valor or '')):
            raise ValueError("Responsable inválido (2-30 caracteres).")
        self.__responsable = valor

    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, valor):
        self.__estado = 1 if int(valor) else 0

    @property
    def tipo_obra(self):
        return self.__tipo_obra

    @tipo_obra.setter
    def tipo_obra(self, valor):
        if valor not in ("Obra Mayor", "Obra Menor", None):
            raise ValueError("Tipo de obra debe ser 'Obra Mayor' o 'Obra Menor'.")
        self.__tipo_obra = valor

    @property
    def gravedad_sugerida(self):
        return self.__gravedad_sugerida

    @gravedad_sugerida.setter
    def gravedad_sugerida(self, valor):
        if valor not in ("Alta", "Baja", None):
            raise ValueError("Gravedad debe ser 'Alta' o 'Baja'.")
        self.__gravedad_sugerida = valor

    @property
    def origen(self):
        return self.__origen

    @origen.setter
    def origen(self, valor):
        if valor not in ('ia', 'heuristica', 'error', 'manual', 'pendiente', None):
            raise ValueError("Origen inválido.")
        self.__origen = valor

    def _obtener_siguiente_id(self, cursor):
        cursor.execute(
            "SELECT COALESCE(MAX(id_gestion_prioridad), 0) + 1 AS siguiente_id FROM prioridad"
        )
        fila = cursor.fetchone()
        return fila[0] if fila else 1

    def _insertar_prioridad(self, conexion, solicitud_id, rango, justificacion,
                               tipo_obra, gravedad_sugerida, origen, responsable):
        cursor = None
        try:
            cursor = conexion.cursor()
            siguiente_id = self._obtener_siguiente_id(cursor)
            sql = """INSERT INTO prioridad
                     (id_gestion_prioridad, rango_prioridad, tipo_obra, gravedad_sugerida,
                      origen, fecha_asignacion, responsable_ajuste, justificacion_cambio,
                      estado)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                siguiente_id, rango, tipo_obra, gravedad_sugerida,
                origen, datetime.now(), responsable, justificacion,
                self.__estado,
            ))
            return siguiente_id
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass

    def _actualizar_solicitud_prioridad(self, conexion, solicitud_id, prioridad_id):
        cursor = None
        try:
            cursor = conexion.cursor()
            sql = "UPDATE solicitudes SET prioridad_id_gestion_prioridad=%s WHERE id_solicitudes=%s"
            cursor.execute(sql, (prioridad_id, solicitud_id))
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass

    def guardar_prioridad(self, solicitud_id, rango, justificacion, tipo_obra,
                          gravedad_sugerida, origen, responsable):
        """Valida y persiste la prioridad. Llama métodos privados desde validación pública."""
        self.solicitud_id = solicitud_id
        self.rango_prioridad = rango
        self.justificacion = justificacion
        self.tipo_obra = tipo_obra
        self.gravedad_sugerida = gravedad_sugerida
        self.origen = origen
        self.responsable = responsable

        conexion = connectionBD()
        try:
            prioridad_id = self._insertar_prioridad(
                conexion, solicitud_id, rango, justificacion, tipo_obra,
                gravedad_sugerida, origen, responsable,
            )
            self._actualizar_solicitud_prioridad(conexion, solicitud_id, prioridad_id)
            conexion.commit()
            self.__id_prioridad = prioridad_id
            return prioridad_id
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()


def _procesar_priorizacion(solicitud_id, tipo_solicitante=None):
    from models.model_prioridad import PrioridadModel

    try:
        resultado = PrioridadModel.clasificar_nueva_solicitud(
            solicitud_id,
            "IA-Batch",
        )
        if not resultado.get('success'):
            raise RuntimeError(resultado.get('message', 'No se pudo clasificar la solicitud.'))
        datos = resultado['data']
        print(
            f"[Worker Async] Solicitud #{solicitud_id} priorizada: "
            f"rango={datos['rango']}, origen={datos['origen']}"
        )
    except Exception as e:
        print(f"[Worker Async] Error priorizando solicitud {solicitud_id}: {e}")


def priorizar_solicitud_async(id_solicitud, tipo_solicitante=None):
    thread = threading.Thread(
        target=_procesar_priorizacion,
        args=(id_solicitud, tipo_solicitante),
        daemon=True,
        name=f"prioridad-async-{id_solicitud}",
    )
    thread.start()
    return thread


def _worker_batch_ejecutar():
    from models.model_prioridad import PrioridadModel

    print("[Worker Batch] Iniciando ciclo de procesamiento batch...")
    try:
        resultado = PrioridadModel.procesar_solicitudes_pendientes_batch("IA-Batch")
        print(
            "[Worker Batch] Ciclo completado: "
            f"{resultado.get('procesadas', 0)} procesadas, "
            f"{resultado.get('errores', 0)} errores."
        )
    except Exception as e:
        print(f"[Worker Batch] Error: {e}")


class _TimerFallback:
    """Fallback simple si APScheduler no está instalado."""

    def __init__(self):
        self._timer = None
        self._stopped = False

    def add_job(self, func, trigger, **kwargs):
        self._stopped = False
        interval = kwargs.get('minutes', 5) * 60
        self._schedule(interval, func)

    def _schedule(self, interval, func):
        def _run():
            if self._stopped:
                return
            try:
                func()
            except Exception as e:
                print(f"[Timer Fallback] Error: {e}")
            if not self._stopped:
                self._schedule(interval, func)
        self._timer = threading.Timer(interval, _run)
        self._timer.daemon = True
        self._timer.start()

    def start(self):
        pass

    def shutdown(self):
        self._stopped = True
        if self._timer:
            self._timer.cancel()


def obtener_scheduler():
    global _scheduler
    if _scheduler is None:
        with _scheduler_lock:
            if _scheduler is None:
                try:
                    from apscheduler.schedulers.background import BackgroundScheduler
                    _scheduler = BackgroundScheduler()
                    _scheduler.add_job(
                        _worker_batch_ejecutar,
                        'interval',
                        minutes=5,
                        id='worker_prioridad_batch',
                        replace_existing=True,
                        coalesce=True,
                        max_instances=1,
                    )
                    print("[Scheduler] APScheduler configurado (intervalo: 5 min).")
                except ImportError:
                    print("[Scheduler] APScheduler no disponible. Usando Timer fallback.")
                    _scheduler = _TimerFallback()
                    _scheduler.add_job(
                        _worker_batch_ejecutar,
                        'interval',
                        minutes=5,
                        id='worker_prioridad_batch',
                        replace_existing=True,
                    )
                except Exception as e:
                    _scheduler = None
                    print(f"[Scheduler] Error al configurar APScheduler: {e}")
    return _scheduler


def iniciar_scheduler():
    global _worker_active
    if _worker_active:
        return False

    try:
        scheduler = obtener_scheduler()
        scheduler.start()
        _worker_active = True
        print("[Scheduler] Scheduler de prioridad iniciado.")
        return True
    except Exception as e:
        print(f"[Scheduler] Error al iniciar: {e}")
        return False


def detener_scheduler():
    global _scheduler, _worker_active
    _worker_active = False
    if _scheduler:
        try:
            _scheduler.shutdown()
            print("[Scheduler] Scheduler detenido.")
        except Exception as e:
            print(f"[Scheduler] Error al detener: {e}")
        finally:
            _scheduler = None
