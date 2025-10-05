import json
import random
from pathlib import Path

# --- CONFIGURACIÓN ---

# Lista de posibles tipos de módulos (se añade MISSION PLANNING)
MODULE_TYPES = [
    "PRIVATE", "HYGIENE", "WASTE", "EXERCISE", "FOOD", "MAINTENANCE",
    "SCIENCE", "MEDICAL", "SOCIAL", "LOGISTICS", "AIRLOCK", "MISSION PLANNING"
]

# Lista de posibles materiales estructurales
STRUCTURAL_MATERIALS = ["METAL", "AUTONOMO", "INFLABLE", "COMPUESTO"]

# --- DICCIONARIO DE VOLÚMENES POR MÓDULO ---
VOLUME_OPTIONS = {
    "EXERCISE": [3.38, 6.12, 3.92],
    "SOCIAL": [18.20, 10.09, 4.62],
    "FOOD": [10.09, 4.35, 3.30],
    "HYGIENE": [4.35, 2.34, 2.18],
    "MEDICAL": [5.80, 3.40, 1.20],
    "PRIVATE": [10.76, 4.35, 4.80],
    "MAINTENANCE": [4.35, 1.70],
    "MISSION PLANNING": [3.42, 10.09],
    "WASTE": [2.36, 3.76],
    "LOGISTICS": [6.00, 4.35],
    "SCIENCE": [4.35],
    "AIRLOCK": [4.62] # Solo se proporcionó un valor para este módulo
}


# --- REGLAS PARA OTRAS PROPIEDADES (props) ---

# Reglas de limpieza por tipo de módulo
LIMPIEZA_RULES = {
    "PRIVATE": 1.0, "FOOD": 1.0, "SCIENCE": 1.0, "MEDICAL": 1.0,
    "MAINTENANCE": 0.5, "MISSION PLANNING": 0.5
}

# Reglas de permanencia por tipo de módulo
PERMANENCIA_RULES = {
    "PRIVATE": 1, "SCIENCE": 1, "FOOD": 1
}


def generate_props(module_type: str) -> dict:
    """Genera el diccionario 'props' para un tipo de módulo específico."""
    # Elige un volumen aleatorio de la lista de opciones para ese tipo de módulo
    possible_volumes = VOLUME_OPTIONS.get(module_type, [0.0]) # Devuelve [0.0] si el módulo no está en la lista
    random_volume = random.choice(possible_volumes)
    
    return {
        "masa": 0.0,
        "volumen": random_volume,
        "costo": 0.0,
        "limpieza": LIMPIEZA_RULES.get(module_type, 0.0),
        "permanencia": PERMANENCIA_RULES.get(module_type, 0)
    }

# Temporalmente reducido a 50x50 para el labeler
# para que funcione en terminal
# Revisar si cambiar a 100x100 luego
def generate_cell(module_type: str) -> dict:
    """Crea un único diccionario de celda con coordenadas aleatorias."""
    return {
        "x": random.randint(0, 50),
        "y": random.randint(0, 50),
        "type": module_type,
        "props": generate_props(module_type)
    }

def generate_habitat_layout(layout_id: int) -> dict:
    """Genera un layout de hábitat completo con su contexto y celdas."""
    
    # 1. Generar el contexto aleatoriamente
    crew_size = random.randint(2, 8)
    contexto = {
        "cantidadTripulacion": crew_size,
        "materialEstructural": random.choice(STRUCTURAL_MATERIALS),
        "resistenciaRadiacion": random.randint(3, 10)
    }
    
    # 2. Generar las celdas
    cells = []
    
    # Regla 1: Asegurar que haya igual o más módulos PRIVATE que tripulación
    num_private_modules = random.randint(crew_size, crew_size + 2)
    for _ in range(num_private_modules):
        cells.append(generate_cell("PRIVATE"))
        
    # Regla 2: Asegurar que haya por lo menos uno de CADA OTRO tipo de módulo
    other_modules = [mtype for mtype in MODULE_TYPES if mtype != "PRIVATE"]
    for module_type in other_modules:
        cells.append(generate_cell(module_type))
        
    # 3. Ensamblar la estructura final del layout
    layout_data = {
        "layout": {
            "id": f"habitat_generated_{layout_id}",
            "cells": cells
        },
        "contexto": contexto
    }
    
    return layout_data


if __name__ == "__main__":
    # Cantidad de layouts que quieres generar para tu dataset
    NUM_LAYOUTS_TO_GENERATE = 100
    
    print(f"Generando {NUM_LAYOUTS_TO_GENERATE} layouts...")
    
    # Crear la lista de todos los layouts
    all_layouts = [generate_habitat_layout(i) for i in range(NUM_LAYOUTS_TO_GENERATE)]
    
    # Guardar la lista completa en un archivo JSON
    output_path = Path("training_layouts_v2.json")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(all_layouts, f, indent=2, ensure_ascii=False)
        
    print(f" ¡Éxito! Se ha guardado el dataset en el archivo: {output_path}")