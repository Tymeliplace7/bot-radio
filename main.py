import os
import sys
import subprocess
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot Radio Online 24/7"

# Ejecuta bot.py usando el mismo ejecutable de Python y pasando todas las variables de entorno
subprocess.Popen([sys.executable, 'bot.py'], env=os.environ.copy())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
