import requests
from bs4 import BeautifulSoup
import re
import threading
import time

hea = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

base_url = "https://es.mtlnovel.com/start-a-core-pod/chapter-1-sequence/"

def descargar_y_procesar(base_url, archivo_actual, watchdog_event):
    global capitulos_guardados
    while True:
        page = requests.get(base_url, headers=hea)

        if page.status_code != 200:
            print(f'No se pudo obtener la página {base_url}. Reintentando...')
            time.sleep(60)  # Espera 60 segundos antes de volver a intentar
        else:
            print("\npage status ok\n")
            soup = BeautifulSoup(page.text, 'html.parser')

            #Obtiene la historia
            historia_element = soup.find('div', class_=f"par fontsize-16")

            try:
                #Obtencion del nombre y capitulo
                n_c = soup.find('div', class_='m-card single-page').h1.string

            except:
                n_c = "\nError en la obtencion de Numero y Nombre del capitulo\n  "

            if historia_element:
                historia = historia_element.get_text(separator="\n")

                # Guardar la historia en un archivo de texto
                pil = "_-"*20
                with open(f'Start_a_Core_Pod_{archivo_actual}.txt', 'a', encoding='utf-8') as arch_txt:
                    arch_txt.write(f"\n \n \n \n \n {n_c} \n {historia}\n\n\n\n\n{pil}")

                print("Saved...", capitulos_guardados,"\n\n","-_"*35,"\n")
                capitulos_guardados += 1

                # Si se han guardado 100 capítulos en un .txt, cambiar al siguiente .txt (archivo_actual forma parte del nombre del .txt
                if capitulos_guardados > 100:
                    archivo_actual += 100
                    capitulos_guardados = 0

            # Encontrar el enlace a la página siguiente
            base_url = soup.find('a', class_='next')["href"]
            print(base_url, "url ok")

            # Notificar al watchdog que la descarga y el procesamiento están completos
            watchdog_event.set()

# Función del watchdog para supervisar el tiempo de respuesta
def watchdog(watchdog_event, base_url):
    while True:
        # Espera a que se complete la descarga y el procesamiento
        watchdog_event.wait()

        # Reinicia el evento
        watchdog_event.clear()

        # Espera durante un tiempo límite (por ejemplo, 30 minutos)
        print("Esperando...")
        time.sleep(1800)  # 1800 segundos (30 minutos)

        # Si el evento no se activa nuevamente, reinicia la descarga y el procesamiento
        if not watchdog_event.is_set():
            print("Reiniciando la descarga y el procesamiento...")
            base_url = "https://es.mtlnovel.com/start-a-core-pod/chapter-1-sequence/"
            descargar_thread = threading.Thread(target=descargar_y_procesar, args=(base_url, archivo_actual, watchdog_event))
            descargar_thread.start()

if __name__ == "__main__":
    # Inicializar el contador de capítulos y archivo actual
    capitulos_guardados = 0
    archivo_actual = 700

    # Crear un evento para la comunicación entre el hilo del watchdog y el hilo de descarga
    watchdog_event = threading.Event()

    # Crear un hilo para la descarga y procesamiento inicial
    descargar_thread = threading.Thread(target=descargar_y_procesar, args=(base_url, archivo_actual, watchdog_event))
    descargar_thread.start()

    # Crear un hilo para el watchdog
    watchdog_thread = threading.Thread(target=watchdog, args=(watchdog_event, base_url))
    watchdog_thread.start()
