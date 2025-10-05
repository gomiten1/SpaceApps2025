import json
from pathlib import Path

MODULE_TEMPLATES = {
"EMPTY": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 0.5, "permanencia": 0},
"PRIVATE": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 1.0, "permanencia": 1},
"HYGIENE": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 0.0, "permanencia": 2},
"WASTE": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 0.0, "permanencia": 2},
"EXERCISE": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 0.0, "permanencia": 1},
"FOOD": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 1.0, "permanencia": 2},
"MAINTENANCE": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 0.5, "permanencia": 2},
"SCIENCE": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 1.0, "permanencia": 0},
"MEDICAL": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 1.0, "permanencia": 0},
"SOCIAL": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 0.0, "permanencia": 0},
"LOGISTICS": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 0.0, "permanencia": 2},
"AIRLOCK": {"masa": 0.0, "volumen": 0.0, "costo": 0.0, "limpieza": 0.0, "permanencia": 2}
}


def process_layout(game_data: dict, output_path: Path):
    """Recibe el diccionario del juego y genera un JSON etiquetado listo para ML."""
    for cell in game_data["cells"]:
        module = cell["type"].upper()
        props = MODULE_TEMPLATES.get(module, MODULE_TEMPLATES["EMPTY"]).copy()
        cell["props"] = props

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(game_data, f, indent=2, ensure_ascii=False)
    print(f"Archivo etiquetado guardado en {output_path}")


if __name__ == "__main__":
    game_output = {
        "cells": [
            {"x": 0, "y": 0, "type": "EMPTY"},
            {"x": 1, "y": 0, "type": "PRIVATE"},
            {"x": 2, "y": 0, "type": "HYGIENE"},
            {"x": 3, "y": 0, "type": "WASTE"},
            {"x": 4, "y": 0, "type": "EXERCISE"},
            {"x": 5, "y": 0, "type": "FOOD"},
            {"x": 6, "y": 0, "type": "MAINTENANCE"},
            {"x": 7, "y": 0, "type": "SCIENCE"},
            {"x": 8, "y": 0, "type": "MEDICAL"},
            {"x": 9, "y": 0, "type": "SOCIAL"},
            {"x": 10, "y": 0, "type": "LOGISTICS"},
            {"x": 11, "y": 0, "type": "AIRLOCK"}
        ]
    }

process_layout(game_output, Path("labeled_layout.json"))