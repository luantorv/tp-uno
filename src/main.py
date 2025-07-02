import tools as t
import answer as ans
from loader import cargar_csv_a_db
import cleanning as cl

# Cargar tabla con datos semi-crudos

t.limpiar()
cargar_csv_a_db("./file/Covid19Casos.csv")


# Se crea una nueva tabla con los datos limpios
cl.crear_registros_limpios()


# Se crean tablas para las consignas
ans.crear_intervalos_confirmados_y_fallecidos()
ans.crear_intervalos_fallecidos_por_sexo()
ans.crear_casos_confirmados_por_sexo_y_provincia()
ans.crear_tabla_confirmados_vs_poblacion()
ans.crear_tabla_fallecidos_vs_poblacion()


# MENÚ

primera_vez = False
bol = False
seg = True

while seg:
    if primera_vez:
        t.limpiar()
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
            t.limpiar()
            ans.describir_variables()
            seg = t.seguir()
        case 2:
            t.limpiar()
            ans.describir_variables_limpias()
            seg = t.seguir()
        case 3:
            t.limpiar()
            ans.edad_promedio_fallecidos_por_provincia()
            seg = t.seguir()
        case 4:
            t.limpiar()
            ans.mostrar_tabla_intervalos("intervalos_confirmados")
            ans.mostrar_tabla_intervalos("intervalos_fallecidos")
            seg = t.seguir()
        case 5:
            t.limpiar()
            ans.mostrar_intervalos_fallecidos_por_sexo()
            seg = t.seguir()
        case 6:
            t.limpiar()
            ans.mostrar_casos_confirmados_por_sexo_y_provincia()
            seg = t.seguir()
        case 7:
            t.limpiar()
            ans.mostrar_menor_proporcion_confirmados()
            seg = t.seguir()
        case 8:
            t.limpiar()
            ans.mostrar_mayor_proporcion_fallecidos()
            seg = t.seguir()
        case 9:
            t.limpiar()
            ans.calcular_indice_confirmados_por_sexo()
            seg = t.seguir()
        case _:
            bol = True
            t.limpiar()