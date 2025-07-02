from db import conectar
import math

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
    mostrar_tabla("intervalos_fallecidos_varones", "fa")



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
