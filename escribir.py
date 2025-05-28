# escribir.py
import keyboard
import time

def escribir_texto(ruta_txt, delay, espera):
    print("Iniciando...")
    for i in range(int(espera), 0, -1):
        print(f"{i}...")
        time.sleep(1)

    with open(ruta_txt, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()

    time.sleep(0.5)
    i = 0
    while i < len(contenido):
        if contenido[i] == ' ':
            count = 1
            while i + count < len(contenido) and contenido[i + count] == ' ':
                count += 1
            if count >= 4:
                for _ in range(count // 4):
                    keyboard.press_and_release('tab')
                i += count
                continue
            else:
                keyboard.write(' ' * count)
                i += count
                continue
        elif contenido[i] == '\n':
            keyboard.press_and_release('enter')
        else:
            keyboard.write(contenido[i])
        i += 1
        time.sleep(float(delay))

    print("Terminado.")
