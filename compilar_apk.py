import subprocess
import sys

# Llama directamente al ejecutable de flet instalado en tu Python
subprocess.run([sys.executable, "-m", "flet.cli", "build", "apk"])