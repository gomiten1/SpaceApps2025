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
    materialScores = {'ISRU-derivado': 1.0, 'Compuesto': 0.6, 'Aluminio': 0.2}
    return {"scoreSostenibilidad": materialScores.get(materialEstructuralGlobal, 0.1)}

def calcularScoreProteccionRadiacion(resistenciaRadiacionGlobal):
    return {"scoreProteccionRadiacion": _normalize(resistenciaRadiacionGlobal, 1, 10)}

def generarScoresHabitat(habitatLayout, contextoMision):
    """Orquesta el cálculo de todos los sub-scores para un único hábitat."""
    scores = {'habitatId': habitatLayout.get('id', 'N/A')}
    celdas = habitatLayout.get('cells', [])
    

    cantidadTripulacion = contextoMision.get('cantidadTripulacion', 4)
    materialEstructural = contextoMision.get('materialEstructural', 'Inflable')
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
                "scoreAdyacencias", "scorePrivacidad", "scoreSostenibilidad"]
        for key in keys:
            scores[key] = 0.0
            
    return scores



# --- 4. EJEMPLO DE USO ---

if __name__ == '__main__':

    layoutEjemplo = {
      "id": "habitat_alpha_v2",
      "cells": [
        {"x": 10, "y": 80, "type": "PRIVATE", "props": {"masa": 1500, "volumen": 12, "costo": 10, "limpieza": 1.0, "permanencia": 1, "tipoMaterial": "Compuesto", "resistenciaRadiacion": 6}},
        {"x": 80, "y": 80, "type": "HYGIENE", "props": {"masa": 1000, "volumen": 8, "costo": 8, "limpieza": 0.0, "permanencia": 2, "tipoMaterial": "Aluminio", "resistenciaRadiacion": 4}},
        {"x": 85, "y": 85, "type": "WASTE", "props": {"masa": 500, "volumen": 5, "costo": 5, "limpieza": 0.0, "permanencia": 2, "tipoMaterial": "Aluminio", "resistenciaRadiacion": 4}},
        {"x": 70, "y": 70, "type": "EXERCISE", "props": {"masa": 1200, "volumen": 10, "costo": 7, "limpieza": 0.0, "permanencia": 1, "tipoMaterial": "Compuesto", "resistenciaRadiacion": 5}},
        {"x": 10, "y": 10, "type": "FOOD", "props": {"masa": 2000, "volumen": 15, "costo": 12, "limpieza": 1.0, "permanencia": 2, "tipoMaterial": "Compuesto", "resistenciaRadiacion": 5}},
        {"x": 50, "y": 50, "type": "MAINTENANCE", "props": {"masa": 400, "volumen": 15, "costo": 4, "limpieza": 0.5, "permanencia": 1, "tipoMaterial": "Aluminio", "resistenciaRadiacion": 5}},
        {"x": 30, "y": 30, "type": "SCIENCE", "props": {"masa": 2500, "volumen": 20, "costo": 20, "limpieza": 1.0, "permanencia": 0, "tipoMaterial": "ISRU-derivado", "resistenciaRadiacion": 8}},
        {"x": 15, "y": 75, "type": "MEDICAL", "props": {"masa": 800, "volumen": 7, "costo": 15, "limpieza": 1.0, "permanencia": 0, "tipoMaterial": "Compuesto", "resistenciaRadiacion": 6}},
        {"x": 20, "y": 15, "type": "SOCIAL", "props": {"masa": 1000, "volumen": 20, "costo": 5, "limpieza": 1.0, "permanencia": 0, "tipoMaterial": "Compuesto", "resistenciaRadiacion": 5}},
        {"x": 5, "y": 50, "type": "AIRLOCK", "props": {"masa": 3000, "volumen": 10, "costo": 25, "limpieza": 0.0, "permanencia": 2, "tipoMaterial": "Aluminio", "resistenciaRadiacion": 7}},
        {"x": 90, "y": 10, "type": "LOGISTICS", "props": {"masa": 600, "volumen": 6, "costo": 6, "limpieza": 0.5, "permanencia": 1, "tipoMaterial": "Aluminio", "resistenciaRadiacion": 4}},
        {"x": 60, "y": 20, "type": "MISSION PLANNING", "props": {"masa": 700, "volumen": 8, "costo": 9, "limpieza": 1.0, "permanencia": 0, "tipoMaterial": "Compuesto", "resistenciaRadiacion": 5}}
      ]
    }
    contextoAlpha = {
        "cantidadTripulacion": 1,
        "materialEstructural": "Compuesto",
        "resistenciaRadiacion": 7
    }

    # Creamos una lista de tuplas, donde cada tupla es (layout, contexto)
    misHabitats = [(layoutEjemplo, contextoAlpha)]

    nombreArchivoSalida = 'exported_tiles.csv'
    dfResultados = pd.DataFrame([generarScoresHabitat(l, c) for l, c in misHabitats])

    #print(f"\n Scores exportados exitosamente a '{nombreArchivoSalida}'")
    print("\n--- Contenido ---")
    print(dfResultados.to_string())
