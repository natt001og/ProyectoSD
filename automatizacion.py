import subprocess
import time

def run_scraper():
    print("Ejecutando scraper...")
    result = subprocess.run(["docker", "exec", "scraper", "python", "scraper.py"])
    if result.returncode != 0:
        raise Exception("Error al ejecutar scraper")

def run_filtrado_pig():
    print("Ejecutando script de filtrado en Pig...")
    result = subprocess.run(["docker", "exec", "-w", "/app", "pig", "pig", "-x", "local", "Filtrado.pig"])
    if result.returncode != 0:
        raise Exception("Error al ejecutar filtrado con Apache Pig")

def run_indexador():
    print("Ejecutando indexación en Elasticsearch...")
    result = subprocess.run(["py", "elastic/indexar.py"])
    if result.returncode != 0:
        raise Exception("Error al indexar los datos")

def run_cache():
    print("Ejecutando servidor de cache...")
    result = subprocess.Popen(["py", "cache/cache.py"])  # Usamos Popen para que quede corriendo
    time.sleep(5)  # Esperar un poco para que el cache levante
    return result

def run_generador_trafico():
    print("Ejecutando generador de tráfico...")
    result = subprocess.run(["py", "generador_trafico/gdt.py"])
    if result.returncode != 0:
        raise Exception("Error al ejecutar el generador de tráfico")

def main():
    try:
        print("Iniciando automatización del pipeline...")

        run_scraper()
        time.sleep(2)

        run_filtrado_pig()
        time.sleep(2)

        run_indexador()
        time.sleep(2)

        cache_process = run_cache()
        # Ya que cache está corriendo, ejecutamos generador de tráfico
        run_generador_trafico()

        # Cuando termine todo, terminamos el servidor cache
        cache_process.terminate()

        print("Pipeline completo y automatizado.")

    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    main()
