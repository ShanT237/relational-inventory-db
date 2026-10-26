"""Pruebas. Se ejecutan desde la raíz del proyecto:
    python -m unittest discover -s tests -t . -v
Este archivo agrega src/ al path para poder importar los módulos de la aplicación."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
