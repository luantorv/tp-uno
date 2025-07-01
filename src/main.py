import tools as t
import answer as ans
from loader import cargar_csv_a_db
import cleanning as cl

# Cargar tabla con datos semi-crudos

t.limpiar()
cargar_csv_a_db("./file/Covid19Casos.csv")


# Se crea una nueva tabla con los datos limpios
cl.crear_registros_limpios()

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
    print("Opción 2: ")
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
        case "2":
            seg = t.seguir()
        case _:
            bol = True
            t.limpiar()