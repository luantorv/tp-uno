import os
from os import system

def limpiar():
    '''
    Limpia la consola dependiendo del sistema operativo en donde se esté ejecutando.
    '''

    if os.name == "nt":
        system("cls")
    else:
        system("clear")

def limpiar_str(valor):
    '''
    Limpia un valor de texto: quita espacios, lo convierte a mayúsculas y devuelve None si queda vacío.
    '''
    if valor is None:
        return None
    limpio = valor.strip().upper()
    return limpio if limpio else None


def seguir():
    '''
    Pregunta al usuario si quiere volver al menú o quiere salir del programa.
    Si quiere volver al menú devuelve True, si quiere salir devuelve False.
    '''


    aux = True

    while True:
        if aux == True:
            opc = int(input("\nElija una opción: \n 1. Volver al menú \n 2. Salir \n"))
        else:
            opc = int(input("\nElija una opción válida: \n 1. Volver al menú \n 2. Salir \n"))
            aux = True

        match opc:
            case 1:
                return True
            case 2:
                return False
            case _:
                aux = False