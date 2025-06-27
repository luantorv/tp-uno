import os
from os import system

def limpiar():
    if os.name == "nt":
        system("cls")
    else:
        system("clear")

def seguir():
    aux = True

    while True:
        if aux == True:
            opc = int(input("Elija una opción: \n 1. Volver al menú \n 2. Salir \n"))
        else:
            opc = int(input("Elija una opción válida: \n 1. Volver al menú \n 2. Salir \n"))
            aux = True

        match opc:
            case 1:
                return True
            case 2:
                return False
            case _:
                aux = False