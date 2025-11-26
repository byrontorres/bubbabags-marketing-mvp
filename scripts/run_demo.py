"""Script para levantar la demo completa."""
import subprocess
import sys
import time
import threading

def run_api():
    subprocess.run([sys.executable, "scripts/run_api.py"])

def run_ui():
    time.sleep(3)
    subprocess.run([sys.executable, "scripts/run_ui.py"])

if __name__ == "__main__":
    print("=" * 50)
    print("INICIANDO DEMO BUBBABAGS")
    print("=" * 50)
    print("\nAPI:     http://localhost:8000")
    print("Swagger: http://localhost:8000/docs")
    print("UI:      http://localhost:8501")
    print("\nCtrl+C para detener.\n")
    
    api_thread = threading.Thread(target=run_api)
    ui_thread = threading.Thread(target=run_ui)
    
    api_thread.start()
    ui_thread.start()
    
    api_thread.join()
    ui_thread.join()
