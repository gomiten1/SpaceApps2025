import math
import pandas as pd
import json
from funcionJSON import generarScoresHabitat

MAPA_VISUAL = {
    'PRIVATE': '[P]', 'HYGIENE': '[H]', 'WASTE': '[W]', 'EXERCISE': '[E]',
    'FOOD': '[F]', 'MAINTENANCE': '[M]', 'SCIENCE': '[S]', 'MEDICAL': '[+]',
    'SOCIAL': '[T]', 'LOGISTICS': '[L]', 'AIRLOCK': '[A]', 'MISSION PLANNING': '[G]',
    'DEFAULT': '[?]'
}

def visualizarLayoutEnTerminal(celdas, width, height):
    """Crea y muestra una representación 2D del layout en la terminal."""
    # Crea un grid vacío
    grid = [[' . ' for _ in range(width)] for _ in range(height)]
    
    # Coloca los módulos en el grid
    for celda in celdas:
        x, y = celda['x'], celda['y']
        if 0 <= x < width and 0 <= y < height:
            char = MAPA_VISUAL.get(celda['type'], MAPA_VISUAL['DEFAULT'])
            grid[y][x] = char
            
    # Imprime el grid con un borde
    print("+" + "---" * width + "+")
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "---" * width + "+")

def etiquetarDatos(archivoJsonEntrada, archivoCsvSalida):
    """
    Herramienta principal para el etiquetado de datos.
    """
    try:
        with open(archivoJsonEntrada, 'r') as f:
            datosParaEtiquetar = json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de entrada '{archivoJsonEntrada}'")
        return

    datosEtiquetados = []

    print("--- INICIO DEL PROCESO DE ETIQUETADO ---")

    for i, data in enumerate(datosParaEtiquetar):
        layout = data['layout']
        contexto = data['contexto']
        habitatId = layout.get('id', f'habitat_{i+1}')
        celdas = layout.get('cells', [])
        
        print("\n" + "="*50)
        print(f"Revisando Hábitat: {habitatId}")
        print(f"Contexto: {contexto}")
        
         # --- VISUALIZADOR EN TERMINAL ---
        visualizarLayoutEnTerminal(celdas, 50, 50)
        
        # --- LISTA DE COMPONENTES CON VOLUMEN ---
        print("\nMódulos presentes (Tipo - Volumen):")
        for c in celdas:
            vol = c['props'].get('volumen', 'N/A')
            print(f"  - {c['type']:<15} | Volumen: {vol} m³")
        print("-"*50)

        # Pedir calificación al experto
        calificacionExperto = -1
        while not (0 <= calificacionExperto <= 100):
            try:
                respuesta = input(f"Introduce tu calificación (0-100) para '{habitatId}': ")
                calificacionExperto = int(respuesta)
            except ValueError:
                print("Error: Por favor, introduce un número entero.")

        # Calcular los scores automáticos
        scoresCalculados = generarScoresHabitat(layout, contexto)
        
        # Añadir la calificación del experto (normalizada de 0 a 1)
        scoresCalculados['calificacionExperto'] = calificacionExperto / 100.0
        
        datosEtiquetados.append(scoresCalculados)
        print(f"'{habitatId}' etiquetado con un score de {calificacionExperto}.")

    # Exportar a CSV
    df = pd.DataFrame(datosEtiquetados)
    df.to_csv(archivoCsvSalida, index=False)
    print(f"\n Proceso completado. Dataset guardado en '{archivoCsvSalida}'")

if __name__ == '__main__':
    archivoJsonEntrada = 'training_layouts_v2.json'
    archivoCsvSalida = 'dataset_etiquetado.csv'
    etiquetarDatos(archivoJsonEntrada, archivoCsvSalida)