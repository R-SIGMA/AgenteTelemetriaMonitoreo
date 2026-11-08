"""
main.py - Punto de entrada del proyecto (el Controlador arranca todo).

Uso:
    python src/main.py          # abre la ventana del monitor
    python src/main.py demo     # demo controlada en consola (8 casos)

Requiere: pip install psutil
"""

import sys
import tkinter as tk

from app import AppMonitor
from demo import demo_controlada


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_controlada()
        return

    # Aquí entra el login (Axl): usuario = pedir_login(); si es None, salir.
    usuario = "sin sesión"

    ventana = tk.Tk()
    AppMonitor(ventana, usuario)
    ventana.mainloop()


if __name__ == "__main__":
    main()
