import subprocess
import time
import signal
import sys

def run_scraper():
    print("🚀 Ejecutando scraper...")
    result = subprocess.run(["docker", "exec", "scraper", "python", "scraper.py"], check=True)
    print("✅ Scraper completado exitosamente")
    return result

def run_filtrado_pig():
    print("\n🐷 Ejecutando script de filtrado en Pig...")
    result = subprocess.run(
        ["docker", "exec", "-w", "/app", "pig", "pig", "-x", "local", "Filtrado.pig"],
        check=True
    )
    print("✅ Filtrado con Pig completado")
    return result

def run_indexador():
    print("\n🔍 Ejecutando indexación en Elasticsearch...")
    result = subprocess.run(["python", "elastic/indexar.py"], check=True)
    print("✅ Indexación completada")
    return result

def run_cache_services():
    print("\n🔄 Iniciando servicios de caché...")
    
    # Iniciar el servidor de caché principal (cache.py)
    cache_process = subprocess.Popen(["python", "cache/cache.py"])
    time.sleep(3)  # Esperar a que el servidor principal inicie
    
    # Iniciar el worker de pre-caching (cache_worker.py)
    cache_worker_process = subprocess.Popen(
        ["docker", "exec", "cache-worker", "python", "cache_worker.py"]
    )
    time.sleep(2)  # Esperar a que el worker inicie
    
    print("✅ Servicios de caché en ejecución")
    return cache_process, cache_worker_process

def run_generador_trafico():
    print("\n🚦 Ejecutando generador de tráfico...")
    result = subprocess.run(["python", "generador_trafico/gdt.py"], check=True)
    print("✅ Generador de tráfico completado")
    return result

def cleanup_processes(processes):
    print("\n🧹 Limpiando procesos...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
        except Exception as e:
            print(f"⚠️ Error al terminar proceso: {str(e)}")
    print("✅ Procesos terminados correctamente")

def main():
    processes = []
    try:
        print("="*50)
        print("🚦 INICIANDO AUTOMATIZACIÓN DEL PIPELINE COMPLETO")
        print("="*50)

        # Paso 1: Extracción de datos
        run_scraper()
        time.sleep(2)

        # Paso 2: Procesamiento con Pig
        run_filtrado_pig()
        time.sleep(2)

        # Paso 3: Indexación en Elasticsearch
        run_indexador()
        time.sleep(5)  # Esperar más para que Elasticsearch esté listo

        # Paso 4: Servicios de caché
        cache_procs = run_cache_services()
        processes.extend(cache_procs)
        time.sleep(5)  # Esperar a que los servicios de caché estén listos

       

        print("\n" + "="*50)
        print("🎉 PIPELINE COMPLETADO EXITOSAMENTE")
        print("="*50)

        # Mantener los servicios en ejecución para pruebas
        if "--keep-alive" in sys.argv:
            print("\n🔌 Modo keep-alive activado. Presiona Ctrl+C para terminar.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR en el pipeline: {str(e)}")
        print(f"Comando fallido: {' '.join(e.cmd)}")
        print(f"Código de salida: {e.returncode}")
    except Exception as e:
        print(f"\n❌ ERROR inesperado: {str(e)}")
    finally:
        if "--keep-alive" not in sys.argv:
            cleanup_processes(processes)

if __name__ == "__main__":
    main()