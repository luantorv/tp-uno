import csv
from db import crear_tabla_crudos, insertar_crudo, contar_registros
from tools import limpiar_str as limpiar

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