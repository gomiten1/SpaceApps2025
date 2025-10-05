import math
import pandas as pd



HABITAT_WIDTH_M = 100
HABITAT_HEIGHT_M = 100

MODULOS_ESENCIALES = [
    'FOOD', 'HYGIENE', 'MEDICAL', 'PRIVATE HABITATION', 
    'WASTE MANAGEMENT', 'AIRLOCK'
]

PONDERACIONES = {
    "checklist": 3.0,
    "masaTotal": 1.5,
    "eficienciaVolumen": 1.2,
    "proteccionRadiacion": 2.0,
    "zonificacion": 2.5,
    "adyacencias": 1.0,
    "privacidad": 1.5,
    "sostenibilidad": 0.8,
}


def cargarChecklistDict(path='checklist.csv'):
    columnas = [
        'hay_modulos_ejercicio',
        'hay_modulos_social_recreacion',
        'hay_modulos_alimentos',
        'hay_modulos_higiene',
        'hay_modulos_medicos',
        'hay_modulos_habitacion_privada',
        'hay_modulos_mantenimiento',
        'hay_modulos_planeación_de_misiones',
        'hay_modulos_gestion_residuos',
        'hay_modulos_logistica',
        'hay_modulos_laboratorio',
        'hay_modulos_airlock'
    ]
    df = pd.read_csv(path)
    return {
        tuple(row[col] for col in columnas): row['resultado']
        for _, row in df.iterrows()
    }

CHECKLIST_DICT = cargarChecklistDict()

def calcularScoreBaseChecklist(modulos):
    columnas = [
        'hay_modulos_ejercicio',
        'hay_modulos_social_recreacion',
        'hay_modulos_alimentos',
        'hay_modulos_higiene',
        'hay_modulos_medicos',
        'hay_modulos_habitacion_privada',
        'hay_modulos_mantenimiento',
        'hay_modulos_planeación_de_misiones',
        'hay_modulos_gestion_residuos',
        'hay_modulos_logistica',
        'hay_modulos_laboratorio',
        'hay_modulos_airlock'
    ]
    moduloACol = {
        'EXERCISE': 'hay_modulos_ejercicio',
        'SOCIAL/RECREATION': 'hay_modulos_social_recreacion',
        'FOOD': 'hay_modulos_alimentos',
        'HYGIENE': 'hay_modulos_higiene',
        'MEDICAL': 'hay_modulos_medicos',
        'PRIVATE HABITATION': 'hay_modulos_habitacion_privada',
        'MAINTENANCE': 'hay_modulos_mantenimiento',
        'MISSION PLANNING': 'hay_modulos_planeación_de_misiones',
        'WASTE MANAGEMENT': 'hay_modulos_gestion_residuos',
        'LOGISTICS': 'hay_modulos_logistica',
        'LABORATORY': 'hay_modulos_laboratorio',
        'AIRLOCK': 'hay_modulos_airlock'
    }
    presencia = {col: 0.0 for col in columnas}
    for m in modulos:
        nombre = m['modulo'].upper()
        if nombre in moduloACol:
            presencia[moduloACol[nombre]] = 1.0
    key = tuple(presencia[col] for col in columnas)
    return CHECKLIST_DICT.get(key, 0.0)


def calcularScoreMasaYVolumen(modulos):
    if not modulos:
        return {"scoreMasa": 0, "scoreEficienciaVolumen": 0}

    masaTotal = sum(m['atributos']['masa'] for m in modulos)
    volumenOcupado = sum(m['atributos']['volumen'] for m in modulos)
    scoreMasa = max(0, 1 - (masaTotal / 10000))
    areaTotal = HABITAT_WIDTH_M * HABITAT_HEIGHT_M
    volumenHabitable = areaTotal - volumenOcupado
    scoreVolumen = math.log10(1 + max(0, volumenHabitable))
    scoreEficienciaVolumen = min(1, scoreVolumen / 2)
    return {
        "scoreMasa": scoreMasa,
        "scoreEficienciaVolumen": scoreEficienciaVolumen
    }

def calcularScoreProteccionYDurabilidad(modulos):
    if not modulos:
        return {"scoreProteccionRadiacion": 0}
    totalResistencia = sum(m['atributos']['resistenciaRadiacion'] for m in modulos)
    scoreRadiacion = totalResistencia / len(modulos)
    scoreProteccionRadiacion = min(1, scoreRadiacion / 10)
    return {"scoreProteccionRadiacion": scoreProteccionRadiacion}

def calcularScoreLayoutZonificacion(modulos):
    puntosLimpios = [ (m['x'], m['y']) for m in modulos if not m['atributos']['ensuciable'] ]
    puntosSucios = [ (m['x'], m['y']) for m in modulos if m['atributos']['ensuciable'] ]
    if not puntosLimpios or not puntosSucios:
        return {"scoreZonificacion": 0.5}
    cxLimpio = sum(p[0] for p in puntosLimpios) / len(puntosLimpios)
    cyLimpio = sum(p[1] for p in puntosLimpios) / len(puntosLimpios)
    cxSucio = sum(p[0] for p in puntosSucios) / len(puntosSucios)
    cySucio = sum(p[1] for p in puntosSucios) / len(puntosSucios)
    distancia = math.sqrt((cxLimpio - cxSucio)**2 + (cyLimpio - cySucio)**2)
    maxDist = math.sqrt(HABITAT_WIDTH_M**2 + HABITAT_HEIGHT_M**2)
    scoreZonificacion = min(1, distancia / (maxDist * 0.75))
    return {"scoreZonificacion": scoreZonificacion}

def calcularScoreBienestarPsicologico(modulos):
    modulosPrivados = [m for m in modulos if m['modulo'] == 'PRIVATE HABITATION']
    modulosRuidosos = [m for m in modulos if m['modulo'] in ['SOCIAL/RECREATION', 'EXERCISE']]
    if not modulosPrivados or not modulosRuidosos:
        return {"scorePrivacidad": 0.5}
    distanciasTotales = 0
    for priv in modulosPrivados:
        distARuido = sum(math.sqrt((priv['x'] - r['x'])**2 + (priv['y'] - r['y'])**2) for r in modulosRuidosos)
        distanciasTotales += distARuido / len(modulosRuidosos)
    distanciaPromedio = distanciasTotales / len(modulosPrivados)
    maxDist = math.sqrt(HABITAT_WIDTH_M**2 + HABITAT_HEIGHT_M**2)
    scorePrivacidad = min(1, distanciaPromedio / (maxDist * 0.5))
    return {"scorePrivacidad": scorePrivacidad}

def calcularScoreSostenibilidad(modulos):
    if not modulos:
        return {"scoreSostenibilidad": 0}
    scoreMaterial = 0
    for m in modulos:
        material = m['atributos']['tipoMaterial']
        if material == 'ISRU-derivado':
            scoreMaterial += 1.0
        elif material == 'Compuesto':
            scoreMaterial += 0.6
        elif material == 'Aluminio':
            scoreMaterial += 0.2
    scoreSostenibilidad = (scoreMaterial / len(modulos))
    return {"scoreSostenibilidad": scoreSostenibilidad}

def calcularPuntuacionTotalHabitat(habitatLayout):
    subScores = {}
    subScores.update(calcularScoreMasaYVolumen(habitatLayout))
    subScores.update(calcularScoreProteccionYDurabilidad(habitatLayout))
    subScores.update(calcularScoreLayoutZonificacion(habitatLayout))
    subScores.update(calcularScoreBienestarPsicologico(habitatLayout))
    subScores.update(calcularScoreSostenibilidad(habitatLayout))
    scoreChecklist = calcularScoreBaseChecklist(habitatLayout)
    subScores['scoreChecklist'] = scoreChecklist

    puntuacionFinal = 0
    sumaPesos = 0
    if scoreChecklist > 0:
        for key, score in subScores.items():
            keyCamel = key.replace("score", "").lower()
            if keyCamel in PONDERACIONES:
                puntuacionFinal += score * PONDERACIONES[keyCamel]
                sumaPesos += PONDERACIONES[keyCamel]
    if sumaPesos > 0:
        puntuacionFinal /= sumaPesos
    return puntuacionFinal, subScores


# --- EJEMPLO DE USO ---
if __name__ == '__main__':
    miHabitatEjemplo = [
        {'modulo': 'FOOD', 'x': 2, 'y': 8, 'atributos': {'masa': 200, 'volumen': 10, 'ensuciable': True, 'permanencia': 0.8, 'tipoMaterial': 'Compuesto', 'resistenciaRadiacion': 5}},
        {'modulo': 'SOCIAL/RECREATION', 'x': 3, 'y': 7, 'atributos': {'masa': 100, 'volumen': 15, 'ensuciable': False, 'permanencia': 0.7, 'tipoMaterial': 'Compuesto', 'resistenciaRadiacion': 5}},
        {'modulo': 'PRIVATE HABITATION', 'x': 9, 'y': 2, 'atributos': {'masa': 150, 'volumen': 12, 'ensuciable': False, 'permanencia': 0.9, 'tipoMaterial': 'Compuesto', 'resistenciaRadiacion': 6}},
        {'modulo': 'HYGIENE', 'x': 8, 'y': 8, 'atributos': {'masa': 100, 'volumen': 8, 'ensuciable': True, 'permanencia': 0.8, 'tipoMaterial': 'Aluminio', 'resistenciaRadiacion': 4}},
        {'modulo': 'WASTE MANAGEMENT', 'x': 9, 'y': 9, 'atributos': {'masa': 50, 'volumen': 5, 'ensuciable': True, 'permanencia': 0.9, 'tipoMaterial': 'Aluminio', 'resistenciaRadiacion': 4}},
        {'modulo': 'EXERCISE', 'x': 8, 'y': 6, 'atributos': {'masa': 120, 'volumen': 9, 'ensuciable': True, 'permanencia': 0.7, 'tipoMaterial': 'Compuesto', 'resistenciaRadiacion': 5}},
        {'modulo': 'MEDICAL', 'x': 2, 'y': 2, 'atributos': {'masa': 80, 'volumen': 7, 'ensuciable': False, 'permanencia': 0.95, 'tipoMaterial': 'Compuesto', 'resistenciaRadiacion': 6}},
        {'modulo': 'AIRLOCK', 'x': 0, 'y': 5, 'atributos': {'masa': 300, 'volumen': 10, 'ensuciable': True, 'permanencia': 0.9, 'tipoMaterial': 'Aluminio', 'resistenciaRadiacion': 7}},
        {'modulo': 'mesa', 'x': 4, 'y': 7, 'atributos': {'masa': 30, 'volumen': 4, 'ensuciable': False, 'permanencia': 0.9, 'tipoMaterial': 'Compuesto', 'resistenciaRadiacion': 5}}
    ]
    MODULOS_ESENCIALES = ['FOOD', 'HYGIENE', 'PRIVATE HABITATION', 'WASTE MANAGEMENT', 'AIRLOCK', 'MEDICAL']
    puntuacion, desglose = calcularPuntuacionTotalHabitat(miHabitatEjemplo)
    print("="*50)
    print("      ANÁLISIS DE PUNTUACIÓN DEL HÁBITAT")
    print("="*50)
    import json
    print(json.dumps(desglose, indent=4))
    print("-"*50)
    print(f"PUNTUACIÓN MAESTRA FINAL: {puntuacion:.2f} / 1.0")
    print("="*50)