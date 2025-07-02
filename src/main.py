import tools as t
import answer as ans
from loader import cargar_csv_a_db
import cleanning as cl

# Cargar tabla con datos semi-crudos

t.limpiar()
cargar_csv_a_db("./file/Covid19Casos.csv")


# Se crea una nueva tabla con los datos limpios
cl.crear_registros_limpios()
ans.crear_intervalos_confirmados_y_fallecidos()


# MENÚ

bol = False
seg = True

while seg:
    if bol == False:
        print("\n================= Menú =================\n")
    else:
        print("Elija una opción válida: n")
        bol = False

    print("Opción 1a: Descripción de las variables")
    print("Opción 1b: Descripción de las variables ya limpios")
    print("Opción 3: Promedio de edad de los fallecidos por Provencia")
    print("Opción 4: Tabla Sturges - Intervalos de edad - Casos confirmados y fallecidos")
    print("Opción 0: Salir \n")

    op = input("¿Que desea ver? \n")

    match op:
        case "0":
            seg = False
        case "1a":
            t.limpiar()
            ans.describir_variables()
            seg = t.seguir()
        case "1b":
            t.limpiar()
            ans.describir_variables_limpias()
            seg = t.seguir()
        case "3":
            t.limpiar()
            ans.edad_promedio_fallecidos_por_provincia()
            seg = t.seguir()
        case "4":
            t.limpiar()
            ans.mostrar_tabla_intervalos("intervalos_confirmados")
            ans.mostrar_tabla_intervalos("intervalos_fallecidos")
            seg = t.seguir()
        case _:
            bol = True
            t.limpiar()