"""Script para levantar Streamlit."""
import subprocess
import sys
from src.config import settings

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "ui/app.py", "--server.port", str(settings.streamlit_port)])
