import csv
import sqlite3
from collections import Counter
import os

DB_PATH = "data.db"
CSV_PATH = "./file/Covid19Casos.csv"

CAMPOS_SIN_ID = [
    "sexo", "edad", "edad_años_meses",
    "residencia_pais_nombre", "residencia_provincia_nombre", "residencia_departamento_nombre",
    "carga_provincia_nombre", "fallecido", "asistencia_respiratoria_mecanica",
    "origen_financiamiento", "clasificacion", "fecha_diagnostico"
]

def leer_registros_csv():
    registros = []
    errores = 0
    with open(CSV_PATH, newline='', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            try:
                registro = tuple((fila[campo] or "").strip() for campo in CAMPOS_SIN_ID)
                if len(registro) != len(CAMPOS_SIN_ID):
                    errores += 1
                    continue
                registros.append(registro)
            except Exception:
                errores += 1
    return registros, errores

def leer_registros_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    campos_str = ", ".join(CAMPOS_SIN_ID)
    cursor.execute(f"SELECT {campos_str} FROM registros_crudos")
    registros = [tuple((str(val).strip() if val is not None else "") for val in fila) for fila in cursor.fetchall()]
    conn.close()
    return registros

def comparar():
    if not os.path.exists(CSV_PATH):
        print("⚠️ Archivo CSV no encontrado.")
        return
    if not os.path.exists(DB_PATH):
        print("⚠️ Base de datos no encontrada.")
        return

    print("📥 Leyendo registros del CSV...")
    registros_csv, errores_csv = leer_registros_csv()
    total_csv = len(registros_csv)

    print("💾 Leyendo registros de la base de datos...")
    registros_db = leer_registros_db()
    total_db = len(registros_db)

    print("📊 Contando duplicados en el CSV...")
    contador_csv = Counter(registros_csv)
    duplicados_csv = sum(cant - 1 for cant in contador_csv.values() if cant > 1)
    unicos_csv = len(contador_csv)

    print("🧮 Comparando coincidencias con base de datos...")
    set_csv = set(contador_csv.keys())
    set_db = set(registros_db)
    en_csv_y_en_db = set_csv & set_db
    faltantes = set_csv - set_db

    print("\n📋 INFORME DE COMPARACIÓN")
    print("────────────────────────────────────")
    print(f"📄 Registros válidos en CSV:              {total_csv}")
    print(f"📦 Registros únicos en CSV:              {unicos_csv}")
    print(f"🔁 Registros duplicados en CSV:          {duplicados_csv}")
    print(f"❌ Filas con errores en el CSV:           {errores_csv}")
    print(f"💾 Registros en la base de datos:         {total_db}")
    print(f"✅ Registros en CSV que ya están en DB:   {len(en_csv_y_en_db)}")
    print(f"🚫 Registros únicos del CSV que NO están en DB: {len(faltantes)}")
    print("────────────────────────────────────")

    if len(faltantes) == 0:
        print("✅ Todos los registros únicos del CSV están en la base de datos.")
    else:
        print("⚠️ Algunos registros del CSV no están en la base. Puede haber error en la carga o estar fuera del índice UNIQUE.")

if __name__ == "__main__":
    comparar()
