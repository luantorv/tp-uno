import tools as t
import answer as ans

# Cargar tabla con datos semi-crudos

t.limpiar()
ans.cargar_csv_a_db("./file/Covid19Casos.csv")


# MENÚ

bol = False
seg = True

while seg:
    if bol == False:
        print("\n================= Menú =================\n")
    else:
        print("Elija una opción válida: n")
        bol = False

    print("Opción 1: Descripción de las variables")
    print("Opción 2: ")
    print("Opción 3: Salir \n")

    op = int(input("¿Que desea ver? \n"))

    match op:
        case 1:
            t.limpiar()
            ans.describir_variables()
            seg = t.seguir()
        case 2:
            seg = t.seguir()
        case 3:
            seg = False
        case _:
            bol = True
            t.limpiar()