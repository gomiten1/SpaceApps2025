import math
import pandas as pd
import json

# --- 1. CONFIGURACIÓN GLOBAL ---

# Dimensiones del hábitat en tiles
# Temporalmente reducido a 50x50 para el labeler
# para que funcione en terminal
HABITAT_WIDTH_M = 50
HABITAT_HEIGHT_M = 50


# --- 2. FUNCIONES DE CÁLCULO DE SCORES ---

def _normalize(value, minVal, maxVal):
    """Normaliza un valor a una escala de 0 a 1."""
    if maxVal == minVal: return 0.5
    value = max(minVal, min(value, maxVal))
    return (value - minVal) / (maxVal - minVal)

COLUMNAS_CHECKLIST = [
    'hay_modulos_ejercicio', 'hay_modulos_social_recreacion', 'hay_modulos_alimentos',
    'hay_modulos_higiene', 'hay_modulos_medicos', 'hay_modulos_habitacion_privada',
    'hay_modulos_mantenimiento', 'hay_modulos_planeacion_de_misiones', 'hay_modulos_gestion_residuos',
    'hay_modulos_logistica', 'hay_modulos_laboratorio', 'hay_modulos_airlock'
]

# Diccionario con los datos del CSV. La clave es una tupla de 1s y 0s.
CHECKLIST_DICT = {
    (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1): 1,
    (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1): 0.90,
    (0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1): 0.75,
    (1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1): 0.85,
    (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1): 0.70,
    (1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1): 0.55,
    (1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1): 0.55,
    (1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1): 0.90,
    (1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1): 0.90,
    (1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1): 0.60
}


def calcularScoreChecklist(celdas, cantidadTripulacion):
    """
    Calcula el score base verificando la combinación de módulos presentes
    contra el diccionario de checklist interno.
    """
    mapa_tipo_a_columna = {
        'EXERCISE': 'hay_modulos_ejercicio',
        'SOCIAL': 'hay_modulos_social_recreacion',
        'FOOD': 'hay_modulos_alimentos',
        'HYGIENE': 'hay_modulos_higiene',
        'MEDICAL': 'hay_modulos_medicos',
        'PRIVATE': 'hay_modulos_habitacion_privada',
        'MAINTENANCE': 'hay_modulos_mantenimiento',
        'MISSION PLANNING': 'hay_modulos_planeacion_de_misiones',
        'WASTE': 'hay_modulos_gestion_residuos',
        'LOGISTICS': 'hay_modulos_logistica',
        'SCIENCE': 'hay_modulos_laboratorio',
        'AIRLOCK': 'hay_modulos_airlock'
    }

    presencia = {col: 0 for col in COLUMNAS_CHECKLIST}
    tipos_presentes = {c['type'] for c in celdas}

    for tipo, columna in mapa_tipo_a_columna.items():
        if tipo in tipos_presentes:
            presencia[columna] = 1
        
    numCamarotes = len([c for c in celdas if c['type'] == 'PRIVATE'])
    if numCamarotes < cantidadTripulacion:
        return 0.0 # Penalización máxima si no hay camas para todos
            
    clave_actual = tuple(presencia[col] for col in COLUMNAS_CHECKLIST)
    
    # Busca la clave en el diccionario. Si no la encuentra, devuelve 0.0.
    return CHECKLIST_DICT.get(clave_actual, 0.0)

def calcularScoresIngenieria(celdas, cantidadTripulacion):
    """Calcula scores de Masa, Volumen."""
    if not celdas:
        return {"scoreMasa": 0, "scoreVolumen": 0, "scoreVolumenPorPersona": 0}

    masaTotal = sum(c['props']['masa'] for c in celdas)
    
    # Menos es mejor para masa
    scoreMasa = max(0, 1 - _normalize(masaTotal, 5000, 50000))
    

    # Más volumen habitable es mejor, con rendimientos decrecientes
    areaTotal = HABITAT_WIDTH_M * HABITAT_HEIGHT_M
    volumenHabitable = areaTotal - len(celdas) # Asumiendo 1 tile = 1 unidad de área
    scoreVolumenLog = math.log10(1 + max(0, volumenHabitable))
    scoreVolumen = _normalize(scoreVolumenLog, 2, 4) # log(100) a log(10000)
    
    areaTotal = HABITAT_WIDTH_M * HABITAT_HEIGHT_M
    volumenHabitable = areaTotal - len(celdas)
    volumenPorPersona = volumenHabitable / cantidadTripulacion if cantidadTripulacion > 0 else 0
    
    # Usamos los valores de los papers: el óptimo está alrededor de 37 m³/persona
    # Premiamos estar cerca de ese ideal, penalizando tanto por debajo como muy por encima.
    scoreVolumenPorPersona = _normalize(volumenPorPersona, 5, 20)
    
    return {"scoreMasa": scoreMasa, "scoreVolumen": scoreVolumen, "scoreVolumenPorPersona": scoreVolumenPorPersona}

def calcularScoresLayout(celdas):
    """Calcula scores espaciales: Zonificación, Adyacencias y Privacidad."""
    # --- Zonificación (Limpio vs. Sucio) ---
    puntosLimpios = [(c['x'], c['y']) for c in celdas if c['props']['limpieza'] == 1.0]
    puntosSucios = [(c['x'], c['y']) for c in celdas if c['props']['limpieza'] == 0.0]
    scoreZonificacion = 0.5
    if puntosLimpios and puntosSucios:
        cxL, cyL = [sum(coords) / len(puntosLimpios) for coords in zip(*puntosLimpios)]
        cxS, cyS = [sum(coords) / len(puntosSucios) for coords in zip(*puntosSucios)]
        distancia = math.sqrt((cxL - cxS)**2 + (cyL - cyS)**2)
        maxDist = math.sqrt(HABITAT_WIDTH_M**2 + HABITAT_HEIGHT_M**2)
        scoreZonificacion = _normalize(distancia, 0, maxDist * 0.75)

    # --- Adyacencias Deseadas ---
    PARES_DESEADOS = [('FOOD', 'SOCIAL'), ('AIRLOCK', 'MAINTENANCE'), ('SCIENCE', 'AIRLOCK'), ('PRIVATE', 'SCIENCE'), ('PRIVATE', 'MEDICINE'), ('PRIVATE', 'FOOD')]
    posiciones = {c['type']: (c['x'], c['y']) for c in celdas}
    scoresPares = []
    for modA, modB in PARES_DESEADOS:
        if modA in posiciones and modB in posiciones:
            dist = math.sqrt((posiciones[modA][0] - posiciones[modB][0])**2 + (posiciones[modA][1] - posiciones[modB][1])**2)
            scoresPares.append(1 / (1 + dist))
    scoreAdyacencias = sum(scoresPares) / len(scoresPares) if scoresPares else 0

    # --- Privacidad ---
    privados = [c for c in celdas if c['type'] == 'PRIVATE']
    ruidosos = [c for c in celdas if c['type'] in ['SOCIAL', 'EXERCISE']]
    scorePrivacidad = 0.5
    if privados and ruidosos:
        distPromedio = sum(math.sqrt((p['x']-r['x'])**2 + (p['y']-r['y'])**2) for p in privados for r in ruidosos) / (len(privados)*len(ruidosos))
        maxDist = math.sqrt(HABITAT_WIDTH_M**2 + HABITAT_HEIGHT_M**2)
        scorePrivacidad = _normalize(distPromedio, 0, maxDist * 0.5)
        
    return {
        "scoreZonificacion": scoreZonificacion, 
        "scoreAdyacencias": scoreAdyacencias,
        "scorePrivacidad": scorePrivacidad
    }

def calcularScoresTecnologicos(celdas):
    """Calcula scores de Sostenibilidad y Autonomía."""
    if not celdas:
        return {"scoreSostenibilidad": 0, "scoreAutonomia": 0}

    # Asumimos que 'permanencia' alta = más autónomo y fiable (menos mantenimiento)
    scorePermanenciaTotal = sum(c['props'].get('permanencia', 1) for c in celdas)
    scoreAutonomia = _normalize(scorePermanenciaTotal / len(celdas), 0, 2)

    
    

    return {
        "scoreAutonomia": scoreAutonomia
    }


def calcularScoreVistaEspacial(celdas):
    """
    Calcula la "amplitud" del hábitat midiendo la línea de visión más larga.
    Concepto: Recompensa los espacios abiertos y penaliza los laberintos.
    Fuente: automatedEvaluation.pdf
    """
    ocupados = {(c['x'], c['y']) for c in celdas}
    maxVistaScore = 0
    
    # Iteramos sobre una muestra de puntos para no tardar demasiado en el hackathon
    for i in range(0, HABITAT_WIDTH_M, 5):
        for j in range(0, HABITAT_HEIGHT_M, 5):
            if (i, j) in ocupados:
                continue

            longitudesDeRayos = []
            # Lanzar rayos en 8 direcciones
            for angulo in range(0, 360, 45):
                rad = math.radians(angulo)
                dx, dy = math.cos(rad), math.sin(rad)
                distancia = 0
                # El paso del rayo es de 1 metro (asumiendo tiles de 1m)
                for paso in range(1, int(HABITAT_WIDTH_M * 1.5)):
                    puntoActual = (int(i + dx * paso), int(j + dy * paso))
                    if puntoActual in ocupados or \
                       not (0 <= puntoActual[0] < HABITAT_WIDTH_M and 0 <= puntoActual[1] < HABITAT_HEIGHT_M):
                        break
                    distancia = paso
                longitudesDeRayos.append(distancia)
            
            vistaPromedioTile = sum(longitudesDeRayos) / 8
            if vistaPromedioTile > maxVistaScore:
                maxVistaScore = vistaPromedioTile

    maxDistPosible = math.sqrt(HABITAT_WIDTH_M**2 + HABITAT_HEIGHT_M**2)
    scoreVistaEspacial = _normalize(maxVistaScore, 0, maxDistPosible / 2) # Normaliza contra la mitad de la diagonal
    
    return {"scoreVistaEspacial": scoreVistaEspacial}


def calcularScoreAreaDeTrabajo(celdas):
    """
    Verifica que los módulos de trabajo tengan espacio libre al frente para operar.
    Concepto: El espacio vacío es funcional si sirve a un propósito, como trabajar.
    Fuente: Internal Layout...ASCEND.pdf
    """
    MODULOS_DE_TRABAJO = ['FOOD', 'MAINTENANCE', 'SCIENCE', 'MEDICAL']
    ocupados = {(c['x'], c['y']) for c in celdas}
    
    workstations = [c for c in celdas if c['type'] in MODULOS_DE_TRABAJO]
    if not workstations:
        return {"scoreAreaDeTrabajo": 0}

    scoresDeWorkstations = []
    for ws in workstations:
        # Simplificación: Verificamos un área de 3x3 alrededor del módulo.
        # Una versión más avanzada consideraría la orientación del módulo.
        areaRequerida = 8 # 8 tiles libres alrededor
        tilesLibres = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                if (ws['x'] + dx, ws['y'] + dy) not in ocupados:
                    tilesLibres += 1
        scoresDeWorkstations.append(tilesLibres / areaRequerida)
        
    scoreAreaDeTrabajo = sum(scoresDeWorkstations) / len(scoresDeWorkstations)
    return {"scoreAreaDeTrabajo": scoreAreaDeTrabajo}


def calcularScoreErgonomia(celdas):
    """
    Puntúa la ubicación de los módulos según su frecuencia de uso.
    Concepto: Lo más usado debe estar en la ubicación más céntrica y accesible.
    Fuente: automatedEvaluation.pdf
    """
    # Frecuencia de uso estimada (1-10)
    FRECUENCIA_USO = {
        'PRIVATE': 10, 'FOOD': 9, 'SOCIAL': 8, 'HYGIENE': 8,
        'WASTE': 7, 'EXERCISE': 7, 'MEDICAL': 5, 'MAINTENANCE': 4,
        'SCIENCE': 6, 'LOGISTICS': 3, 'AIRLOCK': 5, 'MISSION PLANNING': 7
    }
    
    if not celdas:
        return {"scoreErgonomia": 0}
        
    centroHabitat = (HABITAT_WIDTH_M / 2, HABITAT_HEIGHT_M / 2)
    scorePonderadoTotal = 0
    frecuenciaTotal = 0
    
    for c in celdas:
        frecuencia = FRECUENCIA_USO.get(c['type'], 1)
        distAlCentro = math.sqrt((c['x'] - centroHabitat[0])**2 + (c['y'] - centroHabitat[1])**2)
        
        # Un score de centralidad que es alto cuando la distancia es baja
        scoreCentralidad = 1 / (1 + distAlCentro)
        
        scorePonderadoTotal += frecuencia * scoreCentralidad
        frecuenciaTotal += frecuencia
        
    scoreErgonomia = scorePonderadoTotal / frecuenciaTotal if frecuenciaTotal > 0 else 0
    # El score ya está normalizado entre 0 y 1 por la naturaleza del cálculo
    return {"scoreErgonomia": scoreErgonomia}

def calcularScoreSostenibilidad(materialEstructuralGlobal):
    materialScores = {'autonomo': 1.0, 'metal': 0.5, 'compuesto':0.6, 'inflable': 0.2}
    return {"scoreSostenibilidad": materialScores.get(materialEstructuralGlobal, 0.1)}

def calcularScoreProteccionRadiacion(resistenciaRadiacionGlobal):
    return {"scoreProteccionRadiacion": _normalize(resistenciaRadiacionGlobal, 1, 10)}

def generarScoresHabitat(habitatLayout, contextoMision):
    """Orquesta el cálculo de todos los sub-scores para un único hábitat."""
    scores = {'habitatId': habitatLayout.get('id', 'N/A')}
    celdas = habitatLayout.get('cells', [])
    

    cantidadTripulacion = contextoMision.get('cantidadTripulacion', 4)
    materialEstructural = contextoMision.get('materialEstructural', 'INFLABLE')
    resistenciaRadiacion = contextoMision.get('resistenciaRadiacion', 7)
    
    scores['scoreChecklist'] = calcularScoreChecklist(celdas, cantidadTripulacion)
    
    if scores['scoreChecklist'] > 0:
        scores.update(calcularScoresIngenieria(celdas, cantidadTripulacion))
        scores.update(calcularScoresLayout(celdas))
        scores.update(calcularScoresTecnologicos(celdas))
        scores.update(calcularScoreVistaEspacial(celdas))
        scores.update(calcularScoreAreaDeTrabajo(celdas))
        scores.update(calcularScoreErgonomia(celdas))
        scores.update(calcularScoreSostenibilidad(materialEstructural))
        scores.update(calcularScoreProteccionRadiacion(resistenciaRadiacion))
        
    else:
        keys = ["scoreMasa", "scoreVolumen", "scoreZonificacion", 
                "scoreAdyacencias", "scorePrivacidad", "scoreSostenibilidad","scoreAutonomia",
                "scoreVistaEspacial", "scoreAreaDeTrabajo", "scoreErgonomia",
                "scoreProteccionRadiacion", "scoreVolumenPorPersona"]
        for key in keys:
            scores[key] = 0.0
            
    return scores

# Los pesos determinan la importancia de cada métrica en la calificación final.
PONDERACIONES = {
   
    "scoreZonificacion":        2.5,  # Clave para la higiene y calidad de vida.
    "scorePrivacidad":          2.0,  # Vital para la salud mental en misiones largas.
    "scoreAreaDeTrabajo":       2.0,  # Afecta directamente la eficiencia de la tripulación.
    "scoreAdyacencias":         1.8,  # Mide la inteligencia del flujo de trabajo.
    "scoreErgonomia":           1.2,  # Calidad de vida, acceso a lo más usado.
    "scoreVistaEspacial":       0.8,  # Es un "plus", pero menos crítico que otros.

    "scoreProteccionRadiacion": 3.0,  # La seguridad de la tripulación es máxima prioridad.
    "scoreMasa":                1.5,  # La masa es un driver principal del costo.
    "scoreVolumenPorPersona":   1.5,  # Métrica fundamental de habitabilidad.

    "scoreSostenibilidad":      1.0,  # Importante para la visión a largo plazo.
    "scoreAutonomia":           1.2,  # Reduce la carga de trabajo y el riesgo.
}

def calcularCalificacionFinal(subScores):
    """
    Calcula una calificación final de 0 a 100 a partir de un diccionario de sub-scores,
    aplicando una ponderación para cada métrica.
    """
    puntuacionPonderadaTotal = 0.0
    sumaDePesos = 0.0

    for nombreScore, valorScore in subScores.items():
        if nombreScore in PONDERACIONES:
            peso = PONDERACIONES[nombreScore]
            puntuacionPonderadaTotal += valorScore * peso
            sumaDePesos += peso
            
    if sumaDePesos == 0:
        return 0.0
        
    # Normaliza la puntuación ponderada para que vuelva a estar entre 0 y 1
    scoreNormalizado = puntuacionPonderadaTotal / sumaDePesos
    
    # Escala el resultado final a 0-100
    calificacionFinal = scoreNormalizado * 100
    
    return calificacionFinal

def leerHabitatDesdeJsonTiles(path):
    """
    Lee un JSON con estructura:
    {
      "cells": [...],
      "contexto": [{...}]
    }
    y retorna (celdas, contexto) listos para las funciones de scoring.
    """
    with open(path, 'r') as f:
        data = json.load(f)
    celdas = data.get('cells', [])
    # contexto es una lista, tomamos el primer elemento si existe
    contexto = data.get('contexto', [{}])
    if isinstance(contexto, list):
        contexto = contexto[0] if contexto else {}
    return celdas, contexto

# --- 4. EJEMPLO DE USO ---

if __name__ == '__main__':
    ruta_json = "exported_tiles.json"
    celdas, contexto = leerHabitatDesdeJsonTiles(ruta_json)
    scores = generarScoresHabitat({'cells': celdas}, contexto)
    print(scores)
    calificacionFinal = calcularCalificacionFinal(scores)
    print(f"Calificación final: {calificacionFinal:.2f}")
