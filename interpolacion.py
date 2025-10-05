import json

# === Datos base de volúmenes para 4 y 6 tripulantes ===
modules_data = [
    {"module": "EXERCISE MODULES 1", "volume_4": 6.12, "volume_6": 12.24},
    {"module": "EXERCISE MODULES 2", "volume_4": 3.38, "volume_6": 6.76},
    {"module": "EXERCISE MODULES 3", "volume_4": 3.92, "volume_6": 7.84},
    {"module": "SOCIAL/RECREATION MODULES 1", "volume_4": 18.20, "volume_6": 27.30},
    {"module": "SOCIAL/RECREATION MODULES 2", "volume_4": 10.09, "volume_6": 15.14},
    {"module": "HYGIENE MODULES", "volume_4": 4.35, "volume_6": 8.70},
    {"module": "WASTE MANAGEMENT MODULES", "volume_4": 2.36, "volume_6": 4.72},
    {"module": "LOGISTICS MODULES", "volume_4": 6.00, "volume_6": 6.00},
    {"module": "MAINTENANCE MODULES 1", "volume_4": 3.40, "volume_6": 3.40},
    {"module": "MAINTENANCE MODULES 2", "volume_4": 4.82, "volume_6": 4.82},
    {"module": "FOOD MODULES 1", "volume_4": 4.35, "volume_6": 8.70},
    {"module": "FOOD MODULES 2", "volume_4": 3.30, "volume_6": 3.30},
    {"module": "MEDICAL MODULES 1", "volume_4": 1.20, "volume_6": 1.20},
    {"module": "MEDICAL MODULES 2", "volume_4": 5.80, "volume_6": 5.80},
    {"module": "MISSION PLANNING MODULE", "volume_4": 3.42, "volume_6": 3.42},
    {"module": "PRIVATE HABITATION MODULES 1", "volume_4": 17.40, "volume_6": 26.10},
    {"module": "PRIVATE HABITATION MODULES 2", "volume_4": 13.96, "volume_6": 20.94},
    {"module": "SCIENCE MODULE", "volume_4": 5.00, "volume_6": 7.50},
    {"module": "AIRLOCK MODULE", "volume_4": 3.76, "volume_6": 3.76}
]

# === Función de interpolación ===
def interpolar_valores(valor_4, valor_6, n_tripulantes):
    if n_tripulantes == 4:
        return valor_4
    elif n_tripulantes == 6:
        return valor_6
    else:
        pendiente = (valor_6 - valor_4) / (6 - 4)
        return valor_4 + pendiente * (n_tripulantes - 4)

# === Generar JSON con datos interpolados ===
def generar_datos_habitat(n_tripulantes):
    layout = []
    for m in modules_data:
        volumen = interpolar_valores(m["volume_4"], m["volume_6"], n_tripulantes)
        layout.append({
            "module": m["module"],
            "tripulantes": n_tripulantes,
            "volumen_estimado_m3": round(volumen, 2)
        })
    return layout

# === Guardar a JSON ===
def exportar_a_json(data, filename="volumen_interpolado.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Archivo guardado: {filename}")

# === Ejemplo de uso ===
if __name__ == "__main__":
    crew_size = int(input("Ingrese el número de tripulantes: "))
    datos = generar_datos_habitat(crew_size)
    exportar_a_json(datos)
    print(json.dumps(datos, indent=2, ensure_ascii=False))
