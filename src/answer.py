import csv
from db import crear_tabla_crudos, insertar_crudo

def cargar_csv_a_db(path_csv):
    crear_tabla_crudos()

    with open(path_csv, newline='', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)

        for fila in lector:
            # Obtener y sanitizar cada campo
            sexo = fila.get("sexo", "").strip() or None
            edad = fila.get("edad", "").strip()
            edad = int(edad) if edad.isdigit() else None
            edad_años_meses = fila.get("edad_años_meses", "").strip() or None
            residencia_pais = fila.get("residencia_pais_nombre", "").strip() or None
            residencia_prov = fila.get("residencia_provincia_nombre", "").strip() or None
            residencia_dpto = fila.get("residencia_departamento_nombre", "").strip() or None
            carga_prov = fila.get("carga_provincia_nombre", "").strip() or None
            fallecido = fila.get("fallecido", "").strip() or None
            arm = fila.get("asistencia_respiratoria_mecanica", "").strip() or None
            financiamiento = fila.get("origen_financiamiento", "").strip() or None
            clasificacion = fila.get("clasificacion", "").strip() or None
            fecha_diag = fila.get("fecha_diagnostico", "").strip() or None

            insertar_crudo(
                sexo, edad, edad_años_meses,
                residencia_pais, residencia_prov, residencia_dpto,
                carga_prov, fallecido, arm,
                financiamiento, clasificacion, fecha_diag
            )
