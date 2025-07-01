from db import conectar

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