from db import conectar
import math

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
            ("fecha_diagnostico", True)
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
            print(f"\nLa tabla '{nombre_tabla}' ya existe. Se omite su creación.")
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

        print(f"\nCreando tabla '{nombre_tabla}' con {k} intervalos (amplitud: {amplitud})")

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

