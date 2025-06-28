import sqlite3

DB_NAME = "data.db"

def conectar():
    '''
    Crea la conección a la Base de Datos y la devuelve.
    '''

    return sqlite3.connect(DB_NAME)



def crear_tabla_crudos():
    '''
    Se asegura que exista la tabla registros_crudos en la Base de Datos.
    '''
    duplicados = 0

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros_crudos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fila_csv INTEGER,
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

def insertar_crudo(registro):
    '''
    Inserta registros en la tabla registros_crudos.
    Si ocurre un IntegrityError en el lote, intenta insertar individualmente cada fila
    para no perder todo el lote.
    '''

    duplicados = 0

    with conectar() as conn:
        cursor = conn.cursor()
        try:
            cursor.executemany('''
                INSERT INTO registros_crudos (
                    fila_csv, sexo, edad, edad_años_meses,
                    residencia_pais_nombre, residencia_provincia_nombre, residencia_departamento_nombre,
                    carga_provincia_nombre, fallecido, asistencia_respiratoria_mecanica,
                    origen_financiamiento, clasificacion, fecha_diagnostico
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', registro)
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"⚠️ Lote falló. Intentando insertar fila por fila. Error: {e}")
            for fila in registro:
                try:
                    cursor.execute('''
                        INSERT INTO registros_crudos (
                            fila_csv, sexo, edad, edad_años_meses,
                            residencia_pais_nombre, residencia_provincia_nombre, residencia_departamento_nombre,
                            carga_provincia_nombre, fallecido, asistencia_respiratoria_mecanica,
                            origen_financiamiento, clasificacion, fecha_diagnostico
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', fila)
                    conn.commit()
                except sqlite3.IntegrityError:
                    duplicados += 1
    return duplicados

def eliminar_duplicados_crudos():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM registros_crudos
            WHERE ROWID NOT IN (
                SELECT MIN(ROWID)
                FROM registros_crudos
                GROUP BY
                    sexo, edad, edad_años_meses,
                    residencia_pais_nombre, residencia_provincia_nombre, residencia_departamento_nombre,
                    carga_provincia_nombre, fallecido, asistencia_respiratoria_mecanica,
                    origen_financiamiento, clasificacion, fecha_diagnostico
            )
        ''')
        conn.commit()

def contar_registros():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM registros_crudos")
        return cursor.fetchone()[0]

def obtener_crudos():
    '''
    Devuelve la tabla registros_crudos
    '''

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros_crudos")
        return cursor.fetchall()

def borrar_tabla_crudos():
    '''
    Borra la tabla registros_crudos. No creo que sea necesario, pero por si las dudas lo dejo acá.
    '''

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registros_crudos")
        conn.commit()