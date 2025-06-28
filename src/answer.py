import csv
from db import crear_tabla_crudos, insertar_crudo, conectar, contar_registros
from tools import limpiar_str as limpiar

def cargar_csv_a_db(path_csv, tam_lote=1000):
    '''
    Invoca a crear_tabla_crudos() que se asegura que exista, para poder guardar datos en ella.

    Abre el archivo y se fija cuantos registros hay (sin contar las cabeceras)
    
    Vuelve a abrir el archivo y crea una variable para cada campo les hace un .strip()
    o deja un None (para que sea más fácil trabajar con ellos después), para luego
    insertarlos en la tabla como un registro.

    También muestra un mensaje en consola que se actualiza cada 1000 registros, y otro
    mensaje cuando termina.
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
            sexo = limpiar(fila.get("sexo"))
            edad = fila.get("edad", "").strip()
            edad = int(edad) if edad.isdigit() else None
            edad_años_meses = limpiar(fila.get("edad_años_meses"))
            residencia_pais = limpiar(fila.get("residencia_pais_nombre"))
            residencia_prov = limpiar(fila.get("residencia_provincia_nombre"))
            residencia_dpto = limpiar(fila.get("residencia_departamento_nombre"))
            carga_prov = limpiar(fila.get("carga_provincia_nombre"))
            fallecido = limpiar(fila.get("fallecido"))
            arm = limpiar(fila.get("asistencia_respiratoria_mecanica"))
            financiamiento = limpiar(fila.get("origen_financiamiento"))
            clasificacion = limpiar(fila.get("clasificacion"))
            fecha_diag = limpiar(fila.get("fecha_diagnostico"))

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



def describir_variables():
    '''
    Ya que no hay tantas columnas, y el archivo no es variable, podemos
    hacer el análisis de numerica/categorica de forma """manual"""guardandolo
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
