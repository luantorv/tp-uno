import sqlite3
import csv
import os

DB_PATH = "data.db"
CSV_PATH = "./file/Covid19Casos.csv"

# Campos a considerar para detectar duplicados exactos
CAMPOS_SIN_ID = [
    "sexo", "edad", "edad_años_meses",
    "residencia_pais_nombre", "residencia_provincia_nombre", "residencia_departamento_nombre",
    "carga_provincia_nombre", "fallecido", "asistencia_respiratoria_mecanica",
    "origen_financiamiento", "clasificacion", "fecha_diagnostico"
]

def contar_csv(path_csv):
    with open(path_csv, newline='', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        filas_validas = sum(1 for _ in lector)
    return filas_validas

def contar_db(path_db):
    conn = sqlite3.connect(path_db)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM registros_crudos")
    total = cursor.fetchone()[0]

    campos_str = ", ".join(CAMPOS_SIN_ID)
    cursor.execute(f'''
        SELECT COUNT(*) FROM (
            SELECT DISTINCT {campos_str}
            FROM registros_crudos
        )
    ''')
    distintos = cursor.fetchone()[0]


    conn.close()
    return total, distintos

def verificar():
    if not os.path.exists(DB_PATH):
        print("⚠️ No se encontró la base de datos.")
        return
    if not os.path.exists(CSV_PATH):
        print("⚠️ No se encontró el archivo CSV.")
        return

    total_csv = contar_csv(CSV_PATH)
    total_db, distintos_db = contar_db(DB_PATH)

    duplicados = total_db - distintos_db

    print(f"\n📊 VERIFICACIÓN DE CARGA")
    print(f"────────────────────────────")
    print(f"✔️ Registros válidos en el CSV:         {total_csv}")
    print(f"✔️ Registros totales en la base:        {total_db}")
    print(f"✔️ Registros distintos en la base:      {distintos_db}")
    print(f"🔁 Registros duplicados detectados:     {duplicados}")
    print(f"────────────────────────────")

    if total_csv == total_db:
        print("✅ Todo en orden: CSV y base tienen igual cantidad de registros.")
    elif total_db < total_csv:
        print(f"⚠️ Faltan {total_csv - total_db} registros en la base.")
    else:
        print(f"⚠️ Hay {total_db - total_csv} registros EXTRA en la base.")

    if duplicados > 0:
        print("⚠️ Hay registros duplicados exactos en la base. Considerá eliminarlos.")

if __name__ == "__main__":
    verificar()
