import os
from os import system
import csv
import sqlite3
import math

''' TOOLS.PY '''
def limpiar():
    '''
    Limpia la consola dependiendo del sistema operativo en donde se esté ejecutando.
    '''

    if os.name == "nt":
        system("cls")
    else:
        system("clear")

def limpiar_str(valor):
    '''
    Limpia un valor de texto: quita espacios, lo convierte a mayúsculas y devuelve None si queda vacío.
    '''
    if valor is None:
        return None
    limpio = valor.strip().upper()
    return limpio if limpio else None


def seguir():
    '''
    Pregunta al usuario si quiere volver al menú o quiere salir del programa.
    Si quiere volver al menú devuelve True, si quiere salir devuelve False.
    '''


    aux = True

    while True:
        if aux == True:
            opc = int(input("\nElija una opción: \n 1. Volver al menú \n 2. Salir \n"))
        else:
            opc = int(input("\nElija una opción válida: \n 1. Volver al menú \n 2. Salir \n"))
            aux = True

        match opc:
            case 1:
                return True
            case 2:
                return False
            case _:
                aux = False

''' DB.PY '''
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

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros_crudos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fila_csv INTEGER UNIQUE,
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
    errores = 0

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

        except sqlite3.IntegrityError:
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
                except Exception:
                    errores += 1 

    if errores > 0:
        print(f"{errores} errores inesperados al insertar.")

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


''' LOADER.PY '''
def cargar_csv_a_db(path_csv, tam_lote=1000):
    '''
    Invoca a crear_tabla_crudos() que se asegura que exista, para poder guardar datos en ella.

    Abre el archivo y se fija cuantos registros hay (sin contar las cabeceras)
    
    Vuelve a abrir el archivo y crea una variable para cada campo, utiliza la función .limpiar_str()
    para limpiar los string (les hace un .upper() y un .strip()), si es un dato nulo lo rellena con un None, 
    para luego insertarlos en la tabla como un registro.

    También muestra un mensaje en consola que se actualiza cada 1000 registros, y otros
    mensajes cuando termina, informando cuantos registros fueron añadidos, cuantos dupplicados se ignoraron
    y el total actual de registros en la base de datos.
    '''

    crear_tabla_crudos()

    with open(path_csv, newline='', encoding='utf-8') as f:
        total = sum(1 for _ in f) - 1

    
    lote = []
    cargados_antes = contar_registros()
    duplicados = 0

    with open(path_csv, newline='', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)

        for i, fila in enumerate(lector, start=1):
            sexo = limpiar_str(fila.get("sexo"))
            edad = fila.get("edad", "").strip()
            edad = int(edad) if edad.isdigit() else None
            edad_años_meses = limpiar_str(fila.get("edad_años_meses"))
            residencia_pais = limpiar_str(fila.get("residencia_pais_nombre"))
            residencia_prov = limpiar_str(fila.get("residencia_provincia_nombre"))
            residencia_dpto = limpiar_str(fila.get("residencia_departamento_nombre"))
            carga_prov = limpiar_str(fila.get("carga_provincia_nombre"))
            fallecido = limpiar_str(fila.get("fallecido"))
            arm = limpiar_str(fila.get("asistencia_respiratoria_mecanica"))
            financiamiento = limpiar_str(fila.get("origen_financiamiento"))
            clasificacion = limpiar_str(fila.get("clasificacion"))
            fecha_diag = limpiar_str(fila.get("fecha_diagnostico"))

            lote.append((
                i, sexo, edad, edad_años_meses,
                residencia_pais, residencia_prov, residencia_dpto,
                carga_prov, fallecido, arm,
                financiamiento, clasificacion, fecha_diag
            ))

            if i % tam_lote == 0 or i == total:
                duplicados += insertar_crudo(lote)
                porcentaje = (i / total) * 100
                print(f"Cargando: {i} de {total} ({porcentaje:.2f}%)", end='\r')
                lote = []

    cargados_despues = contar_registros()
    nuevos = cargados_despues - cargados_antes
    print(f"\nCarga finalizada. Nuevos registros insertados: {nuevos}")
    print(f"Registros duplicados ignorados: {duplicados}")
    print(f"Total en base de datos: {cargados_despues}")


''' CLEANNING.PY '''
def crear_registros_limpios():
    '''
    Crea una nueva tabla `registros_limpios` a partir de `registros_crudos`, aplicando:
    - Conversión de edad en meses a años
    - Eliminación de edades inválidas (>130 años o >120 meses)
    - Corrección de valores "SIN ESPECIFICAR" en residencia_pais_nombre
    - Simplificación de clasificacion
    - Eliminación de residencia_departamento_nombre y edad_años_meses.
    - Eliminación de fecha_diagnostico.
    '''

    provincias_arg = {
        "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CÓRDOBA",
        "CORRIENTES", "ENTRE RÍOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA",
        "MENDOZA", "MISIONES", "NEUQUÉN", "RÍO NEGRO", "SALTA", "SAN JUAN",
        "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO",
        "TUCUMÁN"
    }

    with conectar() as conn:
        cursor = conn.cursor()

        # Eliminar tabla si existe
        cursor.execute('DROP TABLE IF EXISTS registros_limpios')

        # Crea la tabla nueva
        cursor.execute('''
            CREATE TABLE registros_limpios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fila_csv INTEGER UNIQUE,
                sexo TEXT,
                edad INTEGER,
                residencia_pais_nombre TEXT,
                residencia_provincia_nombre TEXT,
                carga_provincia_nombre TEXT,
                fallecido TEXT,
                asistencia_respiratoria_mecanica TEXT,
                origen_financiamiento TEXT,
                clasificacion TEXT
            )
        ''')

        # Conteo total original
        cursor.execute('SELECT COUNT(*) FROM registros_crudos')
        total_original = cursor.fetchone()[0]

        # Conteo con edad nula o fuera de rango
        cursor.execute('''
            SELECT COUNT(*) FROM registros_crudos
            WHERE edad IS NULL OR
                  (edad_años_meses = 'MESES' AND edad > 120) OR
                  (edad_años_meses != 'MESES' AND edad > 130)
        ''')
        total_descartados = cursor.fetchone()[0]

        cursor.execute('''
            INSERT INTO registros_limpios (
                fila_csv, sexo, edad, residencia_pais_nombre, residencia_provincia_nombre,
                carga_provincia_nombre, fallecido, asistencia_respiratoria_mecanica,
                origen_financiamiento, clasificacion
            )
            SELECT
                rc.fila_csv,
                rc.sexo,
                CASE
                    WHEN rc.edad_años_meses = 'MESES' AND rc.edad IS NOT NULL THEN CAST(rc.edad / 12 AS INT)
                    ELSE rc.edad
                END AS edad,
                CASE
                    WHEN rc.residencia_pais_nombre = 'SIN ESPECIFICAR'
                         AND UPPER(rc.residencia_provincia_nombre) IN ({})
                         THEN 'ARGENTINA'
                    ELSE rc.residencia_pais_nombre
                END AS residencia_pais_nombre,
                rc.residencia_provincia_nombre,
                rc.carga_provincia_nombre,
                rc.fallecido,
                rc.asistencia_respiratoria_mecanica,
                rc.origen_financiamiento,
                CASE
                    WHEN rc.clasificacion LIKE '%DESCARTADO%' THEN 'DESCARTADO'
                    WHEN rc.clasificacion LIKE '%CONFIRMADO%' THEN 'CONFIRMADO'
                    WHEN rc.clasificacion LIKE '%SOSPECHOSO%' THEN 'SOSPECHOSO'
                    ELSE rc.clasificacion
                END AS clasificacion
            FROM registros_crudos rc
            WHERE rc.edad IS NOT NULL AND (
                (rc.edad_años_meses = 'MESES' AND rc.edad <= 120) OR
                (rc.edad_años_meses != 'MESES' AND rc.edad <= 130)
            )
        '''.format(','.join(f"'{prov}'" for prov in provincias_arg)))

        conn.commit()

    print("\nTabla registros_limpios creada exitosamente.")
    print(f"Registros descartados por edad nula o fuera de rango: {total_descartados} de {total_original} ({(total_descartados / total_original) * 100:.2f}%)")


''' ANSWER.PY '''
poblacion_provincias = {
    'BUENOS AIRES': 17541141,
    'CABA': 3075646,
    'CATAMARCA': 429562,
    'CHACO': 1142025,
    'CHUBUT': 603120,
    'CÓRDOBA': 3874893,
    'CORRIENTES': 1216615,
    'ENTRE RÍOS': 1432425,
    'FORMOSA': 606041,
    'JUJUY': 797730,
    'LA PAMPA': 366022,
    'LA RIOJA': 384607,
    'MENDOZA': 2092860,
    'MISIONES': 1213344,
    'NEUQUÉN': 726590,
    'RÍO NEGRO': 762067,
    'SALTA': 1441351,
    'SAN JUAN': 818234,
    'SAN LUIS': 540903,
    'SANTA CRUZ': 337226,
    'SANTA FE': 3531351,
    'SANTIAGO DEL ESTERO': 1060832,
    'TIERRA DEL FUEGO': 190641,
    'TUCUMÁN': 1694651
}

def describir_variables():
    '''
    Ya que no hay tantas columnas, y el archivo no es variable, podemos
    hacer el análisis de numerica/categorica de forma """manual""" guardandolo
    como pares ordenados en la lista columnas.

    Después mediante consultas SQL se verifica cuantos registros hay en la tabla,
    cuantos nulos y no nulos hay por columna.

    Y dependiendo del tipo de variable (categorica o numerica) va a sacar más 
    información; si es numérica va sacar el RANGO y el PROMEDIO; pero si es
    categorica muestra cuantos valores DISTINTOS ENTRE SI puede tomar la variable
    y su frecuencia (ignorando los nulos).
    '''

    columnas = [
        ("sexo", "categorica"),
        ("edad", "numerica"),
        ("edad_años_meses", "categorica"),
        ("residencia_pais_nombre", "categorica"),
        ("residencia_provincia_nombre", "categorica"),
        ("residencia_departamento_nombre", "categorica"),
        ("carga_provincia_nombre", "categorica"),
        ("fallecido", "categorica"),
        ("asistencia_respiratoria_mecanica", "categorica"),
        ("origen_financiamiento", "categorica"),
        ("clasificacion", "categorica"),
        ("fecha_diagnostico", "categorica")
    ]

    with conectar() as conn:
        cursor = conn.cursor()

        for col, tipo in columnas:
            print(f"\n--- {col.upper()} ({tipo}) ---")

            # Total y nulos
            cursor.execute(f"SELECT COUNT(*) FROM registros_crudos")
            total = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM registros_crudos WHERE {col} IS NULL")
            nulos = cursor.fetchone()[0]
            no_nulos = total - nulos

            print(f"Total registros: {total}")
            print(f"No nulos: {no_nulos}")
            print(f"Nulos: {nulos}")

            if tipo == "numerica":
                cursor.execute(f"SELECT MIN({col}), MAX({col}), AVG({col}) FROM registros_crudos WHERE {col} IS NOT NULL")
                minimo, maximo, promedio = cursor.fetchone()
                print(f"Rango: {minimo} - {maximo}")
                print(f"Promedio: {round(promedio, 2) if promedio is not None else 'N/A'}")

            elif tipo == "categorica":
                cursor.execute(f'''
                    SELECT {col}, COUNT(*) as freq
                    FROM registros_crudos
                    WHERE {col} IS NOT NULL
                    GROUP BY {col}
                    ORDER BY freq DESC
                    LIMIT 10
                ''')
                filas = cursor.fetchall()
                print(f"Valores más frecuentes:")
                for valor, freq in filas:
                    print(f"  {valor or '[VACÍO]'}: {freq} veces")

def describir_variables_limpias():
    '''
    Imprime estadísticas y resumen para cada variable de la tabla registros_limpios.
    '''
    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM registros_limpios')
        total = cursor.fetchone()[0]
        print("\nDESCRIPCIÓN DE VARIABLES EN registros_limpios")
        print("───────────────────────────────────────────────")

        columnas = [
            ("sexo", True),
            ("edad", False),
            ("residencia_pais_nombre", True),
            ("residencia_provincia_nombre", True),
            ("carga_provincia_nombre", True),
            ("fallecido", True),
            ("asistencia_respiratoria_mecanica", True),
            ("origen_financiamiento", True),
            ("clasificacion", True),
            #("fecha_diagnostico", True)
        ]

        for col, es_categorica in columnas:
            print(f"\n--- {col.upper()} ({'categorica' if es_categorica else 'numerica'}) ---")
            cursor.execute(f'SELECT COUNT(*) FROM registros_limpios WHERE {col} IS NOT NULL')
            no_nulos = cursor.fetchone()[0]
            nulos = total - no_nulos
            print(f"Total registros: {total}")
            print(f"No nulos: {no_nulos}")
            print(f"Nulos: {nulos}")

            if es_categorica:
                cursor.execute(f'''
                    SELECT {col}, COUNT(*)
                    FROM registros_limpios
                    GROUP BY {col}
                    ORDER BY COUNT(*) DESC
                    LIMIT 10
                ''')
                print("Valores más frecuentes:")
                for valor, freq in cursor.fetchall():
                    print(f"  {valor}: {freq} veces")
            else:
                cursor.execute(f'SELECT MIN({col}), MAX({col}), AVG({col}) FROM registros_limpios')
                minimo, maximo, promedio = cursor.fetchone()
                print(f"Rango: {minimo} - {maximo}")
                print(f"Promedio: {promedio:.2f}")


def edad_promedio_fallecidos_por_provincia():
    '''
    Calcula y muestra la edad promedio de fallecidos por provincia,
    ordenada de mayor a menor edad promedio.
    '''

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                residencia_provincia_nombre,
                ROUND(AVG(edad), 2) AS edad_promedio,
                COUNT(*) AS cantidad_fallecidos
            FROM registros_limpios
            WHERE fallecido = 'SI' AND edad IS NOT NULL
            GROUP BY residencia_provincia_nombre
            ORDER BY edad_promedio DESC
        ''')
        resultados = cursor.fetchall()

    print("\nEdad promedio de fallecidos por provincia:")
    print("─────────────────────────────────────────────────────────────────────")
    for provincia, promedio, cantidad in resultados:
        print(f"{provincia:<25} Edad promedio: {promedio:>5} años  |  Fallecidos: {cantidad}")



def crear_tabla_intervalos_detallados(nombre_tabla, filtro_sql):
    '''
    Crea una tabla de intervalos con estadísticas detalladas:
    - nombre_tabla: nombre de la tabla a crear
    - filtro_sql: condición WHERE para filtrar los registros (ej: "clasificacion = 'CONFIRMADO'")
    '''

    with conectar() as conn:
        cursor = conn.cursor()

        # Si ya existe, omitir
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{nombre_tabla}'")
        if cursor.fetchone():
            print(f"La tabla '{nombre_tabla}' ya existe. Se omite su creación.")
            return

        # Obtener datos base
        cursor.execute(f'''
            SELECT COUNT(*), MIN(edad), MAX(edad)
            FROM registros_limpios
            WHERE edad IS NOT NULL AND {filtro_sql}
        ''')
        n, edad_min, edad_max = cursor.fetchone()

        k = math.ceil(1 + 3.322 * math.log10(n))
        amplitud = math.ceil((edad_max - edad_min + 1) / k)

        print(f"Creando tabla '{nombre_tabla}' con {k} intervalos (amplitud: {amplitud})")

        # Crear tabla
        cursor.execute(f"DROP TABLE IF EXISTS {nombre_tabla}")
        cursor.execute(f'''
            CREATE TABLE {nombre_tabla} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                desde INTEGER,
                hasta INTEGER,
                fa INTEGER,
                fr REAL,
                frp REAL,
                fa_acum_asc INTEGER,
                fr_acum_asc REAL,
                frp_acum_asc REAL,
                fa_acum_desc INTEGER,
                fr_acum_desc REAL,
                frp_acum_desc REAL
            )
        ''')

        # Construir intervalos
        intervalos = []
        for i in range(k):
            desde = edad_min + i * amplitud
            hasta = desde + amplitud
            cursor.execute(f'''
                SELECT COUNT(*) FROM registros_limpios
                WHERE edad >= ? AND edad < ? AND {filtro_sql}
            ''', (desde, hasta))
            fa = cursor.fetchone()[0]
            fr = fa / n
            frp = fr * 100
            intervalos.append({'desde': desde, 'hasta': hasta, 'fa': fa, 'fr': fr, 'frp': frp})

        # Acumulados ascendentes
        fa_acum_asc = 0
        fr_acum_asc = 0.0
        for intervalo in intervalos:
            fa_acum_asc += intervalo['fa']
            fr_acum_asc += intervalo['fr']
            intervalo['fa_acum_asc'] = fa_acum_asc
            intervalo['fr_acum_asc'] = fr_acum_asc
            intervalo['frp_acum_asc'] = fr_acum_asc * 100

        # Acumulados descendentes
        fa_acum_desc = 0
        fr_acum_desc = 0.0
        for intervalo in reversed(intervalos):
            fa_acum_desc += intervalo['fa']
            fr_acum_desc += intervalo['fr']
            intervalo['fa_acum_desc'] = fa_acum_desc
            intervalo['fr_acum_desc'] = fr_acum_desc
            intervalo['frp_acum_desc'] = fr_acum_desc * 100

        # Insertar en la tabla
        for intervalo in intervalos:
            cursor.execute(f'''
                INSERT INTO {nombre_tabla} (
                    desde, hasta, fa, fr, frp,
                    fa_acum_asc, fr_acum_asc, frp_acum_asc,
                    fa_acum_desc, fr_acum_desc, frp_acum_desc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                intervalo['desde'], intervalo['hasta'], intervalo['fa'], intervalo['fr'], intervalo['frp'],
                intervalo['fa_acum_asc'], intervalo['fr_acum_asc'], intervalo['frp_acum_asc'],
                intervalo['fa_acum_desc'], intervalo['fr_acum_desc'], intervalo['frp_acum_desc']
            ))

        conn.commit()
        print(f"Tabla '{nombre_tabla}' creada correctamente con {k} intervalos.")



def crear_intervalos_confirmados_y_fallecidos():
    crear_tabla_intervalos_detallados("intervalos_confirmados", "clasificacion = 'CONFIRMADO'")
    crear_tabla_intervalos_detallados("intervalos_fallecidos", "clasificacion = 'CONFIRMADO' AND fallecido = 'SI'")



def mostrar_tabla_intervalos(nombre_tabla):
    '''
    Muestra por consola la tabla de intervalos con estadísticas detalladas.
    Al final, informa el intervalo con mayor cantidad de registros (frecuencia absoluta).
    '''

    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute(f'''
            SELECT
                desde, hasta, fa, fr, frp,
                fa_acum_asc, fr_acum_asc, frp_acum_asc,
                fa_acum_desc, fr_acum_desc, frp_acum_desc
            FROM {nombre_tabla}
            ORDER BY desde ASC
        ''')
        filas = cursor.fetchall()

        cursor.execute(f'''
            SELECT desde, hasta, fa
            FROM {nombre_tabla}
            ORDER BY fa DESC
            LIMIT 1
        ''')
        intervalo_max = cursor.fetchone()

    print(f"\nTabla: {nombre_tabla}")
    print("─" * 100)
    print(f"{'Intervalo':<15} {'FA':>6} {'FR':>8} {'FR%':>8} "
          f"{'FAA↑':>7} {'FRA↑':>8} {'FR%A↑':>9} "
          f"{'FAD↓':>7} {'FRD↓':>8} {'FR%D↓':>9}")
    print("─" * 100)

    for fila in filas:
        desde, hasta, fa, fr, frp, faa, fra, frpa, fad, frd, frpd = fila
        intervalo = f"{desde}-{hasta - 1}"
        print(f"{intervalo:<15} {fa:>6} {fr:>8.4f} {frp:>8.2f} "
              f"{faa:>7} {fra:>8.4f} {frpa:>9.2f} "
              f"{fad:>7} {frd:>8.4f} {frpd:>9.2f}")

    print("─" * 100)

    if intervalo_max:
        desde, hasta, fa = intervalo_max
        print(f"Intervalo con mayor cantidad de registros: {desde}-{hasta - 1} ({fa} casos)")

def crear_intervalos_fallecidos_por_sexo(k=0):
    '''
    Crea dos tablas:
    - intervalos_fallecidas_mujeres
    - intervalos_fallecidos_varones

    Utiliza Sturges si k=0, o el valor dado de k.
    '''
    with conectar() as conn:
        cursor = conn.cursor()

        # Total fallecidos por sexo
        cursor.execute("SELECT COUNT(*) FROM registros_limpios WHERE sexo = 'F' AND fallecido = 'SI'")
        total_f = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM registros_limpios WHERE sexo = 'M' AND fallecido = 'SI'")
        total_m = cursor.fetchone()[0]

        # Rango de edad
        cursor.execute("SELECT MIN(edad), MAX(edad) FROM registros_limpios WHERE fallecido = 'SI'")
        edad_min, edad_max = cursor.fetchone()

        # Cálculo de k si no se pasa
        if k <= 0:
            cursor.execute("SELECT COUNT(*) FROM registros_limpios WHERE fallecido = 'SI'")
            total_fallecidos = cursor.fetchone()[0]
            k = math.ceil(1 + 3.322 * math.log10(total_fallecidos))

        amplitud = math.ceil((edad_max - edad_min + 1) / k)

        # Borra tablas anteriores si existen
        cursor.execute("DROP TABLE IF EXISTS intervalos_fallecidas_mujeres")
        cursor.execute("DROP TABLE IF EXISTS intervalos_fallecidos_varones")

        cursor.execute('''
            CREATE TABLE intervalos_fallecidas_mujeres (
                desde INTEGER,
                hasta INTEGER,
                fa INTEGER,
                fr REAL,
                frp REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE intervalos_fallecidos_varones (
                desde INTEGER,
                hasta INTEGER,
                fa INTEGER,
                fr REAL,
                frp REAL
            )
        ''')

        # Insertar intervalos
        for i in range(k):
            desde = edad_min + i * amplitud
            hasta = desde + amplitud

            # Mujeres
            cursor.execute('''
                SELECT COUNT(*) FROM registros_limpios
                WHERE sexo = 'F' AND fallecido = 'SI' AND edad >= ? AND edad < ?
            ''', (desde, hasta))
            fa_f = cursor.fetchone()[0]
            fr_f = fa_f / total_f if total_f else 0
            frp_f = fr_f * 100

            cursor.execute('''
                INSERT INTO intervalos_fallecidas_mujeres (desde, hasta, fa, fr, frp)
                VALUES (?, ?, ?, ?, ?)
            ''', (desde, hasta, fa_f, fr_f, frp_f))

            # Varones
            cursor.execute('''
                SELECT COUNT(*) FROM registros_limpios
                WHERE sexo = 'M' AND fallecido = 'SI' AND edad >= ? AND edad < ?
            ''', (desde, hasta))
            fa_m = cursor.fetchone()[0]
            fr_m = fa_m / total_m if total_m else 0
            frp_m = fr_m * 100

            cursor.execute('''
                INSERT INTO intervalos_fallecidos_varones (desde, hasta, fa, fr, frp)
                VALUES (?, ?, ?, ?, ?)
            ''', (desde, hasta, fa_m, fr_m, frp_m))

        conn.commit()

    print("Tablas 'intervalos_fallecidas_mujeres' y 'intervalos_fallecidos_varones' creadas correctamente.")


def mostrar_intervalos_fallecidos_por_sexo():
    '''
    Muestra ambas tablas por consola, indicando el intervalo con más fallecidas
    y el de mayor porcentaje de fallecidos varones.
    '''
    def mostrar_tabla(nombre_tabla, criterio):
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT desde, hasta, fa, fr, frp FROM {nombre_tabla} ORDER BY desde ASC
            ''')
            filas = cursor.fetchall()

            if criterio == "fa":
                cursor.execute(f'''
                    SELECT desde, hasta, fa FROM {nombre_tabla} ORDER BY fa DESC LIMIT 1
                ''')
            else:
                cursor.execute(f'''
                    SELECT desde, hasta, frp FROM {nombre_tabla} ORDER BY frp DESC LIMIT 1
                ''')
            intervalo_max = cursor.fetchone()

        print(f"\nTabla: {nombre_tabla}")
        print("─" * 60)
        print(f"{'Intervalo':<15} {'FA':>6} {'FR':>10} {'FR%':>10}")
        print("─" * 60)

        for desde, hasta, fa, fr, frp in filas:
            print(f"{desde}-{hasta - 1:<13} {fa:>6} {fr:>10.4f} {frp:>10.2f}")

        print("─" * 60)
        if criterio == "fa":
            desde, hasta, fa = intervalo_max
            print(f"Intervalo con mayor número de mujeres fallecidas: {desde}-{hasta - 1} ({fa} casos)")
        else:
            desde, hasta, frp = intervalo_max
            print(f"Intervalo con mayor % de varones fallecidos: {desde}-{hasta - 1} ({frp:.2f}%)")

    mostrar_tabla("intervalos_fallecidas_mujeres", "fa")
    mostrar_tabla("intervalos_fallecidos_varones", "frp")



def crear_casos_confirmados_por_sexo_y_provincia():
    '''
    Crea dos tablas que cuentan los casos confirmados por provincia según sexo:
    - confirmados_mujeres_por_provincia
    - confirmados_varones_por_provincia
    '''

    with conectar() as conn:
        cursor = conn.cursor()

        # Borrar si existen
        cursor.execute("DROP TABLE IF EXISTS confirmados_mujeres_por_provincia")
        cursor.execute("DROP TABLE IF EXISTS confirmados_varones_por_provincia")

        # Crear las tablas
        cursor.execute('''
            CREATE TABLE confirmados_mujeres_por_provincia (
                provincia TEXT,
                cantidad INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE confirmados_varones_por_provincia (
                provincia TEXT,
                cantidad INTEGER
            )
        ''')

        # Mujeres
        cursor.execute('''
            INSERT INTO confirmados_mujeres_por_provincia (provincia, cantidad)
            SELECT residencia_provincia_nombre, COUNT(*) 
            FROM registros_limpios
            WHERE sexo = 'F' AND clasificacion = 'CONFIRMADO'
            GROUP BY residencia_provincia_nombre
        ''')

        # Varones
        cursor.execute('''
            INSERT INTO confirmados_varones_por_provincia (provincia, cantidad)
            SELECT residencia_provincia_nombre, COUNT(*) 
            FROM registros_limpios
            WHERE sexo = 'M' AND clasificacion = 'CONFIRMADO'
            GROUP BY residencia_provincia_nombre
        ''')

        conn.commit()

    print("Tablas 'confirmados_mujeres_por_provincia' y 'confirmados_varones_por_provincia' creadas correctamente.")



def mostrar_casos_confirmados_por_sexo_y_provincia():
    '''
    Muestra por consola los casos confirmados por provincia para mujeres y varones.
    También informa cuál provincia lidera cada caso.
    '''

    def mostrar_tabla(nombre_tabla, sexo):
        with conectar() as conn:
            cursor = conn.cursor()

            cursor.execute(f'''
                SELECT provincia, cantidad FROM {nombre_tabla} ORDER BY cantidad DESC
            ''')
            filas = cursor.fetchall()

            top = filas[0] if filas else ("Desconocido", 0)

        print(f"\nCasos confirmados en {sexo}")
        print("─" * 40)
        print(f"{'Provincia':<25} {'Cantidad':>10}")
        print("─" * 40)
        for provincia, cantidad in filas:
            print(f"{provincia:<25} {cantidad:>10}")
        print("─" * 40)
        print(f"Provincia con más casos en {sexo.lower()}: {top[0]} ({top[1]} casos)")

    mostrar_tabla("confirmados_mujeres_por_provincia", "Mujeres")
    mostrar_tabla("confirmados_varones_por_provincia", "Varones")



def crear_tabla_confirmados_vs_poblacion():
    """
    Crea una tabla temporal en la base de datos con:
    - Provincia
    - Cantidad de casos confirmados
    - Población total (según Censo 2022)
    - Proporción de casos confirmados respecto a la población
    """

    with conectar() as conn:
        cursor = conn.cursor()

        # Eliminar la tabla si ya existe
        cursor.execute("DROP TABLE IF EXISTS confirmados_vs_poblacion")

        # Crear la tabla
        cursor.execute('''
            CREATE TABLE confirmados_vs_poblacion (
                provincia TEXT,
                confirmados INTEGER,
                poblacion INTEGER,
                proporcion REAL
            )
        ''')

        for provincia, poblacion in poblacion_provincias.items():
            cursor.execute('''
                SELECT COUNT(*) FROM registros_limpios
                WHERE clasificacion = 'CONFIRMADO'
                AND residencia_provincia_nombre = ?
            ''', (provincia,))

            confirmados = cursor.fetchone()[0]
            proporcion = confirmados / poblacion if poblacion else 0

            cursor.execute('''
                INSERT INTO confirmados_vs_poblacion (provincia, confirmados, poblacion, proporcion)
                VALUES (?, ?, ?, ?)
            ''', (provincia, confirmados, poblacion, proporcion))

        conn.commit()
        print("Tabla confirmados_vs_poblacion creada correctamente.")


def mostrar_menor_proporcion_confirmados():
    """
    Muestra la provincia con menor proporción de casos confirmados respecto a su población.
    """
    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT provincia, confirmados, poblacion, proporcion
            FROM confirmados_vs_poblacion
            ORDER BY proporcion ASC
            LIMIT 1
        ''')

        menor = cursor.fetchone()

        print("\nProvincia con menor proporción de casos confirmados respecto a su población:")
        print(f"Provincia: {menor[0]}")
        print(f"Confirmados: {menor[1]:,}")
        print(f"Población: {menor[2]:,}")
        print(f"Proporción: {menor[3]:.6f} ({menor[3]*100:.4f}%)")



def crear_tabla_fallecidos_vs_poblacion():
    '''
    Crea una tabla con la proporción de fallecidos respecto a la población total por provincia.
    '''

    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS fallecidos_vs_poblacion")
        cursor.execute("""
            CREATE TABLE fallecidos_vs_poblacion (
                provincia TEXT PRIMARY KEY,
                cantidad_fallecidos INTEGER,
                poblacion_total INTEGER,
                proporcion_fallecidos REAL
            )
        """)

        for provincia, poblacion in poblacion_provincias.items():
            cursor.execute("""
                SELECT COUNT(*) FROM registros_limpios
                WHERE fallecido = 'SI' AND residencia_provincia_nombre = ?
            """, (provincia,))
            fallecidos = cursor.fetchone()[0]
            proporcion = fallecidos / poblacion if poblacion > 0 else 0
            cursor.execute("""
                INSERT INTO fallecidos_vs_poblacion (provincia, cantidad_fallecidos, poblacion_total, proporcion_fallecidos)
                VALUES (?, ?, ?, ?)
            """, (provincia, fallecidos, poblacion, proporcion))

        conn.commit()
        print("Tabla fallecidos_vs_poblacion creada correctamente.")


def mostrar_mayor_proporcion_fallecidos():
    '''
    Muestra la provincia con mayor proporción de fallecidos respecto a su población.
    '''

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT provincia, cantidad_fallecidos, poblacion_total, proporcion_fallecidos
            FROM fallecidos_vs_poblacion
            ORDER BY proporcion_fallecidos DESC
            LIMIT 1
        """)
        fila = cursor.fetchone()

    if fila:
        print("\nProvincia con mayor proporción de fallecidos respecto a la población:")
        print(f"Provincia: {fila[0]}")
        print(f"Cantidad de fallecidos: {fila[1]}")
        print(f"Población total: {fila[2]}")
        print(f"Proporción: {fila[3]*100:.4f}%")
    else:
        print("No se encontraron datos para mostrar.")


def calcular_indice_confirmados_por_sexo():
    '''
    Calcula el índice de confirmados por sexo y muestra en consola cuál tiene el mayor índice.
    '''
    with conectar() as conn:
        cursor = conn.cursor()

        # Obtenemos total y confirmados por sexo
        cursor.execute('''
            SELECT 
                sexo,
                COUNT(*) AS total,
                SUM(CASE WHEN clasificacion = 'CONFIRMADO' THEN 1 ELSE 0 END) AS confirmados
            FROM registros_limpios
            WHERE sexo IN ('F', 'M')
            GROUP BY sexo
        ''')

        resultados = cursor.fetchall()

    print("\nÍndice de casos confirmados por sexo:\n")
    print("Sexo | Total | Confirmados | Índice")
    print("----------------------------------------")

    max_indice = -1
    sexo_max = None

    for sexo, total, confirmados in resultados:
        indice = confirmados / total if total else 0
        print(f"{sexo:>4} | {total:>5} | {confirmados:>11} | {indice:.4f}")

        if indice > max_indice:
            max_indice = indice
            sexo_max = sexo

    print("\nEl mayor índice de casos confirmados lo tiene:", "Mujeres" if sexo_max == 'F' else "Varones")
    print("Se utilizó como índice: confirmados / total por sexo.")



''' MAIN.PY '''
# Cargar tabla con datos semi-crudos

limpiar()
cargar_csv_a_db("./file/Covid19Casos.csv")


# Se crea una nueva tabla con los datos limpios
crear_registros_limpios()


# Se crean tablas para las consignas
crear_intervalos_confirmados_y_fallecidos()
crear_intervalos_fallecidos_por_sexo()
crear_casos_confirmados_por_sexo_y_provincia()
crear_tabla_confirmados_vs_poblacion()
crear_tabla_fallecidos_vs_poblacion()


# MENÚ

primera_vez = False
bol = False
seg = True

while seg:
    if primera_vez:
        limpiar()
    else:
        primera_vez = True

    if bol == False:
        print("\n================= Menú =================\n")
    else:
        print("Elija una opción válida: n")
        bol = False

    print("Opción 1: Descripción de las variables.")
    print("Opción 2: Descripción de las variables ya limpios.") # Es el único que no coincide del todo con la consigna
    print("Opción 3: Promedio de edad de los fallecidos por Provencia.")
    print("Opción 4: Tabla Sturges - Intervalos de edad - Casos confirmados y fallecidos.")
    print("Opción 5: Tablas fallecidos hombres y mujeres según edad.")
    print("Opción 6: Provincia con más confirmados por sexo.")
    print("Opción 7: Jurisdicción con menor proporción de casos confirmados.")
    print("Opción 8: Jurisdicción con mayor proporción de fallecidos.")
    print("Opción 9: Proporción de casos confirmados en hombres y mujeres.")
    print("Opción 0: Salir \n")

    op = int(input("¿Que desea ver? \n"))

    match op:
        case 0:
            seg = False
        case 1:
            limpiar()
            describir_variables()
            seg = seguir()
        case 2:
            limpiar()
            describir_variables_limpias()
            seg = seguir()
        case 3:
            limpiar()
            edad_promedio_fallecidos_por_provincia()
            seg = seguir()
        case 4:
            limpiar()
            mostrar_tabla_intervalos("intervalos_confirmados")
            mostrar_tabla_intervalos("intervalos_fallecidos")
            seg = seguir()
        case 5:
            limpiar()
            mostrar_intervalos_fallecidos_por_sexo()
            seg = seguir()
        case 6:
            limpiar()
            mostrar_casos_confirmados_por_sexo_y_provincia()
            seg = seguir()
        case 7:
            limpiar()
            mostrar_menor_proporcion_confirmados()
            seg = seguir()
        case 8:
            limpiar()
            mostrar_mayor_proporcion_fallecidos()
            seg = seguir()
        case 9:
            limpiar()
            calcular_indice_confirmados_por_sexo()
            seg = seguir()
        case _:
            bol = True
            limpiar()