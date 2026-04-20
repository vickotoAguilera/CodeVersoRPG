import os
import subprocess
import sys

# Lanzador para abrir el gestor NUEVO de interfaz NPC con canvas.
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

script = os.path.join(ROOT, "gestor_interfaz_npc_v1.py")
raise SystemExit(subprocess.call([sys.executable, script]))
