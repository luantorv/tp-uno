from db import conectar

def crear_registros_limpios():
    '''
    Crea una nueva tabla `registros_limpios` a partir de `registros_crudos`, aplicando:
    - Conversión de edad en meses a años
    - Eliminación de edades inválidas (>110 años o >120 meses)
    - Corrección de valores "SIN ESPECIFICAR" en residencia_pais_nombre
    - Simplificación de clasificacion
    - Eliminación de residencia_departamento_nombre y edad_años_meses.
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
                clasificacion TEXT,
                fecha_diagnostico TEXT
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
                  (edad_años_meses != 'MESES' AND edad > 110)
        ''')
        total_descartados = cursor.fetchone()[0]

        cursor.execute('''
            INSERT INTO registros_limpios (
                fila_csv, sexo, edad, residencia_pais_nombre, residencia_provincia_nombre,
                carga_provincia_nombre, fallecido, asistencia_respiratoria_mecanica,
                origen_financiamiento, clasificacion, fecha_diagnostico
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
                END AS clasificacion,
                rc.fecha_diagnostico
            FROM registros_crudos rc
            WHERE rc.edad IS NOT NULL AND (
                (rc.edad_años_meses = 'MESES' AND rc.edad <= 120) OR
                (rc.edad_años_meses != 'MESES' AND rc.edad <= 110)
            )
        '''.format(','.join(f"'{prov}'" for prov in provincias_arg)))

        conn.commit()

    print("\nTabla registros_limpios creada exitosamente.")
    print(f"Registros descartados por edad nula o fuera de rango: {total_descartados} de {total_original} ({(total_descartados / total_original) * 100:.2f}%)")
