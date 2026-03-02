import os
import json
import csv

# Configuración de rutas
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data')

def asegurar_carpeta():
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

def guardar_formatos_planos(nombre, precio, cantidad):
    asegurar_carpeta()
    
    # 1. Persistencia TXT (Uso de open)
    with open(os.path.join(DATA_PATH, "datos.txt"), "a", encoding="utf-8") as f:
        f.write(f"{nombre}, {precio}, {cantidad}\n")

    # 2. Persistencia JSON (Librería json + diccionario)
    ruta_json = os.path.join(DATA_PATH, "datos.json")
    datos_json = []
    if os.path.exists(ruta_json) and os.path.getsize(ruta_json) > 0:
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos_json = json.load(f)
    
    datos_json.append({"nombre": nombre, "precio": precio, "cantidad": cantidad})
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(datos_json, f, indent=4)

    # 3. Persistencia CSV (Librería csv)
    ruta_csv = os.path.join(DATA_PATH, "datos.csv")
    existe = os.path.isfile(ruta_csv)
    with open(ruta_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["Nombre", "Precio", "Cantidad"])
        writer.writerow([nombre, precio, cantidad])