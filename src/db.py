import sqlite3

DB_NAME = "data.db"

def conectar():
    return sqlite3.connect(DB_NAME)



def crear_tabla_crudos():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros_crudos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sexo TEXT,
                edad INTEGER,
                edad_años_meses TEXT,
                residencia_pais_nombre TEXT,
                residencia_provincia_nombre TEXT,
                residencia_departamento_nombre TEXT,
                carga_provincia_nombre TEXT,
                fallecido TEXT,
                asistencia_respiratoria_mecanica TEXT,
                origen_financiamiento TEXT,
                clasificacion TEXT,
                fecha_diagnostico TEXT
            )
        ''')
        conn.commit()

def insertar_crudo(
    sexo, edad, edad_años_meses,
    residencia_pais_nombre, residencia_provincia_nombre, residencia_departamento_nombre,
    carga_provincia_nombre, fallecido, asistencia_respiratoria_mecanica,
    origen_financiamiento, clasificacion, fecha_diagnostico
):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO registros_crudos (
                sexo, edad, edad_años_meses,
                residencia_pais_nombre, residencia_provincia_nombre, residencia_departamento_nombre,
                carga_provincia_nombre, fallecido, asistencia_respiratoria_mecanica,
                origen_financiamiento, clasificacion, fecha_diagnostico
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sexo, edad, edad_años_meses,
            residencia_pais_nombre, residencia_provincia_nombre, residencia_departamento_nombre,
            carga_provincia_nombre, fallecido, asistencia_respiratoria_mecanica,
            origen_financiamiento, clasificacion, fecha_diagnostico
        ))
        conn.commit()


def obtener_crudos():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros_crudos")
        return cursor.fetchall()

def borrar_tabla_crudos():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registros_crudos")
        conn.commit()