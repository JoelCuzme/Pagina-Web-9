import json
import csv
import os

# Configuración de rutas de archivos
DATA_DIR = "inventario/data"
TXT_FILE = os.path.join(DATA_DIR, "datos.txt")
JSON_FILE = os.path.join(DATA_DIR, "datos.json")
CSV_FILE = os.path.join(DATA_DIR, "datos.csv")

class InventarioManager:
    @staticmethod
    def guardar_txt(nombre, precio, cantidad):
        with open(TXT_FILE, "a") as f:
            f.write(f"Producto: {nombre}, Precio: {precio}, Cantidad: {cantidad}\n")

    @staticmethod
    def guardar_json(nombre, precio, cantidad):
        datos = []
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r") as f:
                datos = json.load(f)
        
        datos.append({"nombre": nombre, "precio": precio, "cantidad": cantidad})
        
        with open(JSON_FILE, "w") as f:
            json.dump(datos, f, indent=4)

    @staticmethod
    def guardar_csv(nombre, precio, cantidad):
        file_exists = os.path.isfile(CSV_FILE)
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Nombre", "Precio", "Cantidad"])
            writer.writerow([nombre, precio, cantidad])